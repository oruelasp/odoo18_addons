# -*- coding: utf-8 -*-
from odoo import models, fields

class SalesProgramMatrixLine(models.Model):
    _name = 'sales.program.matrix.line'
    _description = 'Línea de Matriz para Programa de Ventas'

    program_id = fields.Many2one(
        'sales.program',
        string='Programa de Venta',
        required=True,
        ondelete='cascade',
        index=True
    )
    sales_program_line_id = fields.Many2one(
        'sales.program.line',
        string='Línea del Programa',
        required=True,
        ondelete='cascade'
    )
    col_value_id = fields.Many2one(
        'product.attribute.value',
        string='Valor Columna (Talla)',
        required=True,
        ondelete='cascade'
    )
    product_qty = fields.Float(
        string='Cantidad Planificada',
        digits='Product Unit of Measure'
    )

    _sql_constraints = [
        ('unique_matrix_entry', 'unique(program_id, sales_program_line_id, col_value_id)',
         'Ya existe una entrada en la matriz para esta combinación de línea y valor de columna.')
    ]
