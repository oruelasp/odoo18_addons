# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    set_users_limit = fields.Integer(string='Set Your User Limit Here', tracking=True)

    @api.model
    def create(self, vals):
        # Fetch all users and the admin user
        users = self.env['res.users'].search([('share', '=', False),('active', '=', True)])
        admin_user = self.env['res.users'].sudo().search([('login', '=', 'admin')], limit=1)

        if not admin_user:
            raise UserError("Admin user not found.")
        
        # Get the user limit set by the admin
        user_limit = admin_user.set_users_limit

        if len(users) > user_limit:
            raise UserError("Maximum number of users created. Please contact your system administrator.")

        # Proceed with the creation of the user if the limit has not been reached
        return super(ResUsers, self).create(vals)
