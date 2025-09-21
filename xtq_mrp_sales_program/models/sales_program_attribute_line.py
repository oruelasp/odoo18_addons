# -*- coding: utf-8 -*-
from odoo import models, fields

class SalesProgramAttributeLine(models.Model):
    _name = 'sales.program.attribute.line'
    _description = 'Línea de Atributo para Programa de Ventas'

    program_id = fields.Many2one(
        'sales.program',
        string='Programa de Venta',
        required=True,
        ondelete='cascade'
    )
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Atributo',
        required=True
    )
    attribute_value_id = fields.Many2one(
        'product.attribute.value',
        string='Valor',
        required=True,
        domain="[('attribute_id', '=', attribute_id)]"
    )

    _sql_constraints = [
        ('unique_attribute_entry', 'unique(program_id, attribute_id)',
         'Cada atributo debe ser único por Programa de Venta.')
    ]
