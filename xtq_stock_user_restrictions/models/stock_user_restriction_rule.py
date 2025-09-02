# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockUserRestrictionRule(models.Model):
    _name = 'stock.user.restriction.rule'
    _description = 'Stock User Restriction Rule'

    user_id = fields.Many2one(
        comodel_name='res.users',
        required=True,
        ondelete='cascade',
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        required=True,
    )
    picking_type_ids = fields.Many2many(
        comodel_name='stock.picking.type',
        string='Allowed Picking Types',
        help="If left empty, all picking types for the selected warehouse will be allowed.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped('user_id').clear_caches()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.mapped('user_id').clear_caches()
        return res

    def unlink(self):
        users_to_clear = self.mapped('user_id')
        res = super().unlink()
        users_to_clear.clear_caches()
        return res
