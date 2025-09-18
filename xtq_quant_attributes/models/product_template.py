# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_quality_attrs_in_picking = fields.Boolean(
        string="Mostrar Atributos de Calidad en Picking",
        help="Si se marca, la ventana de selección de lotes para este producto "
             "mostrará columnas adicionales con sus atributos de calidad."
    )
