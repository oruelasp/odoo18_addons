# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Orden de Servicio",
        readonly=True,
        copy=False,
    )
    is_subcontract = fields.Boolean(
        related='workcenter_id.is_subcontract',
        string="¿Es subcontratado?",
        readonly=True,
        store=True,
    )

    def _calc_operation_cost(self, opt):
        duration_expected = opt.duration_expected or 0
        return (duration_expected / 60) * opt.workcenter_id.costs_hour

    def action_create_subcontract_po(self):
        self.ensure_one()
        if not self.workcenter_id.is_subcontract:
            raise UserError(_("This work order is not a subcontracting operation."))
        if self.purchase_order_id:
            raise UserError(_("A purchase order has already been created for this work order."))
        if not self.workcenter_id.partner_id:
            raise UserError(_("You must configure a Vendor on the subcontracting Work Center."))
        if not self.workcenter_id.product_id:
            raise UserError(_("You must configure a Subcontract Product on the subcontracting Work Center."))

        workcenter = self.workcenter_id
        product = self.workcenter_id.product_id

        cost = self._calc_operation_cost(self)
        po_vals = {
            'partner_id': workcenter.partner_id.id,
            'origin': f"{self.production_id.name} - {self.name}",
            'order_line': [Command.create({
                'product_id': product.id,
                'product_qty': self.production_id.product_qty,
                'price_unit': cost,
            })],
        }
        purchase_order = self.env['purchase.order'].create(po_vals)
        self.purchase_order_id = purchase_order.id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Subcontracting Purchase Order'),
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'target': 'current',
        }                
