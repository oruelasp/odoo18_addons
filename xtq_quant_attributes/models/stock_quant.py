# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # Campos para almacenar dinámicamente los valores de los atributos
    x_lot_attr_value_1 = fields.Char(compute='_compute_lot_attributes', string="Valor Atributo 1")
    x_lot_attr_value_2 = fields.Char(compute='_compute_lot_attributes', string="Valor Atributo 2")
    x_lot_attr_value_3 = fields.Char(compute='_compute_lot_attributes', string="Valor Atributo 3")
    x_lot_attr_value_4 = fields.Char(compute='_compute_lot_attributes', string="Valor Atributo 4")
    x_lot_attr_value_5 = fields.Char(compute='_compute_lot_attributes', string="Valor Atributo 5")

    # Campos para almacenar dinámicamente las etiquetas de los atributos (para la vista)
    x_lot_attr_label_1 = fields.Char(compute='_compute_lot_attributes')
    x_lot_attr_label_2 = fields.Char(compute='_compute_lot_attributes')
    x_lot_attr_label_3 = fields.Char(compute='_compute_lot_attributes')
    x_lot_attr_label_4 = fields.Char(compute='_compute_lot_attributes')
    x_lot_attr_label_5 = fields.Char(compute='_compute_lot_attributes')

    @api.depends('lot_id', 'product_id')
    def _compute_lot_attributes(self):
        """
        Calcula y asigna los valores y etiquetas de los atributos de lote
        a los campos genéricos para poder mostrarlos en la vista.
        """
        for quant in self:
            # Inicializar todos los campos
            for i in range(1, 6):
                setattr(quant, f'x_lot_attr_value_{i}', False)
                setattr(quant, f'x_lot_attr_label_{i}', False)

            if not quant.lot_id or not quant.product_id:
                continue

            # Obtener los atributos de lote relevantes para este producto
            lot_attributes = self.env['product.attribute'].search([
                ('is_lot_attribute', '=', True),
                ('product_tmpl_ids', 'in', quant.product_id.product_tmpl_id.id),
            ], limit=5, order='id')

            if not lot_attributes:
                continue

            # Crear un mapa de los valores de atributo del lote actual
            attribute_values = {
                line.attribute_id.id: line.value_id.name or ''
                for line in quant.lot_id.attribute_line_ids
            }

            # Asignar valores y etiquetas a los campos genéricos
            for i, attr in enumerate(lot_attributes, start=1):
                setattr(quant, f'x_lot_attr_label_{i}', attr.name)
                if attr.id in attribute_values:
                    setattr(quant, f'x_lot_attr_value_{i}', attribute_values[attr.id])
