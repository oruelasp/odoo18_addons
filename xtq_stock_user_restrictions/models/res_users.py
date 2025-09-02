# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    stock_restrictions_active = fields.Boolean(
        string='Activate Stock Restrictions',
        help="If checked, the stock restrictions defined below will be applied to this user.",
    )
    stock_restriction_rule_ids = fields.One2many(
        comodel_name='stock.user.restriction.rule',
        inverse_name='user_id',
        string='Stock Restriction Rules',
    )

    def _get_allowed_picking_type_ids(self):
        """
        Returns the list of picking type IDs the user has access to based on
        their restriction rules.
        """
        self.ensure_one()
        if not self.stock_restrictions_active:
            # If restrictions are not active, return all picking types.
            # The empty search domain `[]` means "no condition", so it finds all records.
            return self.env['stock.picking.type'].search([]).ids

        allowed_picking_type_ids = set()
        # Warehouses for which all picking types should be fetched
        warehouses_to_fetch_all = self.env['stock.warehouse']

        for rule in self.stock_restriction_rule_ids:
            if not rule.picking_type_ids:
                warehouses_to_fetch_all |= rule.warehouse_id
            else:
                allowed_picking_type_ids.update(rule.picking_type_ids.ids)
        
        if warehouses_to_fetch_all:
            all_types_in_warehouses = self.env['stock.picking.type'].search([
                ('warehouse_id', 'in', warehouses_to_fetch_all.ids)
            ])
            allowed_picking_type_ids.update(all_types_in_warehouses.ids)

        return list(allowed_picking_type_ids)
