from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
import json

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # ... (Los campos de configuración y el JSON se mantienen igual) ...
    matrix_attribute_row_id = fields.Many2one('product.attribute', string='Atributo Fila')
    matrix_values_row_ids = fields.Many2many('product.attribute.value', 'mrp_production_matrix_row_rel', string='Valores (Fila)', domain="[('attribute_id', '=', matrix_attribute_row_id)]")
    matrix_attribute_col_id = fields.Many2one('product.attribute', string='Atributo Columna')
    matrix_values_col_ids = fields.Many2many('product.attribute.value', 'mrp_production_matrix_col_rel', string='Valores (Columna)', domain="[('attribute_id', '=', matrix_attribute_col_id)]")
    matrix_line_ids = fields.One2many('mrp.production.matrix.line', 'production_id', string='Desglose Matriz')
    matrix_data_json = fields.Text(string="Matrix Data JSON", copy=False)
    total_matrix_quantity = fields.Float(string="Cantidad Total en Matriz", compute='_compute_total_matrix_quantity', store=True)

    @api.depends('matrix_line_ids.quantity')
    def _compute_total_matrix_quantity(self):
        for mo in self: mo.total_matrix_quantity = sum(line.quantity for line in mo.matrix_line_ids)

    # --- La lógica de sincronización JSON se mantiene ---
    @api.model_create_multi
    def create(self, vals_list):
        productions = super().create(vals_list)
        for production, vals in zip(productions, vals_list):
            if vals.get('matrix_data_json'):
                production._sync_matrix_lines_from_json(vals.get('matrix_data_json'))
        return productions

    def write(self, vals):
        res = super().write(vals)
        if 'matrix_data_json' in vals:
            for production in self:
                production._sync_matrix_lines_from_json(vals.get('matrix_data_json'))
        return res

    def _sync_matrix_lines_from_json(self, json_data):
        self.ensure_one()
        try:
            data = json.loads(json_data or '[]')
        except (json.JSONDecodeError, TypeError):
            data = []
        commands = [(5, 0, 0)] 
        for item in data:
            commands.append((0, 0, {
                'row_value_id': item.get('yValueId'),
                'col_value_id': item.get('xValueId'),
                'quantity': item.get('quantity'),
            }))
        
        self.with_context(tracking_disable=True).write({'matrix_line_ids': commands})
  



    @api.constrains('product_qty', 'total_matrix_quantity')
    def _check_quantity_match(self):
        for mo in self:
            if mo.matrix_line_ids and not float_is_zero(mo.product_qty - mo.total_matrix_quantity, precision_rounding=mo.product_uom_id.rounding):
                raise ValidationError(f"Conflicto de Cantidades: La cantidad a producir ({mo.product_qty}) no coincide con el total de la matriz ({mo.total_matrix_quantity}).")

    # *** CORRECCIÓN DEFINITIVA EN LA LÓGICA DE FINALIZACIÓN ***
    def _get_moves_finished_values(self):
        if not self.matrix_line_ids:
            return super()._get_moves_finished_values()

        moves_values = []
        template = self.product_id.product_tmpl_id # Obtenemos la plantilla una sola vez

        for line in self.matrix_line_ids.filtered(lambda l: l.quantity > 0):
            # 1. BÚSQUEDA EN TIEMPO REAL: Buscamos la variante aquí y ahora.
            variant_product = self.env['product.product'].search([
                ('product_tmpl_id', '=', template.id),
                ('product_template_attribute_value_ids', '=', line.row_value_id.id),
                ('product_template_attribute_value_ids', '=', line.col_value_id.id)
            ], limit=1)

            # 2. VALIDACIÓN: Comprobamos si la búsqueda tuvo éxito.
            if not variant_product:
                raise UserError(f"No se encontró una variante de producto para la combinación: {line.row_value_id.name} / {line.col_value_id.name}. Por favor, asegúrese de que esta variante exista en la configuración del producto.")

            # 3. CREACIÓN DEL MOVIMIENTO: Usamos el 'variant_product' que acabamos de encontrar.
            move_vals = {
                'name': self.name, 'origin': self.name, 'product_id': variant_product.id,
                'product_uom_qty': line.quantity, 'product_uom': variant_product.uom_id.id,
                'location_id': self.product_id.with_company(self.company_id).property_stock_production.id,
                'location_dest_id': self.location_dest_id.id, 'production_id': self.id,
                'company_id': self.company_id.id, 'group_id': self.procurement_group_id.id
            }
            moves_values.append(move_vals)

        if not moves_values and self.product_qty > 0:
            raise UserError("La matriz no tiene cantidades para producir.")
        
        return moves_values

    # ... (El resto de los onchange y get_matrix_data se mantienen igual) ...
    @api.onchange('product_id')
    def _onchange_product_id_set_attribute_domain(self):
        self.matrix_attribute_row_id = False; self.matrix_values_row_ids = False; self.matrix_attribute_col_id = False; self.matrix_values_col_ids = False
        if self.product_id:
            attribute_ids = self.product_id.attribute_line_ids.attribute_id.ids
            domain = [('id', 'in', attribute_ids)]
            return {'domain': {'matrix_attribute_row_id': domain, 'matrix_attribute_col_id': domain}}
        else:
            domain = [('id', 'in', [])]
            return {'domain': {'matrix_attribute_row_id': domain, 'matrix_attribute_col_id': domain}}

    @api.onchange('matrix_attribute_row_id')
    def _onchange_attribute_row_set_values_domain(self):
        self.matrix_values_row_ids = False
        if not self.matrix_attribute_row_id or not self.product_id: return {'domain': {'matrix_values_row_ids': [('id', 'in', [])]}}
        attribute_line = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),('attribute_id', '=', self.matrix_attribute_row_id.id)], limit=1)
        if attribute_line: domain = [('id', 'in', attribute_line.value_ids.ids)]
        else: domain = [('id', 'in', [])]
        return {'domain': {'matrix_values_row_ids': domain}}

    @api.onchange('matrix_attribute_col_id')
    def _onchange_attribute_col_set_values_domain(self):
        self.matrix_values_col_ids = False
        if not self.matrix_attribute_col_id or not self.product_id: return {'domain': {'matrix_values_col_ids': [('id', 'in', [])]}}
        attribute_line = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),('attribute_id', '=', self.matrix_attribute_col_id.id)], limit=1)
        if attribute_line: domain = [('id', 'in', attribute_line.value_ids.ids)]
        else: domain = [('id', 'in', [])]
        return {'domain': {'matrix_values_col_ids': domain}}

    def get_matrix_data(self):
        self.ensure_one()
        if not all([self.matrix_attribute_col_id, self.matrix_values_col_ids, self.matrix_attribute_row_id, self.matrix_values_row_ids]): return {'error': 'Configure Fila y Columna con sus respectivos Valores.'}
        quantities = {f"{line.row_value_id.id}-{line.col_value_id.id}": line.quantity for line in self.matrix_line_ids}
        return {'axis_y': {'name': self.matrix_attribute_row_id.name, 'values': [{'id': v.id, 'name': v.name} for v in self.matrix_values_row_ids]}, 'axis_x': {'name': self.matrix_attribute_col_id.name, 'values': [{'id': v.id, 'name': v.name} for v in self.matrix_values_col_ids]}, 'quantities': quantities}

    def _create_lots_for_finished_move(self):
        # Esta es la definición del método que faltaba.
        self.ensure_one()
        finished_move = self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id and m.state == 'done')
        if not finished_move: 
            return

        # Limpiamos las líneas de movimiento autogeneradas para reemplazarlas con nuestro desglose.
        finished_move.move_line_ids.unlink()

        for line in self.matrix_line_ids.filtered(lambda l: l.quantity > 0):
            # Aquí se construye el nombre del lote
            lot_name = f"{self.product_id.default_code or self.product_id.name}-{line.row_value_id.name}-{line.col_value_id.name}-{self.name}"
            
            # Aquí se crea el registro del lote
            lot = self.env['stock.lot'].create({
                'name': lot_name, 
                'product_id': self.product_id.id, 
                'company_id': self.company_id.id
            })
            
            # Y aquí se asigna ese lote a un movimiento de inventario
            self.env['stock.move.line'].create({
                'move_id': finished_move.id, 
                'lot_id': lot.id, 
                'quantity': line.quantity,
                'product_id': self.product_id.id, 
                'product_uom_id': self.product_uom_id.id,
                'location_id': finished_move.location_id.id, 
                'location_dest_id': finished_move.location_dest_id.id,
                'company_id': self.company_id.id
            })
