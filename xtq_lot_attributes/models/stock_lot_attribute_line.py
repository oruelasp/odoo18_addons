# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockLotAttributeLine(models.Model):
    _name = 'stock.lot.attribute.line'
    _description = 'Línea de Atributo para Lote'
    _rec_name = 'attribute_id'

    lot_id = fields.Many2one(
        'stock.lot', 
        string='Lote/Nº de Serie',
        required=True, 
        ondelete='cascade'
    )
    attribute_id = fields.Many2one(
        'product.attribute', 
        string='Atributo',
        required=True,
        domain="[('is_lot_attribute', '=', True)]"
    )
    value_id = fields.Many2one(
        'product.attribute.value', 
        string='Valor',
        required=True,
        domain="[('attribute_id', '=', attribute_id)]" 
    )

    _sql_constraints = [
        ('unique_lot_attribute', 'unique(lot_id, attribute_id)',
         '¡No puedes registrar el mismo atributo dos veces para un mismo lote!')
    ]