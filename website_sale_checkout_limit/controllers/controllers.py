# -*- coding: utf-8 -*-
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo import http
from odoo.http import request, route
import logging
import requests
_logger = logging.getLogger(__name__)


class WebsiteSaleExtended(WebsiteSale):
    @http.route()
    def cart_update_json(self, *args, set_qty=None, **kwargs):
        result = super().cart_update_json(*args, set_qty=set_qty, **kwargs)

        is_min = request.website.check_cart_amount()
        result['website_sale.check'] = is_min
        return result

    @route('/shop/checkout', type='http', methods=['GET'], auth='public', website=True, sitemap=False)
    def shop_checkout(self, try_skip_step=None, **query_params):
        _logger.info("Checking cart amount before checkout")
        is_min = request.website.check_cart_amount()
        _logger.info(f"Cart amount check result: {is_min}")
        if is_min:
            _logger.info("Cart amount is sufficient, proceeding to checkout")
            return super(WebsiteSaleExtended, self).shop_checkout(try_skip_step=try_skip_step, **query_params)
        _logger.info("Cart amount is insufficient, redirecting to confirmation page")
        # Obtener la orden actual (carrito activo)
        order = request.website.sale_get_order()
        if order:
            city_name = order.partner_shipping_id.city_id.name.strip() if order.partner_shipping_id.city_id else ''
            if city_name and city_name.lower() != 'lima':
                _logger.info("District is not Lima, marking order as no_send_sap")
                order.write({'no_send_sap': True, 'state': 'draft'})
                return request.redirect("/confirmacion-control-de-distrito")
            # Marcar la orden para no enviar a SAP
            order.no_send_sap = True
            _logger.info("Order marked as no_send_sap")
            order.write({'no_send_sap': True, 'state': 'draft'})
        return request.redirect("/confirmacion-control-de-compras-anuales")
        #return request.redirect("/shop/cart")

    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        _logger.info("Checking cart amount before payment")
        _logger.info("Starting Gesintel validation for the order 2")
        is_min = request.website.check_cart_amount()
        _logger.info(f"Cart amount check result: {is_min}")

        #Validacion Gesintel
        #  
        _logger.info("Starting Gesintel validation for the order 1")
        ircsudo = request.env['ir.config_parameter'].sudo()
        gesintel_ambiente_produccion = ircsudo.get_param('gesintel_ambiente_produccion')
        gesintel_token_prd = ircsudo.get_param('gesintel_token_prd')
        gesintel_token_qas = ircsudo.get_param('gesintel_token_qas')
        gesintel_url_prd = ircsudo.get_param('gesintel_url_prd')
        gesintel_url_qas = ircsudo.get_param('gesintel_url_qas')
        gesintel_url = gesintel_url_prd if gesintel_ambiente_produccion == True else gesintel_url_qas
        gesintel_token = gesintel_token_prd if gesintel_ambiente_produccion == True else gesintel_token_qas
        if not gesintel_token or not gesintel_url:
            _logger.error("Gesintel configuration is missing. Cannot proceed with checkout.")
        
        
        # Construir la URL pasando los parámetros rut y dni
        
        #headers = {
        #    'Content-Type': 'application/json',
        #    'Authorization': f'Bearer {gesintel_token}'
        #}

        payload = {}
        headers = {
        'Authorization': gesintel_token
        }
        url = f"{gesintel_url}/mvc/rest/AMLUpdate"
        if order:
            rut = order.partner_id.vat if order.partner_id else ""
            name = order.partner_id.name if hasattr(order.partner_id, 'name') else ""
            distrito = order.partner_id.city_id.name if hasattr(order.partner_id, 'state_id') else ""
            ciudad = order.partner_id.city if hasattr(order.partner_id, 'city') else ""
            distrito_order = order.partner_shipping_id.city_id.name if hasattr(order.partner_id, 'state_id') else ""
            _logger.info(f"Order partner details: RUT={rut}, Name={name}, District={distrito}, City={ciudad}")

            url = f"{gesintel_url}/mvc/rest/getAMLResult?rut={rut}&name={name}"
            _logger.info(f"Requesting Gesintel URL: {url} with headers: {headers}")
            response = requests.request("GET", url, headers=headers, data=payload)
            _logger.info(f"Gesintel response: {response.text}")
            data = response.json()  # ✅ Convierte la respuesta en dict
            results = data.get("results", {})

            tiene_alerta, fuente = WebsiteSaleExtended.check_risk_flags(results)
            _logger.info(f"Risk check result: {tiene_alerta}, source: {fuente}")
            if tiene_alerta:
                _logger.info(fuente)
                print("FUENTE GENSITEL: " + fuente)
                order.write({'no_send_sap': True, 'alert_gesintel': True, 'message_gesintel': fuente + ' Detalle de Respuesta : '+ str(response.text),'state': 'draft'})
                _logger.warning(f"Alert detected from source: {fuente}. Redirecting to confirmation page.")
                # Redirigir a la página de confirmación
                return request.redirect("/confirmacion-control-de-compras-anuales")
            
            if distrito_order != 'Lima':
                _logger.info("District is not Lima, marking order as no_send_sap")
                order.write({'no_send_sap': True, 'state': 'draft'})
                return request.redirect("/confirmacion-control-de-distrito")


        if is_min:
            _logger.info("Cart amount is sufficient, proceeding to payment")
            return super(WebsiteSaleExtended, self).shop_payment(**post)
        _logger.info("Cart amount is insufficient, redirecting to confirmation page")
        return request.redirect("/confirmacion-control-de-compras-anuales")
    
    
    def check_risk_flags(results):
        """
        Revisa la respuesta del servicio AMLUpdate y devuelve True si hay alguna alerta/riesgo.
        """
        alert_keys = [
            "pepResults",
            "pepHResults",
            "pepCResults",
            "fpResults",
            "pjudResults",
            "personResults",
            "djResults",
            "negativeResults",
            "vipResults",
            "pepRelacionados",
            "pepHRelacionados",
        ]

        for key in alert_keys:
            value = results.get(key)
            if isinstance(value, list) and value:
                return True, key  # Hay riesgo en una lista
            elif isinstance(value, dict) and value:
                return True, key  # Hay riesgo en un objeto
            elif value not in [None, [], {}, ""]:
                return True, key  # Otro valor no vacío (ej. booleano True)

        return False, None
