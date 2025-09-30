from odoo import models, fields, api, _
from odoo.exceptions import UserError

class UpperProduct(models.TransientModel):
    _name = "upper.text"
    _description = "Convertir a mayúsculas los nombres y códigos SAP de productos"

    def action_set_upper(self):
        productos = self.env["product.template"].search([])  # No es necesario el [()]
        for item in productos:
            valores = {}
            if item.name and item.name != item.name.title():
                valores['name'] = item.name.title()
            if item.codigo_sap and item.codigo_sap != item.codigo_sap.upper():
                valores['codigo_sap'] = item.codigo_sap.upper()
            if item.default_code and item.default_code != item.default_code.upper():
                valores['default_code'] = item.default_code.upper()

            if valores:
                item.write(valores)
