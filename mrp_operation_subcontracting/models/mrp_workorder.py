# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, Command

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        readonly=True,
        copy=False,
    )

    def _calc_operation_cost(self, opt):
        duration_expected = opt.duration_expected or 0
        return (duration_expected / 60) * opt.workcenter_id.costs_hour

    def action_create_subcontract_po(self):
        for workorder in self.filtered(lambda wo: wo.workcenter_id.is_subcontract and not wo.purchase_order_id):
            workcenter = workorder.workcenter_id
            name = f"{workorder.id}_{workorder.name}@{workorder.production_id.name}"
            # create service product
            product = self.env['product.product'].search([('name', '=', name)], limit=1)
            if not product:
                product = self.env['product.product'].create({
                    'name': name,
                    'sale_ok': False,
                    'purchase_ok': True,
                    'detailed_type': "service"
                })

            cost = self._calc_operation_cost(workorder)
            po_vals = {
                'partner_id': workcenter.partner_id.id,
                'origin': name,
                'order_line': [Command.create({
                    'product_id': product.id,
                    'product_qty': workorder.production_id.product_qty,
                    'price_unit': cost,
                })],
            }
            purchase_order = self.env['purchase.order'].create(po_vals)
            workorder.purchase_order_id = purchase_order.id
        return True                
