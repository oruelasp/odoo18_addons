from odoo import fields, api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _compute_location_id(self):
        pass

    @api.onchange('user_id')
    def get_records(self):
        if not self.env.user.has_group('warehouse_restriction_for_user.ware_house_user_restrict'):
            return

        domain = {}
        if self.env.user.restrict_ware_house:
            warehouses = self.env.user.allowed_ware_house_ids
            picking_types = warehouses.mapped('picking_type_ids')
            locations = self.env['stock.location'].search([('warehouse_id', 'in', warehouses.ids)])
            domain = {
                'picking_type_id': [('id', 'in', picking_types.ids)],
                'location_id': [('id', 'in', locations.ids)],
                'location_dest_id': [('id', 'in', locations.ids)],
            }
        else:
            picking_ids = []
            if self.env.user.restrict_operation:
                picking_ids = self.env.user.ware_house_picking_type_ids.ids

            location_ids = []
            if self.env.user.restrict_location:
                location_ids = self.env.user.allow_location_ids.ids

            domain = {
                'picking_type_id': [('id', 'in', picking_ids)],
                'location_id': [('id', 'in', location_ids)],
                'location_dest_id': [('id', 'in', location_ids)],
            }

        if domain:
            return {'domain': domain}

        return
