from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
import json
import math

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
    matrix_qty_mismatch = fields.Boolean(
        string="Desfase de Cantidad en Matriz",
        compute="_compute_matrix_qty_mismatch",
        help="Se activa si la cantidad total de la matriz no coincide con la cantidad a producir."
    )

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

    @api.depends('matrix_line_ids.product_qty')
    def _compute_total_matrix_quantity(self):
        for mo in self: mo.total_matrix_quantity = sum(line.product_qty for line in mo.matrix_line_ids)

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
  
    # @api.constrains('product_qty', 'total_matrix_quantity')
    #def _check_quantity_match(self):
        # for mo in self:
            # La validación ahora debe ser sobre product_qty de la matriz (product_qty) vs product_qty de la MO
            #if mo.matrix_line_ids and not float_is_zero(mo.product_qty - sum(line.product_qty for line in mo.matrix_line_ids), precision_rounding=mo.product_uom_id.rounding):
                #raise ValidationError(f"Conflicto de Cantidades: La cantidad a producir de la OP ({mo.product_qty}) no coincide con el total de la matriz planificada ({sum(line.product_qty for line in mo.matrix_line_ids)}).")

    # *** CORRECCIÓN DEFINITIVA EN LA LÓGICA DE FINALIZACIÓN ***
    def _get_moves_finished_values(self):
        if not self.matrix_line_ids:
            return super()._get_moves_finished_values()

        moves_values = []
        template = self.product_id.product_tmpl_id # Obtenemos la plantilla una sola vez

        for line in self.matrix_line_ids.filtered(lambda l: l.product_qty > 0):
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
                'product_uom_qty': line.product_qty, 'product_uom': variant_product.uom_id.id,
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
        # Ya no pre-poblamos la curva al cambiar el atributo de FILA; la curva corresponde al eje COLUMNA
        if not self.matrix_attribute_row_id or not self.product_id:
            return {'domain': {'matrix_values_row_ids': [('id', 'in', [])]}}

        attribute_line = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('attribute_id', '=', self.matrix_attribute_row_id.id)
        ], limit=1)

        if attribute_line:
            domain = [('id', 'in', attribute_line.value_ids.ids)]
        else:
            domain = [('id', 'in', [])]
        return {'domain': {'matrix_values_row_ids': domain}}

    @api.onchange('matrix_attribute_col_id')
    def _onchange_attribute_col_set_values_domain(self):
        self.matrix_values_col_ids = False
        # Al cambiar el atributo de COLUMNA, la curva de tallas debe reinicializarse con sus valores
        self.matrix_curve_ids = [(5, 0, 0)]
        if not self.matrix_attribute_col_id or not self.product_id:
            return {'domain': {'matrix_values_col_ids': [('id', 'in', [])]}}

        attribute_line = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('attribute_id', '=', self.matrix_attribute_col_id.id)
        ], limit=1)

        if attribute_line:
            domain = [('id', 'in', attribute_line.value_ids.ids)]
            # Pre-poblar curva con valores del eje COLUMNA (tallas)
            commands = []
            for val in attribute_line.value_ids:
                commands.append((0, 0, {
                    'attribute_value_id': val.id,
                    'proportion': 1,
                }))
            self.matrix_curve_ids = commands
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
                'values': [{'id': v.id, 'name': v.name} for v in self.matrix_values_row_ids]
            },
            'axis_x': {
                'name': self.matrix_attribute_col_id.name,
                'values': [{'id': v.id, 'name': v.name, 'proportion': curve_proportions.get(v.id, 0)} for v in self.matrix_values_col_ids]
            },
            'quantities': quantities,
            'matrix_state': self.matrix_state,
        }

    def action_recalculate_matrix(self):
        self.ensure_one()
        if self.matrix_state != 'pending':
            raise UserError("La matriz solo se puede recalcular en estado 'Pendiente'.")

        # --- INICIO DE LA CORRECCIÓN ---
        # Paso 1: Forzar la sincronización de la Curva de Tallas con los Valores de Columna seleccionados.
        # Esto elimina la dependencia del onchange y previene errores de estado.
        existing_proportions = {c.attribute_value_id.id: c.proportion for c in self.matrix_curve_ids}
        new_curve_lines = []
        for value in self.matrix_values_col_ids:
            new_curve_lines.append((0, 0, {
                'attribute_value_id': value.id,
                'proportion': existing_proportions.get(value.id, 1)
            }))
        
        # Reemplazar la curva en memoria para usarla en el cálculo. Se guardará junto con las líneas de la matriz.
        self.matrix_curve_ids = [(5, 0, 0)] + new_curve_lines
        # --- FIN DE LA CORRECCIÓN ---

        if not self.product_id or not self.matrix_attribute_row_id or not self.matrix_values_row_ids or not self.matrix_attribute_col_id or not self.matrix_values_col_ids:
            raise UserError("Por favor, configure todos los atributos de la matriz.")

        total_qty_mo = self.product_qty
        if float_is_zero(total_qty_mo, precision_rounding=self.product_uom_id.rounding):
            raise UserError("La cantidad a producir de la OP es cero. Ingrese una cantidad válida.")

        num_rows = len(self.matrix_values_row_ids)
        if num_rows <= 0:
            raise UserError("No hay valores configurados para el eje Fila.")

        curve_map = {c.attribute_value_id.id: c.proportion for c in self.matrix_curve_ids}
        selected_col_ids = self.matrix_values_col_ids.ids
        total_proportion = sum(prop for val_id, prop in curve_map.items() if val_id in selected_col_ids)

        if total_proportion == 0:
            raise UserError("La suma de las proporciones para las columnas seleccionadas es cero. Ajuste la configuración de la curva.")

        matrix_values = {}
        # ... (lógica de redondeo) ...
        for row_val in self.matrix_values_row_ids:
            per_row_qty = total_qty_mo / num_rows
            for col_val in self.matrix_values_col_ids:
                col_prop = curve_map.get(col_val.id, 0)
                ideal_val = per_row_qty * (col_prop / total_proportion)
                rounded_val = math.ceil(ideal_val)
                matrix_values[(row_val.id, col_val.id)] = {
                    'ideal': ideal_val,
                    'rounded': rounded_val,
                    'final': rounded_val
                }
        
        total_rounded = sum(v['rounded'] for v in matrix_values.values())
        excess = total_rounded - total_qty_mo
        
        if excess > 0:
            sorted_cells = sorted(matrix_values.items(), key=lambda item: (item[1]['rounded'] - item[1]['ideal']), reverse=True)
            for i in range(int(excess)):
                cell_key = sorted_cells[i % len(sorted_cells)][0]
                matrix_values[cell_key]['final'] -= 1

        new_matrix_lines_commands = []
        for row_val in self.matrix_values_row_ids:
            for col_val in self.matrix_values_col_ids:
                final_qty = matrix_values.get((row_val.id, col_val.id), {}).get('final', 0)
                new_matrix_lines_commands.append((0, 0, {
                    'row_value_id': row_val.id,
                    'col_value_id': col_val.id,
                    'product_qty': final_qty,
                    'qty_producing': 0,
                }))
        
        # Borrar líneas viejas y escribir las nuevas
        self.matrix_line_ids = [(5, 0, 0)]
        self.write({'matrix_line_ids': new_matrix_lines_commands})

    def action_confirm_planning(self):
        self.ensure_one()
        if self.matrix_state != 'pending':
            raise UserError("La planificación ya ha sido confirmada o se encuentra en otro estado.")
        if not self.matrix_line_ids or all(float_is_zero(line.product_qty, precision_rounding=self.product_uom_id.rounding) for line in self.matrix_line_ids):
            raise UserError("No hay cantidades planificadas en la matriz para confirmar.")

        if self.matrix_qty_mismatch:
            raise UserError(_(
                "La cantidad total de la matriz (%s) es diferente de la cantidad a producir de la orden (%s). "
                "Por favor, regularice las cantidades antes de confirmar la planificación.",
                self.total_matrix_quantity, self.product_qty
            ))
        self.write({'matrix_state': 'planned'})
        return True

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

    @api.depends("total_matrix_quantity", "product_qty")
    def _compute_matrix_qty_mismatch(self):
        """
        Compara el total de la matriz con la cantidad a producir de la OP.
        Usa float_compare para manejar imprecisiones con decimales.
        """
        for production in self:
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_comparison = float_compare(production.total_matrix_quantity, production.product_qty, precision_digits=precision_digits)
            production.matrix_qty_mismatch = qty_comparison != 0
