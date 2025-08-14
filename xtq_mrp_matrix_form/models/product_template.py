# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    matrix_attribute_x_id = fields.Many2one(
        'product.attribute',
        string='Atributo Matriz X',
        help="Define el atributo que se usará para el eje X en la matriz de producción."
    )
    matrix_attribute_y_id = fields.Many2one(
        'product.attribute',
        string='Atributo Matriz Y',
        help="Define el atributo que se usará para el eje Y en la matriz de producción."
    )
