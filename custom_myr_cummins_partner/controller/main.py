from odoo import http
from odoo.http import request, Response
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleCustom(WebsiteSale):

    @http.route(
        '/shop/address/submit', type='http', methods=['POST'], auth='public', website=True,
        sitemap=False
    )
    def shop_address_submit(
        self, partner_id=None, address_type='billing', use_delivery_as_billing=None, callback=None,
        required_fields=None, **form_data
    ):
        # ✅ Si NO es usuario público, ejecutar método original de Odoo
        if request.env.user != request.website.user_id:
            return super().shop_address_submit(
                partner_id=partner_id,
                address_type=address_type,
                use_delivery_as_billing=use_delivery_as_billing,
                callback=callback,
                required_fields=required_fields,
                **form_data
            )

        # ✅ Verifica si está en la URL correcta y tipo de dirección "delivery"
        path = request.httprequest.path
        if not (path.endswith("/shop/address/submit") and address_type == "billing"):
            return super().shop_address_submit(
                partner_id=partner_id,
                address_type=address_type,
                use_delivery_as_billing=use_delivery_as_billing,
                callback=callback,
                required_fields=required_fields,
                **form_data
            )

        # 🛒 Lógica personalizada para visitante con validación de distrito
        order_sudo = request.website.sale_get_order()
        if order_sudo:
            city_id = form_data.get('city_id')
            city_name = ""
            if city_id:
                try:
                    city = request.env['res.city'].sudo().browse(int(city_id))
                    city_name = city.name.strip() if city.exists() else ""
                except Exception as e:
                    _logger.warning(f"⚠️ Error al obtener ciudad: {e}")

            _logger.info(f"🌍 Ciudad seleccionada: {city_name}")

            if city_name and city_name.lower() != 'lima':
                _logger.info("⚠️ Ciudad no es Lima, marcando orden como no_send_sap")
                order_sudo.sudo().write({
                    'no_send_sap': True,
                    'state': 'draft'
                })

                return Response(
                    json.dumps({'redirectUrl': "/confirmacion-control-de-distrito"}),
                    content_type='application/json',
                    status=200
                )

        if redirection := self._check_cart(order_sudo):
            return redirection

        partner_sudo, address_type = self._prepare_address_update(
            order_sudo, partner_id=partner_id and int(partner_id), address_type=address_type
        )

        use_delivery_as_billing = use_delivery_as_billing in ('true', 'True', True)
        required_fields = required_fields or ''
        address_values, extra_form_data = self._parse_form_data(form_data)

        is_anonymous_cart = order_sudo._is_anonymous_cart()
        is_main_address = is_anonymous_cart or (
            partner_sudo and order_sudo.partner_id.id == partner_sudo.id
        )

        invalid_fields, missing_fields, error_messages = self._validate_address_values(
            address_values,
            partner_sudo,
            address_type,
            use_delivery_as_billing,
            required_fields,
            is_main_address=is_main_address,
            **extra_form_data,
        )
        if error_messages:
            return Response(
                json.dumps({
                    'invalid_fields': list(invalid_fields | missing_fields),
                    'messages': error_messages,
                }),
                content_type='application/json',
                status=400,
            )

        is_new_address = False
        if not partner_sudo:
            is_new_address = True
            self._complete_address_values(address_values, address_type, use_delivery_as_billing, order_sudo)

            create_context = request.env.context.copy()
            create_context.update({
                'tracking_disable': True,
                'no_vat_validation': True,
            })

            vat = address_values.get('vat')
            existing_partner = None
            if vat:
                existing_partner = request.env['res.partner'].sudo().search([('vat', '=', vat)], limit=1)

            if existing_partner:
                # ⚠️ Evitar jerarquía recursiva
                if address_values.get("parent_id") and int(address_values["parent_id"]) == existing_partner.id:
                    address_values.pop("parent_id")
                existing_partner.write(address_values)
                partner_sudo = existing_partner
                is_new_address = False
            else:
                if address_values.get("parent_id"):
                    address_values.pop("parent_id")
                partner_sudo = request.env['res.partner'].sudo().with_context(create_context).create(address_values)

        elif not self._are_same_addresses(address_values, partner_sudo):
            if address_values.get("parent_id") and int(address_values["parent_id"]) == partner_sudo.id:
                address_values.pop("parent_id")
            partner_sudo.write(address_values)

        partner_fnames = set()
        if is_main_address:
            partner_fnames.add('partner_id')

        if address_type == 'billing':
            partner_fnames.add('partner_invoice_id')
            if is_new_address and order_sudo.only_services:
                partner_fnames.add('partner_shipping_id')
            callback = callback or self._get_extra_billing_info_route(order_sudo)
        elif address_type == 'delivery':
            partner_fnames.add('partner_shipping_id')
            if use_delivery_as_billing:
                partner_fnames.add('partner_invoice_id')

        order_sudo._update_address(partner_sudo.id, partner_fnames)

        if is_anonymous_cart:
            order_sudo.message_unsubscribe(order_sudo.website_id.partner_id.ids)

        if is_new_address or order_sudo.only_services:
            callback = callback or '/shop/checkout?try_skip_step=true'
        else:
            callback = callback or '/shop/checkout'

        self._handle_extra_form_data(extra_form_data, address_values)

        return Response(
            json.dumps({'redirectUrl': callback}),
            content_type='application/json',
            status=200,
        )
