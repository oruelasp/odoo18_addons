# -*- coding: utf-8 -*-
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sales_program_id = fields.Many2one(
        'sales.program',
        string='Sales Program',
        readonly=True,
        copy=False,
    )
