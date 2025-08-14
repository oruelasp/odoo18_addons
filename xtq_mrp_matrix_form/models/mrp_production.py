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

    matrix_state = fields.Selection([
        ('pending', 'Pendiente'),
        ('planned', 'Programada'),
        ('progress', 'Ejecutado'),
        ('done', 'Realizado')
    ], string='Estado de Matriz', default='pending', copy=False, tracking=True,
    help="Estado del proceso de planificación y producción de la matriz.")

    matrix_curve_ids = fields.One2many(
        'mrp.production.curve.line',
        'production_id',
        string='Curva de Tallas',
        copy=True,
        help="Define la proporción de cada talla en la curva de producción."
    )

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
                'product_qty': item.get('product_qty'), # Usar product_qty
                'qty_producing': item.get('qty_producing', 0.0), # Añadir qty_producing
            }))
        
        self.with_context(tracking_disable=True).write({'matrix_line_ids': commands})
  

    @api.constrains('product_qty', 'total_matrix_quantity')
    def _check_quantity_match(self):
        for mo in self:
            # La validación ahora debe ser sobre product_qty de la matriz (product_qty) vs product_qty de la MO
            if mo.matrix_line_ids and not float_is_zero(mo.product_qty - sum(line.product_qty for line in mo.matrix_line_ids), precision_rounding=mo.product_uom_id.rounding):
                raise ValidationError(f"Conflicto de Cantidades: La cantidad a producir de la OP ({mo.product_qty}) no coincide con el total de la matriz planificada ({sum(line.product_qty for line in mo.matrix_line_ids)}).")

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
        # Limpiar campos de matriz si cambia el producto
        self.matrix_attribute_row_id = False
        self.matrix_values_row_ids = False
        self.matrix_attribute_col_id = False
        self.matrix_values_col_ids = False
        self.matrix_curve_ids = [(5,0,0)] # Limpiar la curva también

        if self.product_id:
            # Obtener atributos configurados en la plantilla del producto
            product_tmpl = self.product_id.product_tmpl_id
            matrix_x_attr = product_tmpl.matrix_attribute_x_id
            matrix_y_attr = product_tmpl.matrix_attribute_y_id

            if matrix_x_attr:
                self.matrix_attribute_col_id = matrix_x_attr.id
            if matrix_y_attr:
                self.matrix_attribute_row_id = matrix_y_attr.id

            attribute_ids = self.product_id.attribute_line_ids.attribute_id.ids
            domain = [('id', 'in', attribute_ids)]
            return {'domain': {'matrix_attribute_row_id': domain, 'matrix_attribute_col_id': domain}}
        else:
            domain = [('id', 'in', [])]
            return {'domain': {'matrix_attribute_row_id': domain, 'matrix_attribute_col_id': domain}}

    @api.onchange('matrix_attribute_row_id')
    def _onchange_attribute_row_set_values_domain(self):
        self.matrix_values_row_ids = False
        self.matrix_curve_ids = [(5,0,0)] # Limpiar curva al cambiar atributo de fila
        if not self.matrix_attribute_row_id or not self.product_id: return {'domain': {'matrix_values_row_ids': [('id', 'in', [])]}}

        attribute_line = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('attribute_id', '=', self.matrix_attribute_row_id.id)
        ], limit=1)

        if attribute_line:
            domain = [('id', 'in', attribute_line.value_ids.ids)]
            # Pre-poblar la curva de tallas con los valores de la fila
            commands = []
            for val in attribute_line.value_ids:
                commands.append((0, 0, {
                    'attribute_value_id': val.id,
                    'proportion': 1, # Default a 1 o 0, se recalculará
                }))
            self.matrix_curve_ids = commands
        else:
            domain = [('id', 'in', [])]
        return {'domain': {'matrix_values_row_ids': domain}}

    @api.onchange('matrix_attribute_col_id')
    def _onchange_attribute_col_set_values_domain(self):
        self.matrix_values_col_ids = False
        if not self.matrix_attribute_col_id or not self.product_id: return {'domain': {'matrix_values_col_ids': [('id', 'in', [])]}}

        attribute_line = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('attribute_id', '=', self.matrix_attribute_col_id.id)
        ], limit=1)

        if attribute_line:
            domain = [('id', 'in', attribute_line.value_ids.ids)]
        else:
            domain = [('id', 'in', [])]
        return {'domain': {'matrix_values_col_ids': domain}}

    def get_matrix_data(self):
        self.ensure_one()
        if not all([self.matrix_attribute_col_id, self.matrix_values_col_ids,
                    self.matrix_attribute_row_id, self.matrix_values_row_ids]):
            return {'error': 'Configure Fila y Columna con sus respectivos Valores.'}

        quantities = {f"{line.row_value_id.id}-{line.col_value_id.id}": {
            'product_qty': line.product_qty,
            'qty_producing': line.qty_producing,
        } for line in self.matrix_line_ids}

        curve_proportions = {curve.attribute_value_id.id: curve.proportion for curve in self.matrix_curve_ids}

        return {
            'axis_y': {
                'name': self.matrix_attribute_row_id.name,
                'values': [{'id': v.id, 'name': v.name, 'proportion': curve_proportions.get(v.id, 0)} for v in self.matrix_values_row_ids]
            },
            'axis_x': {
                'name': self.matrix_attribute_col_id.name,
                'values': [{'id': v.id, 'name': v.name} for v in self.matrix_values_col_ids]
            },
            'quantities': quantities,
            'matrix_state': self.matrix_state, # Pasar el estado al frontend
        }

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

    # Métodos de los botones

    def action_recalculate_matrix(self):
        self.ensure_one()
        if self.matrix_state != 'pending':
            raise UserError("La matriz solo se puede recalcular en estado 'Pendiente'.")

        if not self.product_id or not self.matrix_attribute_row_id or not self.matrix_values_row_ids or not self.matrix_attribute_col_id or not self.matrix_values_col_ids or not self.matrix_curve_ids:
            raise UserError("Por favor, configure todos los atributos de la matriz y la curva de tallas.")

        total_qty_mo = self.product_qty
        if float_is_zero(total_qty_mo, precision_rounding=self.product_uom_id.rounding):
            raise UserError("La cantidad a producir de la OP es cero. Ingrese una cantidad válida.")

        total_proportion = sum(curve.proportion for curve in self.matrix_curve_ids)
        if total_proportion == 0:
            raise UserError("La suma de las proporciones de la curva de tallas es cero. Ajuste la configuración de la curva.")

        new_matrix_lines_commands = [(5, 0, 0)] # Borrar y recrear

        for row_val in self.matrix_values_row_ids:
            row_proportion = next((curve.proportion for curve in self.matrix_curve_ids if curve.attribute_value_id == row_val), 0)
            if total_proportion > 0:
                row_qty = (total_qty_mo * row_proportion) / total_proportion
            else:
                row_qty = 0 # Fallback si total_proportion es 0, aunque ya se validó antes

            # Distribuir la cantidad de la fila entre las columnas del eje X
            num_cols = len(self.matrix_values_col_ids)
            qty_per_cell = row_qty / num_cols if num_cols > 0 else 0

            for col_val in self.matrix_values_col_ids:
                existing_line = self.matrix_line_ids.filtered(
                    lambda l: l.row_value_id == row_val and l.col_value_id == col_val
                )
                if existing_line:
                    new_matrix_lines_commands.append((1, existing_line.id, {
                        'product_qty': qty_per_cell,
                        'qty_producing': 0, # Reset qty_producing on recalculate
                    }))
                else:
                    new_matrix_lines_commands.append((0, 0, {
                        'row_value_id': row_val.id,
                        'col_value_id': col_val.id,
                        'product_qty': qty_per_cell,
                        'qty_producing': 0,
                    }))
        self.write({'matrix_line_ids': new_matrix_lines_commands})

    def action_confirm_planning(self):
        self.ensure_one()
        if self.matrix_state != 'pending':
            raise UserError("La planificación ya ha sido confirmada o se encuentra en otro estado.")
        if not self.matrix_line_ids or all(float_is_zero(line.product_qty, precision_rounding=self.product_uom_id.rounding) for line in self.matrix_line_ids):
            raise UserError("No hay cantidades planificadas en la matriz para confirmar.")

        self.write({'matrix_state': 'planned'})

    def action_produce_lots(self):
        self.ensure_one()
        if self.matrix_state not in ['planned', 'progress']:
            raise UserError("La matriz debe estar en estado 'Programada' o 'Ejecutado' para producir lotes.")

        if not self.matrix_line_ids or all(float_is_zero(line.qty_producing, precision_rounding=self.product_uom_id.rounding) for line in self.matrix_line_ids):
            raise UserError("No hay cantidades a producir en la matriz.")

        # Obtener los movimientos de producto terminado
        finished_move = self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id)

        if not finished_move:
            raise UserError("No se encontró el movimiento de producto terminado para esta Orden de Producción.")

        # Limpiar las líneas de movimiento existentes si es necesario para recrearlas con los lotes
        finished_move.move_line_ids.unlink()

        total_produced_from_matrix = 0
        produced_lots = self.env['stock.lot']
        for line in self.matrix_line_ids.filtered(lambda l: l.qty_producing > 0):
            total_produced_from_matrix += line.qty_producing

            # Generar nombre del lote
            lot_name = f"{self.product_id.default_code or self.product_id.name}-{line.row_value_id.name}-{line.col_value_id.name}-{self.name}"

            # Crear stock.lot
            lot = self.env['stock.lot'].create({
                'name': lot_name,
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
            })
            produced_lots += lot

            # Asignar atributos de Tono y Talla usando xtq_lot_attributes
            self.env['stock.lot.attribute.line'].create({
                'lot_id': lot.id,
                'attribute_id': line.row_value_id.attribute_id.id,
                'attribute_value_id': line.row_value_id.id,
            })
            self.env['stock.lot.attribute.line'].create({
                'lot_id': lot.id,
                'attribute_id': line.col_value_id.attribute_id.id,
                'attribute_value_id': line.col_value_id.id,
            })

            # Crear stock.move.line para este lote
            self.env['stock.move.line'].create({
                'move_id': finished_move.id,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_uom_id.id,
                'qty_done': line.qty_producing,
                'lot_id': lot.id,
                'location_id': finished_move.location_id.id,
                'location_dest_id': finished_move.location_dest_id.id,
                'company_id': self.company_id.id,
            })
            # Resetear la cantidad a producir para esta celda después de la explosión
            line.qty_producing = 0

        # Validar y marcar como hecho la MO, gestionando parciales
        if total_produced_from_matrix > 0:
            self.product_qty = total_produced_from_matrix
            self.move_finished_ids.quantity_done = total_produced_from_matrix

            res = self.button_mark_done()
            if self.state == 'done':
                self.matrix_state = 'done'
            else:
                self.matrix_state = 'progress'

            if res and isinstance(res, dict) and res.get('type') == 'ir.actions.act_window':
                return res
            else:
                new_mo_domain = [('origin', '=', self.name)]
                return {
                    'name': 'Órdenes de Producción Parciales',
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.production',
                    'view_mode': 'tree,form',
                    'domain': new_mo_domain,
                    'target': 'current',
                }
        else:
            raise UserError("No se produjo ninguna cantidad en la matriz. Asegúrese de ingresar cantidades a producir.")
