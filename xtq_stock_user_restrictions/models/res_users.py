# -*- coding: utf-8 -*-
from odoo import api, fields, models

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

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        restricted_group = self.env.ref('xtq_stock_user_restrictions.group_stock_restrictions_user', raise_if_not_found=False)
        if restricted_group:
            for user in users.filtered('stock_restrictions_active'):
                restricted_group.sudo().users = [(4, user.id)]
        return users

    def write(self, vals):
        res = super().write(vals)
        if 'stock_restrictions_active' in vals:
            restricted_group = self.env.ref('xtq_stock_user_restrictions.group_stock_restrictions_user', raise_if_not_found=False)
            if restricted_group:
                for user in self:
                    if user.stock_restrictions_active:
                        restricted_group.sudo().users = [(4, user.id)]
                    else:
                        restricted_group.sudo().users = [(3, user.id)]
                self.clear_caches()
        return res

    def _get_allowed_picking_type_ids(self):
        """
        Returns the list of picking type IDs the user has access to based on
        their restriction rules.
        """
        self.ensure_one()
        
        # This condition handles point 2 of your request:
        # If restrictions are active but no rules are defined, the user should see nothing.
        if not self.stock_restriction_rule_ids:
            return []

        allowed_picking_type_ids = set()
        warehouses_to_fetch_all = self.env['stock.warehouse']

        for rule in self.stock_restriction_rule_ids:
            if not rule.picking_type_ids:
                warehouses_to_fetch_all |= rule.warehouse_id
            else:
                allowed_picking_type_ids.update(rule.picking_type_ids.ids)
        
        if warehouses_to_fetch_all:
            # Using sudo() to bypass the chicken-and-egg problem where the rule check
            # would prevent the search for the records needed to evaluate the rule itself.
            all_types_in_warehouses = self.env['stock.picking.type'].sudo().search([
                ('warehouse_id', 'in', warehouses_to_fetch_all.ids)
            ])
            allowed_picking_type_ids.update(all_types_in_warehouses.ids)

        return list(allowed_picking_type_ids)
