from odoo import models, fields



class Empresa (models.Model):
    _inherit = "res.company"

    url_venta = fields.Char(
        string="URL Ventas",
        help="URL para enviar ordenes de ventas a la SAP mediante API",
        default="https://apimsharedqa01.azure-api.net/sap-odata/bc/zjsonodoo?sap-client=400"
    )
    token_venta = fields.Char(
        string="Token Ventas",
        help="Token de acceso para la API de ordenes de venta",
        default="18070936a6414549a18f09ee2cdd1f0c"
    )