# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class QuantAttributeSelectionWizard(models.TransientModel):
    _name = 'quant.attribute.selection.wizard'
    _description = 'Asistente para Seleccionar Lotes por Atributos de Calidad'

    move_id = fields.Many2one('stock.move', string="Movimiento de Origen", required=True)
    line_ids = fields.One2many(
        'quant.attribute.selection.line',
        'wizard_id',
        string="Líneas de Quants"
    )

    def action_confirm_selection(self):
        """
        Procesa las líneas seleccionadas y las añade al stock.move.
        Esta es una implementación básica. La lógica de asignación de move lines
        puede ser más compleja y necesitar ajustes según el flujo exacto de Odoo.
        """
        self.ensure_one()
        selected_lines = self.line_ids.filtered('selected')
        if not selected_lines:
            raise UserError("No se ha seleccionado ninguna línea.")

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
        
        if not move_lines_vals:
            raise UserError("No se ha especificado una cantidad a reservar en ninguna línea.")

        # Reemplaza las move lines existentes con las nuevas seleccionadas
        move.write({'move_line_ids': [(5, 0, 0)] + [(0, 0, vals) for vals in move_lines_vals]})

        return {'type': 'ir.actions.act_window_close'}


class QuantAttributeSelectionLine(models.TransientModel):
    _name = 'quant.attribute.selection.line'
    _description = 'Línea de Selección de Lotes por Atributos'

    wizard_id = fields.Many2one('quant.attribute.selection.wizard', string="Asistente", required=True)
    selected = fields.Boolean(string="Seleccionado", default=False)

    # Campos estándar del quant
    quant_id = fields.Many2one('stock.quant', string="Quant", required=True)
    lot_id = fields.Many2one('stock.lot', string="Lote/Nº de Serie", related='quant_id.lot_id', store=False, readonly=True)
    location_id = fields.Many2one('stock.location', string="Ubicación", related='quant_id.location_id', store=False, readonly=True)
    available_quantity = fields.Float(string="Cantidad Disponible", related='quant_id.quantity', store=False)
    product_uom_id = fields.Many2one('uom.uom', string="UdM", related='quant_id.product_uom_id', store=False, readonly=True)
    
    quantity_to_reserve = fields.Float(string="Cantidad a Reservar")

    # Campos genéricos para atributos dinámicos
    # Se usarán hasta 5 columnas dinámicas. Se pueden añadir más si es necesario.
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
                raise ValidationError(
                    f"La cantidad a reservar ({line.quantity_to_reserve}) para el lote {line.lot_id.name} "
                    f"no puede exceder la cantidad disponible ({line.available_quantity})."
                )
