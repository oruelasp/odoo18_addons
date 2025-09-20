# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class QuantAttributeSelectionWizard(models.TransientModel):
    _name = 'quant.attribute.selection.wizard'
    _description = 'Asistente para Seleccionar Lotes por Atributos de Calidad'
    _rec_name = 'display_name'

    # --- NEW DISPLAY NAME FIELD ---
    display_name = fields.Char(string="Título", compute='_compute_display_name')

    # --- CAMPOS DE CABECERA ---
    move_id = fields.Many2one('stock.move', string="Movimiento de Origen", required=True, readonly=True)
    product_id = fields.Many2one('product.product', string="Producto", related='move_id.product_id', readonly=True)
    demanded_quantity = fields.Float(string="Cantidad Demandada", related='move_id.product_uom_qty', readonly=True)
    picking_info = fields.Char(string="Documento de Origen", compute='_compute_picking_info')
    selected_quantity = fields.Float(string="Cantidad Seleccionada", compute='_compute_selected_quantity', digits='Product Unit of Measure')

    # --- CAMPOS DE LÍNEAS Y PESTAÑAS ---
    # Usaremos un solo campo One2many y lo filtraremos en la vista por el estado
    line_ids = fields.One2many('quant.attribute.selection.line', 'wizard_id', string="Líneas de Lotes")

    # --- CAMPOS DE BÚSQUEDA ---
    search_filter_ids = fields.One2many('quant.attribute.selection.search.filter', 'wizard_id', string="Filtros de Búsqueda")

    @api.depends('picking_info')
    def _compute_display_name(self):
        for wizard in self:
            wizard.display_name = f"Selección Asistida para: {wizard.picking_info}"

    @api.depends('move_id.picking_id')
    def _compute_picking_info(self):
        for wizard in self:
            wizard.picking_info = wizard.move_id.picking_id.name if wizard.move_id.picking_id else 'N/A'

    @api.depends('line_ids', 'line_ids.selection_status', 'line_ids.quantity_to_reserve')
    def _compute_selected_quantity(self):
        for wizard in self:
            wizard.selected_quantity = sum(
                wizard.line_ids.filtered(lambda l: l.selection_status == 'selected').mapped('quantity_to_reserve')
            )

    def action_search(self):
        """
        Limpia los resultados anteriores y ejecuta una nueva búsqueda de quants
        basándose en los filtros activos, creando nuevas líneas de wizard solo para los resultados.
        """
        self.ensure_one()
        
        # 1. Limpiar resultados de búsqueda anteriores (líneas en estado 'available')
        available_lines = self.line_ids.filtered(lambda l: l.selection_status == 'available')
        if available_lines:
            self.line_ids = [(2, line.id) for line in available_lines]

        # 2. Obtener filtros activos
        active_filters = self.search_filter_ids.filtered(lambda f: f.is_active and f.value_id)
        if not active_filters:
            # Si no hay filtros activos, no se muestra nada, como se solicitó.
            return

        # 3. Buscar todos los quants base que podrían ser candidatos
        all_quants = self.env['stock.quant']._gather(
            self.product_id, self.move_id.location_id, strict=False
        ).filtered(lambda q: q.quantity > 0 and q.lot_id)

        # 4. Filtrar los quants que coincidan con TODOS los atributos seleccionados
        matching_quants = []
        for quant in all_quants:
            lot = quant.lot_id
            if all(
                lot.attribute_line_ids.filtered(
                    lambda attr_line: attr_line.attribute_id == f.attribute_id and attr_line.value_id == f.value_id
                ) for f in active_filters
            ):
                matching_quants.append(quant)

        # 5. Preparar los valores para crear las nuevas líneas del wizard
        column_attributes = self.env['product.attribute'].browse(
            self.search_filter_ids.mapped('attribute_id').ids
        )
        new_lines_vals = []
        for quant in matching_quants:
            line_vals = {
                'quant_id': quant.id,
                'selection_status': 'available',
            }
            for i, attr in enumerate(column_attributes[:5]):
                attr_line = quant.lot_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attr
                )
                field_name = f'attr_col_{i + 1}'
                line_vals[field_name] = attr_line.value_id.name if attr_line else ''
            new_lines_vals.append((0, 0, line_vals))

        # 6. Escribir las nuevas líneas en el wizard
        if new_lines_vals:
            self.write({'line_ids': new_lines_vals})

    def action_add_to_selection(self):
        """Mueve las líneas seleccionadas de 'available' a 'selected'."""
        self.ensure_one()
        self.line_ids.filtered(lambda l: l.selected and l.selection_status == 'available').write({
            'selection_status': 'selected',
            'selected': False, # Desmarcar para la siguiente operación
        })

    def action_remove_from_selection(self):
        """Devuelve las líneas seleccionadas de 'selected' a 'available'."""
        self.ensure_one()
        self.line_ids.filtered(lambda l: l.selected and l.selection_status == 'selected').write({
            'selection_status': 'available',
            'selected': False, # Desmarcar para la siguiente operación
        })
        
    def action_confirm_selection(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered(lambda l: l.selection_status == 'selected')
        if not selected_lines:
            raise UserError("No se ha seleccionado ninguna línea para confirmar.")

        move = self.move_id
        move_lines_vals = []
        for line in selected_lines:
            if line.quantity_to_reserve > 0:
                move_lines_vals.append({
                    'picking_id': move.picking_id.id,
                    'lot_id': line.lot_id.id,
                    'quantity': line.quantity_to_reserve,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                })

        move.write({'move_line_ids': [(5, 0, 0)] + [(0, 0, vals) for vals in move_lines_vals]})
        return {'type': 'ir.actions.act_window_close'}


class QuantAttributeSelectionLine(models.TransientModel):
    _name = 'quant.attribute.selection.line'
    _description = 'Línea de Selección de Lotes por Atributos'

    wizard_id = fields.Many2one('quant.attribute.selection.wizard', string="Asistente", required=True, ondelete='cascade')
    selection_status = fields.Selection([('available', 'Disponible'), ('selected', 'Seleccionado')], default='available', required=True)
    selected = fields.Boolean(string="Seleccionar")
    is_visible_in_search = fields.Boolean(string="Visible en Búsqueda", default=True)

    quant_id = fields.Many2one('stock.quant', string="Quant", required=True)
    lot_id = fields.Many2one('stock.lot', string="Lote/Nº de Serie", related='quant_id.lot_id', readonly=True)
    location_id = fields.Many2one('stock.location', string="Ubicación", related='quant_id.location_id', readonly=True)
    available_quantity = fields.Float(string="Cantidad Disponible", related='quant_id.quantity')
    product_uom_id = fields.Many2one('uom.uom', string="UdM", related='quant_id.product_uom_id', readonly=True)
    quantity_to_reserve = fields.Float(string="Cantidad a Reservar")

    attr_col_1 = fields.Char(string="Atributo 1")
    attr_col_2 = fields.Char(string="Atributo 2")
    attr_col_3 = fields.Char(string="Atributo 3")
    attr_col_4 = fields.Char(string="Atributo 4")
    attr_col_5 = fields.Char(string="Atributo 5")

    @api.constrains('quantity_to_reserve', 'available_quantity')
    def _check_quantity_to_reserve(self):
        for line in self:
            if line.quantity_to_reserve < 0:
                raise ValidationError("La cantidad a reservar no puede ser negativa.")
            if line.quantity_to_reserve > line.available_quantity:
                raise ValidationError(f"La cantidad a reservar para el lote {line.lot_id.name} no puede exceder la disponible.")


class QuantAttributeSelectionSearchFilter(models.TransientModel):
    _name = 'quant.attribute.selection.search.filter'
    _description = 'Filtro de Búsqueda para Selección de Lotes'

    wizard_id = fields.Many2one('quant.attribute.selection.wizard', string="Asistente", required=True, ondelete='cascade')
    is_active = fields.Boolean(string="Usar Filtro")
    attribute_id = fields.Many2one('product.attribute', string="Atributo", required=True, readonly=True)
    value_id = fields.Many2one('product.attribute.value', string="Valor a Buscar", domain="[('attribute_id', '=', attribute_id)]")
