# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

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
        # This field is no longer required to allow setting rules for picking types without a warehouse.
    )
    picking_type_ids = fields.Many2many(
        comodel_name='stock.picking.type',
        string='Allowed Picking Types',
        help="If a warehouse is selected and this field is left empty, all picking types for that warehouse will be allowed.",
    )

    @api.constrains('warehouse_id', 'picking_type_ids')
    def _check_warehouse_or_picking_type(self):
        for rule in self:
            if not rule.warehouse_id and not rule.picking_type_ids:
                raise ValidationError("A rule must have either a Warehouse or at least one Allowed Picking Type defined.")

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
