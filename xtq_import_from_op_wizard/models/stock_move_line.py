# -*- coding: utf-8 -*-
from odoo import fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Orden de Trabajo',
        related='picking_id.workorder_id',
        store=True,
    )
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto',
        related='picking_id.project_id',
        store=True,
    )
