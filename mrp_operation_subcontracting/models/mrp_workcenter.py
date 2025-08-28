# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models, _

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    is_subcontract = fields.Boolean("¿Es subcontratado?")
    partner_id = fields.Many2one('res.partner', 
        string='Proveedor', #states=READONLY_STATES, 
        change_default=True, tracking=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", 
        help="Puede encontrar un proveedor por su Nombre, TIN, Email o Referencia Interna.")
    product_id = fields.Many2one('product.product',
        string="Producto de Subcontratación",
        domain="[('type', '=', 'service')]",
        help="El producto de servicio que se usará en la orden de compra para esta operación de subcontratación.")
