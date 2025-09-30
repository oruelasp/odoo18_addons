# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    workorder_id = fields.Many2one(
        'mrp.workorder',
        string="Work Order",
        copy=False,
        index=True,
    )
