# -*- coding: utf-8 -*-
from odoo import models, fields

class QuantAttributeSelectionWizard(models.TransientModel):
    _name = 'quant.attribute.selection.wizard'
    _description = 'Asistente para Seleccionar Lotes por Atributos de Calidad'

    html_table = fields.Html(string="Atributos de Calidad", sanitize=False, readonly=True)
    
    # Aún dejamos las líneas por si después se amplía el flujo para selección/confirmación
    quant_line_ids = fields.One2many(
        'quant.attribute.selection.line',
        'wizard_id',
        string="Líneas de Quants"
    )

class QuantAttributeSelectionLine(models.TransientModel):
    _name = 'quant.attribute.selection.line'
    _description = 'Línea de Selección de Atributos de Quants'

    wizard_id = fields.Many2one(
        'quant.attribute.selection.wizard',
        string="Asistente"
    )
    selected = fields.Boolean(string="Seleccionado")
    quant_id = fields.Many2one('stock.quant', string="Quant", required=True)
    lot_id = fields.Many2one(related='quant_id.lot_id', readonly=True)
    location_id = fields.Many2one(related='quant_id.location_id', readonly=True)
    quantity = fields.Float(related='quant_id.quantity', readonly=True)
    product_uom_id = fields.Many2one(related='quant_id.product_uom_id', readonly=True)
