# -*- coding: utf-8 -*-
from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    attribute_line_ids = fields.One2many(
        'stock.lot.attribute.line',
        'lot_id',
        string='Líneas de Atributos'
    )