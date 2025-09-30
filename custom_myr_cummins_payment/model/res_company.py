from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    api_mode = fields.Selection(
        selection=[
            ("api_net", "API NET")
        ],
        string="API a usar"
    )
    token_api = fields.Char(string="Token")
