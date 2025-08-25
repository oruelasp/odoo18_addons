from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, float_round
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
    # def _get_moves_finished_values(self):
        #if not self.matrix_line_ids:
            #return super()._get_moves_finished_values()

        #moves_values = []
        #template = self.product_id.product_tmpl_id # Obtenemos la plantilla una sola vez

        #for line in self.matrix_line_ids.filtered(lambda l: l.product_qty > 0):
            # 1. BÚSQUEDA EN TIEMPO REAL: Buscamos la variante aquí y ahora.
            #variant_product = self.env['product.product'].search([
                #('product_tmpl_id', '=', template.id),
                #('product_template_attribute_value_ids', '=', line.row_value_id.id),
                #('product_template_attribute_value_ids', '=', line.col_value_id.id)
            #], limit=1)

            # 2. VALIDACIÓN: Comprobamos si la búsqueda tuvo éxito.
            #if not variant_product:
                #raise UserError(f"No se encontró una variante de producto para la combinación: {line.row_value_id.name} / {line.col_value_id.name}. Por favor, asegúrese de que esta variante exista en la configuración del producto.")

            # 3. CREACIÓN DEL MOVIMIENTO: Usamos el 'variant_product' que acabamos de encontrar.
            #move_vals = {
                #'name': self.name, 'origin': self.name, 'product_id': variant_product.id,
                #'product_uom_qty': line.product_qty, 'product_uom': variant_product.uom_id.id,
                #'location_id': self.product_id.with_company(self.company_id).property_stock_production.id,
                #'location_dest_id': self.location_dest_id.id, 'production_id': self.id,
                #'company_id': self.company_id.id, 'group_id': self.procurement_group_id.id
            #}
            #moves_values.append(move_vals)

        #if not moves_values and self.product_qty > 0:
            #raise UserError("La matriz no tiene cantidades para producir.")
        
        #return moves_values

    # ... (El resto de los onchange y get_matrix_data se mantienen igual) ...
    @api.onchange('product_id', 'bom_id')
    def _onchange_product_id_set_attribute_domain(self):
        """
        Al cambiar el producto o la LdM, hereda los atributos de la matriz.
        Prioridad: LdM > Plantilla de Producto.
        AC4 de HU-MRP-004.
        """
        if self.bom_id and self.bom_id.matrix_attribute_row_id and self.bom_id.matrix_attribute_col_id:
            # Heredar desde la LdM (HU-MRP-004)
            self.matrix_attribute_row_id = self.bom_id.matrix_attribute_row_id.id
            self.matrix_attribute_col_id = self.bom_id.matrix_attribute_col_id.id
        elif self.product_id:
            # Mantener el comportamiento anterior como fallback
            self.matrix_attribute_row_id = self.product_id.product_tmpl_id.matrix_attribute_x_id.id
            self.matrix_attribute_col_id = self.product_id.product_tmpl_id.matrix_attribute_y_id.id
        else:
            self.matrix_attribute_row_id = False
            self.matrix_attribute_col_id = False


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

    def button_plan(self):
        """
        Heredamos el botón 'Planificar' estándar de Odoo para integrar la confirmación
        de la planificación de la matriz. Validamos que las cantidades coincidan antes
        de proceder con la planificación estándar.
        """
        # Si la OP no usa la matriz, ejecutar la lógica estándar directamente.
        if not self.matrix_attribute_row_id or not self.matrix_attribute_col_id:
            return super(MrpProduction, self).button_plan()

        self.ensure_one()
        if self.matrix_qty_mismatch:
            raise UserError(_(
                "La cantidad total de la matriz (%s) es diferente de la cantidad a producir de la orden (%s). "
                "Por favor, regularice las cantidades antes de confirmar la planificación.",
                self.total_matrix_quantity, self.product_qty
            ))
        self.write({'matrix_state': 'planned'})
        return super(MrpProduction, self).button_plan()

    def action_generate_serial(self):
        # Si la llamada viene de nuestro flujo automatizado, permitimos que el sistema
        # genere lotes para las OPs residuales si es necesario.
        if self.env.context.get('from_matrix_flow'):
            return super(MrpProduction, self).action_generate_serial()
        
        # Si no, mantenemos nuestro control para evitar la generación manual por parte del usuario.
        if self.matrix_attribute_row_id and self.matrix_attribute_col_id:
            raise UserError(_(
                "No se puede generar un número de lote manualmente para esta orden de producción. "
                "Los lotes se crearán automáticamente desde la matriz al finalizar el proceso."
            ))
        return super(MrpProduction, self).action_generate_serial()

    def button_unplan(self):
        """
        Heredamos el botón 'Anular planeación' para revertir el estado de la matriz.
        Solo se permite si el estado de la matriz es 'Planificado'.
        """
        # Si la OP no usa la matriz, ejecutar la lógica estándar directamente.
        if not self.matrix_attribute_row_id or not self.matrix_attribute_col_id:
            return super(MrpProduction, self).button_unplan()

        if any(production.matrix_state not in ['planned', 'pending'] for production in self):
            raise UserError(_(
                "La anulación de la planificación de la matriz solo es posible si el estado es 'Planificado'. "
                "No se puede anular si está pendiente, en progreso o finalizado."
            ))
        
        res = super(MrpProduction, self).button_unplan()
        self.write({'matrix_state': 'pending'})
        return res

    def action_start_matrix_progress(self):
        """
        Pasa el estado de la matriz a 'En Progreso' y sincroniza la cantidad
        total a producir de la matriz con el campo principal de la OP.
        """
        for production in self:
            total_qty_producing = sum(production.matrix_line_ids.mapped('qty_producing'))
            production.write({
                'qty_producing': total_qty_producing,
                'matrix_state': 'progress'
            })
        return True

    def action_revert_matrix_to_planned(self):
        """
        Revierte el estado de la matriz a 'Planificado'.
        """
        self.write({'matrix_state': 'planned'})
        return True

    def action_recalculate_matrix(self):
        """
        Recalcula la distribución de cantidades en la matriz.
        Esta versión robusta borra las líneas existentes y las recrea
        siguiendo la lógica de distribución por filas y luego por columnas.
        """
        self.ensure_one()
        if self.matrix_state != 'pending':
            raise UserError("La matriz solo se puede recalcular en estado 'Pendiente'.")

        # Forzar sincronización de la curva de tallas para usar datos frescos
        existing_proportions = {c.attribute_value_id.id: c.proportion for c in self.matrix_curve_ids}
        curve_commands = []
        for value in self.matrix_values_col_ids:
            curve_commands.append((0, 0, {
                'attribute_value_id': value.id,
                'proportion': existing_proportions.get(value.id, 1.0)
            }))
        if curve_commands:
            self.matrix_curve_ids = [(5, 0, 0)] + curve_commands

        # Validaciones
        total_qty_mo = self.product_qty
        num_rows = len(self.matrix_values_row_ids)
        if total_qty_mo <= 0 or num_rows == 0:
            self.matrix_line_ids = [(5, 0, 0)] # Limpiar la matriz si no hay nada que calcular
            return True

        curve_map = {c.attribute_value_id.id: c.proportion for c in self.matrix_curve_ids}
        selected_col_ids = self.matrix_values_col_ids.ids
        total_proportion = sum(prop for val_id, prop in curve_map.items() if val_id in selected_col_ids)

        if total_proportion == 0:
            raise UserError("La suma de las proporciones para las columnas seleccionadas es cero. Ajuste la curva.")

        # Lógica de distribución y redondeo inteligente
        matrix_values = {}
        qty_per_row = total_qty_mo / num_rows
        
        for row_val in self.matrix_values_row_ids:
            row_cells = []
            for col_val in self.matrix_values_col_ids:
                col_prop = curve_map.get(col_val.id, 0)
                ideal_val = qty_per_row * (col_prop / total_proportion)
                rounded_val = math.ceil(ideal_val)
                cell_key = (row_val.id, col_val.id)
                matrix_values[cell_key] = {'ideal': ideal_val, 'rounded': rounded_val, 'final': rounded_val}
                row_cells.append(cell_key)

            # Ajuste por fila
            total_rounded_in_row = sum(matrix_values[key]['rounded'] for key in row_cells)
            rounded_qty_per_row = float_round(qty_per_row, precision_rounding=self.product_uom_id.rounding)
            excess_in_row = total_rounded_in_row - rounded_qty_per_row
            if excess_in_row > 0:
                sorted_cells = sorted(row_cells, key=lambda k: (matrix_values[k]['rounded'] - matrix_values[k]['ideal']), reverse=True)
                for i in range(int(excess_in_row)):
                    matrix_values[sorted_cells[i % len(sorted_cells)]]['final'] -= 1

        # Ajuste final para el total general
        final_total = sum(v['final'] for v in matrix_values.values())
        final_difference = total_qty_mo - final_total
        if final_difference != 0 and matrix_values:
            first_key = next(iter(matrix_values.keys()))
            matrix_values[first_key]['final'] += final_difference
            
        # Crear nuevas líneas
        new_lines_cmds = [
            (0, 0, {'row_value_id': r, 'col_value_id': c, 'product_qty': v['final'], 'qty_producing': 0})
            for (r, c), v in matrix_values.items()
        ]
        
        self.matrix_line_ids = [(5, 0, 0)] + new_lines_cmds
        return True

    def button_mark_done(self):
        # Restaurado al comportamiento estándar de Odoo.
        # El usuario llamará a este método en las OPs individuales generadas por la matriz.
        return super(MrpProduction, self).button_mark_done()

    def action_generate_serial(self):
        # Restaurado al comportamiento original del addon, ya que el flujo ha cambiado.
        if self.matrix_attribute_row_id and self.matrix_attribute_col_id:
            raise UserError(_(
                "No se puede generar un número de lote manualmente para esta orden de producción. "
                "Los lotes se crearán automáticamente desde la matriz al finalizar el proceso."
            ))
        return super(MrpProduction, self).action_generate_serial()

    def action_split_by_matrix(self):
        """
        Acción principal para dividir una OP según la matriz de producción.
        1. La OP original se actualiza con la cantidad residual.
        2. Se crean nuevas OPs (backorders) para cada celda de la matriz.
        3. Se crean y asignan lotes con atributos a cada nueva OP.
        4. Se limpia la matriz de la OP original.
        5. Se devuelve una vista de lista con las nuevas OPs.
        """
        self.ensure_one()
        
        lines_to_produce = self.matrix_line_ids.filtered(lambda l: l.qty_producing > 0)
        if not lines_to_produce:
            raise UserError(_("No ha registrado ninguna cantidad a producir en la matriz."))

        total_matrix_qty = sum(lines_to_produce.mapped('qty_producing'))
        
        if float_compare(total_matrix_qty, self.product_qty, precision_rounding=self.product_uom_id.rounding) > 0:
            raise UserError(_(
                "La cantidad total de la matriz (%.2f) no puede ser mayor que la cantidad a producir de la orden (%.2f).",
                total_matrix_qty, self.product_qty
            ))

        residual_qty = self.product_qty - total_matrix_qty
        matrix_data_ordered = list(lines_to_produce)

        # La primera cantidad es la que se quedará en la OP original.
        amounts_for_split = [residual_qty] + [line.qty_producing for line in matrix_data_ordered]
        
        # Dividir la OP. `_split_productions` devuelve todas las OPs involucradas.
        all_productions = self._split_productions({self: amounts_for_split})
        
        # Las nuevas OPs son todas excepto la original (self).
        new_productions = all_productions.filtered(lambda p: p != self)

        if len(new_productions) != len(matrix_data_ordered):
            raise UserError(_("La división de la orden de producción falló. Se generó un número inesperado de órdenes."))

        for production, matrix_line in zip(new_productions, matrix_data_ordered):
            lot_name = self.env['ir.sequence'].next_by_code('stock.lot.serial') or _('Nuevo Lote')
            lot = self.env['stock.lot'].create({
                'name': lot_name, 
                'product_id': production.product_id.id,
                'company_id': production.company_id.id,
            })
            self.env['stock.lot.attribute.line'].create([
                {'lot_id': lot.id, 'attribute_id': self.matrix_attribute_row_id.id, 'value_id': matrix_line.row_value_id.id},
                {'lot_id': lot.id, 'attribute_id': self.matrix_attribute_col_id.id, 'value_id': matrix_line.col_value_id.id}
            ])

            # Asignar lote y limpiar la configuración de la matriz en la nueva OP.
            production.write({
                'lot_producing_id': lot.id,
                'matrix_attribute_row_id': False,
                'matrix_attribute_col_id': False,
            })
            if production.state == 'draft':
                production.action_confirm()
        
        # Limpiar la matriz de la OP original y actualizar su estado.
        self.write({
            'matrix_state': 'done',
            'qty_producing': 0,
        })
        self.matrix_line_ids.write({'qty_producing': 0})

        # Devolver una acción para mostrar las nuevas OPs en una vista de lista.
        return {
            'type': 'ir.actions.act_window',
            'name': _('Órdenes de Producción Divididas'),
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('id', 'in', new_productions.ids)],
        }

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

    def _get_move_raw_values(self, bom_line, product, product_uom_qty, operation, bom):
        """
        Sobrescribe el método original para añadir los valores de atributos de
        la matriz desde la línea de la LdM al diccionario de valores del
        movimiento de stock.
        Este es el punto de herencia correcto que funciona tanto en onchange como al guardar.
        AC5 de HU-MRP-004.
        """
        res = super()._get_move_raw_values(bom_line, product, product_uom_qty, operation, bom)
        if bom_line:
            res['matrix_row_value_ids'] = [(6, 0, bom_line.matrix_row_value_ids.ids)]
            res['matrix_col_value_ids'] = [(6, 0, bom_line.matrix_col_value_ids.ids)]
        return res
