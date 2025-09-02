from odoo import fields, api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_operation = fields.Boolean('Restrict Operation')
    restrict_location = fields.Boolean('Restrict Location')
    allow_location_ids = fields.Many2many('stock.location')
    restrict_ware_house = fields.Boolean('Restrict warehouse')
    allowed_ware_house_ids = fields.Many2many('stock.warehouse')
    ware_house_picking_type_ids = fields.Many2many('stock.picking.type')

    @api.onchange('restrict_operation', 'restrict_location', 'restrict_ware_house')
    def ware_get(self):
        if not self.restrict_ware_house:
            self.allowed_ware_house_ids = [(5, 0, 0)]
        if not self.restrict_operation:
            self.ware_house_picking_type_ids = [(5, 0, 0)]
        if not self.restrict_location:
            self.allow_location_ids = [(5, 0, 0)]

    def _toggle_menus(self):
        """
        Show or hide menus based on user restrictions.
        This is a workaround and might not be fully effective in Odoo 18+ web client.
        Prefer using security groups on menus directly.
        """
        # Deactivate all relevant menus first, then activate the ones that should be visible.
        menus_to_manage = [
            'stock.in_picking', 'stock.out_picking', 'stock.int_picking',
            'mrp.mrp_operation_picking', 'stock_picking_batch.stock_picking_batch_menu',
            'stock_dropshipping.dropship_picking'
        ]
        all_menus = self.env['ir.ui.menu']
        for menu_xml_id in menus_to_manage:
            menu = self.env.ref(menu_xml_id, raise_if_not_found=False)
            if menu:
                all_menus += menu
        
        all_menus.write({'active': True}) # Reset all to active

        if self.restrict_operation:
            # Map codes to menus
            code_menu_map = {
                'incoming': ['stock.in_picking'],
                'outgoing': ['stock.out_picking'],
                'internal': ['stock.int_picking'],
                'mrp_operation': ['mrp.mrp_operation_picking'],
                'Batch Transfers': ['stock_picking_batch.stock_picking_batch_menu'],
                'dropship': ['stock_dropshipping.dropship_picking'],
            }
            
            allowed_codes = self.ware_house_picking_type_ids.mapped('code')
            menus_to_deactivate = self.env['ir.ui.menu']
            
            for code, menu_xml_ids in code_menu_map.items():
                if code not in allowed_codes:
                    for menu_xml_id in menu_xml_ids:
                        menu = self.env.ref(menu_xml_id, raise_if_not_found=False)
                        if menu:
                            menus_to_deactivate += menu
            
            if menus_to_deactivate:
                menus_to_deactivate.write({'active': False})

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if any(f in vals for f in ['restrict_operation', 'ware_house_picking_type_ids']):
            self.sudo()._toggle_menus()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        users.sudo()._toggle_menus()
        return users

    @api.onchange('ware_house_picking_type_ids', 'allow_location_ids', 'allowed_ware_house_ids')
    def _update_record_rule_domain(self):
        rule = self.env.ref('warehouse_restriction_for_user.restrict_stock_picking', raise_if_not_found=False)
        if not rule:
            return
        
        domain_parts = []
        if self.ware_house_picking_type_ids:
            domain_parts.append(('picking_type_id', 'in', self.ware_house_picking_type_ids.ids))
        if self.allow_location_ids:
            domain_parts.append(('location_id', 'in', self.allow_location_ids.ids))
            domain_parts.append(('location_dest_id', 'in', self.allow_location_ids.ids))

        domain = []
        if len(domain_parts) > 1:
            domain = ['|'] * (len(domain_parts) - 1)
            domain.extend(domain_parts)
        elif domain_parts:
            domain = domain_parts[0]

        rule.domain_force = domain if domain else [(1, '=', 1)]
        self._toggle_menus()
