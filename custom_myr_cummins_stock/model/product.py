from odoo import models, fields, api
import re

# PRODUCTO VARIANTE
class ProductProduct(models.Model):
    _inherit = "product.product"

    stock_product = fields.Float(string="Stock del Producto", store=True)

    def _compute_quantities(self):
        super()._compute_quantities()
        for product in self:
            product.qty_available = product.stock_product
            product.incoming_qty = 0.0
            product.outgoing_qty = 0.0
            product.virtual_available = product.stock_product
            product.free_qty = product.stock_product


# TEMPLATE
class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_product = fields.Float(
        string="Stock del Producto",
        compute="_compute_stock_product",
        inverse="_inverse_stock_product",
        store=True
    )
    is_product_sap = fields.Boolean(string="Es producto SAP?")
    fecha_registro = fields.Datetime(string="Fecha de registro")
    codigo_sap = fields.Char(string="Código SAP")
    qty_available = fields.Float(
        string='Cantidad en Stock',
        compute='_compute_qty_available',
        store=True
    )

    @api.depends("product_variant_ids.stock_product")
    def _compute_stock_product(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.stock_product = template.product_variant_ids.stock_product
            else:
                template.stock_product = sum(template.product_variant_ids.mapped("stock_product"))

    def _inverse_stock_product(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.stock_product = template.stock_product

    @api.depends("stock_product")
    def _compute_qty_available(self):
        for template in self:
            template.qty_available = template.stock_product


    @api.model
    def create(self, vals):
        if vals.get('default_code'):
            vals['default_code'] = vals['default_code'].upper()
        if vals.get('codigo_sap'):
            vals['codigo_sap'] = vals['codigo_sap'].upper()
        if vals.get('name') and vals.get('default_code'):
            name = vals['name']
            code = vals['default_code']
            if code.lower() in name.lower():
                import re
                pattern = re.compile(re.escape(code), re.IGNORECASE)
                name_title = name.title()
                vals['name'] = pattern.sub(code.upper(), name_title)
            else:
                vals['name'] = name.title()
        elif vals.get('name'):
            vals['name'] = vals['name'].title()

        return super().create(vals)

    def write(self, vals):
        if vals.get('default_code'):
            vals['default_code'] = vals['default_code'].upper()
        if vals.get('codigo_sap'):
            vals['codigo_sap'] = vals['codigo_sap'].upper()
        if vals.get('name') and (vals.get('default_code') or self.default_code):
            name = vals['name']
            code = vals.get('default_code', self.default_code).upper()
            if code.lower() in name.lower():
                import re
                pattern = re.compile(re.escape(code), re.IGNORECASE)
                name_title = name.title()
                vals['name'] = pattern.sub(code.upper(), name_title)
            else:
                vals['name'] = name.title()
        elif vals.get('name'):
            vals['name'] = vals['name'].title()

        return super().write(vals)
