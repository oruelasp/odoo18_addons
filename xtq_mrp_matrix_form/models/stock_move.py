# -*- coding: utf-8 -*-

from odoo import models, fields

class StockMove(models.Model):
    """
    Extiende el modelo de movimiento de stock para almacenar los valores de
    atributos de la matriz a los que aplica un movimiento de componente,
    heredados desde la línea de la LdM.
    """
    _inherit = 'stock.move'

    matrix_row_value_ids = fields.Many2many(
        'product.attribute.value',
        'stock_move_row_attr_val_rel',
        'move_id', 'attribute_value_id',
        string='Valores Fila Aplicables (Matriz)',
        copy=False,
        help="Valores del atributo de Fila a los que este movimiento de componente aplica."
    )
    matrix_col_value_ids = fields.Many2many(
        'product.attribute.value',
        'stock_move_col_attr_val_rel',
        'move_id', 'attribute_value_id',
        string='Valores Columna Aplicables (Matriz)',
        copy=False,
        help="Valores del atributo de Columna a los que este movimiento de componente aplica."
    )
