# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_lot_attribute = fields.Boolean(
        string="Es un Atributo de Lote",
        help="Marcar esta casilla si este atributo se utilizará para registrar valores específicos en los lotes/números de serie."
    )