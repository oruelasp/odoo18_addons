from odoo import models, fields, api, _
from num2words import num2words
import json
import requests
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Envio de email y status"


    id_sap = fields.Char(
        string="ID SAP",
        help="ID del pedido en SAP, se usa para la integración con SAP.",
        copy=False,
    )
    is_sap_confirm = fields.Boolean(
        string="Confirmado en SAP",
        help="Indica si el pedido ha sido confirmado en SAP.",
        default=False,
        copy=False,
    )
    numero_tarjeta = fields.Char(string="Número de tarjeta")
    tipo_tarjeta = fields.Char(string="Tipo de tarjeta")
    delivery_untaxed = fields.Monetary(
        compute='_compute_split_totals',
        string='Entrega sin IGV',
        store=True
    )
    amount_untaxed_without_delivery = fields.Monetary(
        compute='_compute_split_totals',
        string='Subtotal sin delivery',
        store=True
    )
    amount_tax_without_delivery = fields.Monetary(
        compute='_compute_split_totals',
        string='Impuestos sin delivery',
        store=True
    )

    @api.depends('order_line.price_subtotal', 'order_line.price_tax')
    def _compute_split_totals(self):
        for order in self:
            delivery_lines = order.order_line.filtered(lambda l: l.is_delivery)
            product_lines = order.order_line.filtered(lambda l: not l.is_delivery)

            order.delivery_untaxed = sum(delivery_lines.mapped('price_subtotal'))
            order.amount_untaxed_without_delivery = sum(product_lines.mapped('price_subtotal'))
            order.amount_tax_without_delivery = sum(product_lines.mapped('price_tax'))

    def action_confirm(self):
        # Ejecutar confirmación estándar con sudo
        res = super(SaleOrder, self.sudo()).action_confirm()

        # Plantillas de correo
        confirm_template = self.env.ref("niubiz_payment.email_confirm_sale_order", raise_if_not_found=False)
        pago_template = self.env.ref("niubiz_payment.email_pago_confirm_sale", raise_if_not_found=False)

        entrega = ''
        for order in self:
            items = []
            count = 0
            company = order.company_id
            url_venta = company.url_venta
            token_venta = company.token_venta
            for line in order.order_line:
                if line.product_id.type == 'service':
                    entrega = self.env['delivery.carrier'].sudo().search([('product_id','=', line.product_id.id)], limit=1)
                # Descontar stock (ojo: esto no es buena práctica si usas inventario real)
                if line.product_template_id.stock_product:
                        line.product_template_id.stock_product = line.product_template_id.stock_product - line.product_uom_qty
            
                if line.product_template_id.codigo_sap :    
                    count += 10
                    items.append({
                        "VBELM": order.name,
                        "ITMID": count,
                        "MATNR": line.product_template_id.codigo_sap or '',
                        "KWMENG": line.product_uom_qty or 0,
                        "NETPR": line.price_unit,
                        "WAERK": order.pricelist_id.currency_id.name or ''
                    })
            if entrega :
                _logger.info("DATOS DE ENVÍO A SAP: %s", items)
                url = ''
                ubigeo = self.partner_shipping_id.l10n_pe_district.code
                name1 = self.partner_shipping_id.name
                name2 = self.partner_shipping_id.parent_id.name
                street = self.partner_shipping_id.street
                city = self.partner_shipping_id.city_id.name
                ruc = self.partner_shipping_id.vat
                telf = self.partner_shipping_id.phone
                correo = self.partner_shipping_id.email
                if entrega.tipo_entrega == 'envio' : 
                    url =  f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2=&CORREO={correo}&TELF={telf}&CALLE3={street}&POSTAL=CALLAO 1&CITY1=CALLAO&STCD1={ruc}"
                else :
                    url = f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2=&CORREO={correo}&TELF={telf}&CALLE3={street}&POSTAL=CALLAO 1&CITY1=CALLAO&STCD1={ruc}&TIENDA={entrega.name_sap}"
                payload = json.dumps({
                    "HEADER": {
                        "VBELM": order.name,
                        "WAERK": order.currency_id.name ,
                        "IMPORTE": order.amount_total,
                        "EID": order.id
                    },
                    "ITEM": items
                })
                headers = {
                    'Ocp-Apim-Subscription-Key': f'{token_venta}',
                    'Content-Type': 'application/json',
                    'Cookie': 'sap-usercontext=sap-client=400'
                }

                try:
                    response = requests.post(url, headers=headers, data=payload)
                    response_data = response.json()
                    order.id_sap = response_data.get("RESPUESTA", "")
                    if order.id_sap:
                        order.is_sap_confirm = True
                    _logger.info("Respuesta SAP: %s", response_data)
                except Exception as e:
                    _logger.error("Error al enviar datos a SAP: %s", e)
                    order.id_sap = "ERROR"

                # Crear estado
                self.env["status.sale"].sudo().create({
                    "status_sale": "nuevo",
                    "sale_order": order.id
                })

                # Enviar correos
                if confirm_template:
                    confirm_template.sudo().send_mail(order.id, force_send=True)
                if pago_template:
                    pago_template.sudo().send_mail(order.id, force_send=True)

        return res


    def set_order_sap(self):
        ordenes = self.env["sale.order"].search([("id_sap" "=" "ERROR"), ("no_send_sap", "=", False)])
        if ordenes:
            for order in ordenes:
                items = []
                count = 0
                entrega = ''
                company = order.company_id
                url_venta = company.url_venta
                token_venta = company.token_venta
                ubigeo = order.partner_shipping_id.l10n_pe_district.code
                name1 = order.partner_shipping_id.name
                name2 = order.partner_shipping_id.parent_id.name
                street = order.partner_shipping_id.street
                city = order.partner_shipping_id.city_id.name
                ruc = order.partner_shipping_id.vat

                for line in order.order_line:
                    if line.product_id.type == 'service':
                        entrega = self.env['delivery.carrier'].sudo().search([('product_id','=', line.product_id.id)], limit=1)
                    # Descontar stock (ojo: esto no es buena práctica si usas inventario real)
                    if line.product_template_id.stock_product:
                        line.product_template_id.stock_product = line.product_template_id.stock_product - line.product_uom_qty
                    if line.product_template_id.codigo_sap :    
                        count += 10
                        items.append({
                            "VBELM": order.name,
                            "ITMID": count,
                            "MATNR": line.product_template_id.codigo_sap,
                            "KWMENG": line.product_uom_qty,
                            "NETPR": line.price_unit,
                            "WAERK": order.currency_id.name 
                        })

                _logger.info("DATOS DE ENVÍO A SAP: %s", items)

                url = ''
                if entrega.tipo_entrega == 'envio' : 
                    # url =  f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2={name2}&CORREO={correo}&TELF={telf}&CALLE3={street}&POSTAL=CALLAO 1&CITY1={city}&STCD1={ruc}"
                    url =  f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2=&CORREO={correo}&TELF={telf}&CALLE3={street}&POSTAL=CALLAO 1&CITY1=CALLAO&STCD1={ruc}"
                else :
                    # url = f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2={name2}&CALLE3={street}&POSTAL=CALLAO 1&CITY1={city}&STCD1={ruc}&TIENDA={entrega.name_sap}"
                    url = f"{url_venta}&ZONA={ubigeo}&NAME1={name1}&NAME2=&CORREO={correo}&TELF={telf}&CALLE3={street}&POSTAL=CALLAO 1&CITY1=CALLAO&STCD1={ruc}&TIENDA={entrega.name_sap}"
                payload = json.dumps({
                    "HEADER": {
                        "VBELM": order.name or '',
                        "WAERK": order.pricelist_id.currency_id.name or '',
                        "IMPORTE": order.amount_total or 0.00,
                        "EID": order.id
                    },
                    "ITEM": items
                })
                headers = {
                    'Ocp-Apim-Subscription-Key': f'{token_venta}',
                    'Content-Type': 'application/json',
                    'Cookie': 'sap-usercontext=sap-client=400'
                }

                try:
                    response = requests.post(url, headers=headers, data=payload)
                    response_data = response.json()
                    order.id_sap = response_data.get("RESPUESTA", "")
                    if order.id_sap:
                        order.is_sap_confirm = True
                    _logger.info("Respuesta SAP: %s", response_data)
                except Exception as e:
                    _logger.error("Error al enviar datos a SAP: %s", e)
                    order.id_sap = "ERROR"


    def amount_text (self, numero, moneda):
        parte_entera = int(numero)
        texto_entero = num2words(parte_entera, lang='es').upper()
        text_moneda = ''
        # Obtener la parte decimal
        parte_decimal = round((numero - parte_entera) * 100)
        if moneda == '$' :
            text_moneda = 'DÓLARES AMERICANOS'
        if moneda == 'S/':
            text_moneda = 'SOLES'
        # Crear el texto final con formato de fracción
        texto_final = f"{texto_entero} Y {parte_decimal}/100 {text_moneda}"

        # Mostrar el resultado
        return texto_final
