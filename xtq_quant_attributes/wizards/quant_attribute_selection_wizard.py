# -*- coding: utf-8 -*-
from odoo import models, fields

class QuantAttributeSelectionWizard(models.TransientModel):
    _name = 'quant.attribute.selection.wizard'
    _description = 'Asistente para Seleccionar Lotes por Atributos de Calidad'

    # Este campo almacenará la vista XML generada dinámicamente
    view_arch = fields.Text(string="View Architecture", readonly=True)

    # Líneas del asistente que representarán los quants
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

    def _compute_attribute_value(self):
        # Esta función computará el valor para los campos dinámicos
        for line in self:
            # Identificar qué campo de atributo se está computando
            field_name = self.env.context.get('field_name_compute')
            if not field_name:
                continue

            attribute = self.env['product.attribute'].search([('name', '=', field_name)], limit=1)
            if attribute:
                attr_line = line.lot_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attribute
                )
                line[field_name] = attr_line.value_id.name if attr_line else ''
            else:
                line[field_name] = ''
