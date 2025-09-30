from odoo import http
from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
import requests
import logging
import json
import re
_logger = logging.getLogger(__name__)
class WebsiteSaleCustom(WebsiteSale):

    @route()
    def shop_address_submit(
        self, partner_id=None, address_type='billing', use_delivery_as_billing=None,
        callback=None, required_fields=None, **form_data
    ):
        _logger.info("🟢 shop_address_submit ejecutado")

        mercado = form_data.get('mercado')
        ref = form_data.get('ref')
        _logger.info(f"📦 Mercado: {mercado}, Ref: {ref}")

        response = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            **form_data
        )

        order = request.website.sale_get_order()
        partner = order.partner_invoice_id if address_type == 'billing' else order.partner_shipping_id 

        if partner:
            partner.write({
                'mercado': mercado,
                'ref': ref,
            })
            _logger.info("✅ Campos personalizados guardados en el partner.")

        return response

    def _validate_address_values(
        self,
        address_values,
        partner_sudo,
        address_type,
        use_delivery_as_billing,
        required_fields,
        is_main_address,
        **_kwargs,
    ):
        # Copiamos el método original y reemplazamos solo la validación del VAT
        invalid_fields = set()
        missing_fields = set()
        error_messages = []

        # --- Mantener validaciones originales ---
        if partner_sudo:
            name_change = (
                'name' in address_values
                and partner_sudo.name
                and address_values['name'] != partner_sudo.name
            )
            email_change = (
                'email' in address_values
                and partner_sudo.email
                and address_values['email'] != partner_sudo.email
            )

            if name_change and not partner_sudo._can_edit_name():
                invalid_fields.add('name')
                error_messages.append(_(
                    "No se permite cambiar su nombre una vez que se hayan emitido las facturas para su"
                    " Cuenta. Por favor, contáctenos directamente para esta operación."
                ))

            if (name_change or email_change) and not all(partner_sudo.user_ids.mapped('share')):
                if name_change:
                    invalid_fields.add('name')
                if email_change:
                    invalid_fields.add('email')
                error_messages.append(_(
                    "Si desea cambiar datos porfavor de comunicarse con un administrador"
                ))

            if (
                'vat' in address_values
                and address_values['vat'] != partner_sudo.vat
                and not partner_sudo.can_edit_vat()
            ):
                invalid_fields.add('vat')
                error_messages.append(_(
                    "No se permite cambiar el número de IVA una vez que se hayan emitido los documentos para su"
                    " Cuenta. Por favor, contáctenos directamente para esta operación."
                ))

        # --- Email validation ---
        email_pattern = r"[^@]+@[^@]+\.[^@]+"
        if address_values.get('email') and not re.match(email_pattern, address_values['email']):
            invalid_fields.add('email')
            error_messages.append(_("¡Correo electrónico inválido! Ingresa un correo válido."))

        # ✅ REEMPLAZAMOS validación de VAT
        vat = address_values.get("vat")
        tipo_id = address_values.get("l10n_latam_identification_type_id")
        print("VAT:--------------")
        print(vat)
        print("VAT:--------------")
        print(tipo_id)
        if vat and tipo_id:
            if tipo_id == '5' and len(vat) != 8:  # DNI
                invalid_fields.add('vat')
                error_messages.append(_("El número de DNI debe tener 8 dígitos."))
            elif tipo_id == '4' and len(vat) != 11:  # RUC
                invalid_fields.add('vat')
                error_messages.append(_("El número de RUC debe tener 11 dígitos."))

        # --- Mantener validaciones de campos requeridos ---
        required_field_set = {f for f in required_fields.split(',') if f}
        country = request.env['res.country'].browse(address_values.get('country_id'))
        if address_type == 'delivery' or use_delivery_as_billing:
            required_field_set |= self._get_mandatory_delivery_address_fields(country)
        if address_type == 'billing' or use_delivery_as_billing:
            required_field_set |= self._get_mandatory_billing_address_fields(country)
            if not is_main_address:
                commercial_fields = request.env['res.partner'].sudo()._commercial_fields()
                for fname in commercial_fields:
                    if fname in required_field_set and fname not in address_values:
                        required_field_set.remove(fname)

        for field_name in required_field_set:
            if not address_values.get(field_name):
                missing_fields.add(field_name)

        if missing_fields:
            error_messages.append(_("Algunos campos obligatorios están vacíos."))

        return invalid_fields, missing_fields, error_messages

class SunatApiController(http.Controller):

    @http.route('/api/consulta_documento/<string:numero>', type='http', auth='public', csrf=False, methods=['GET'])
    def consulta_documento(self, numero):
        if not numero:
            return request.make_response(
                '{"error": "Número de documento no proporcionado"}',
                headers=[('Content-Type', 'application/json')]
            )

        token_api = request.env.company.token_api
        if not token_api:
            return request.make_response(
                '{"error": "Token API no configurado en la compañía"}',
                headers=[('Content-Type', 'application/json')]
            )

        # Construir la URL
        if len(numero) == 8:
            url = f"https://api.apis.net.pe/v2/reniec/dni?numero={numero}&token={token_api}"
        elif len(numero) == 11:
            url = f"https://api.apis.net.pe/v2/sunat/ruc?numero={numero}&token={token_api}"
        else:
            return request.make_response(
                '{"error": "Número de documento inválido"}',
                headers=[('Content-Type', 'application/json')]
            )

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if 'digitoVerificador' in data:
                del data['digitoVerificador']

            return request.make_response(
                json.dumps(data, ensure_ascii=False),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error consultando documento {numero}: {e}")
            return request.make_response(
                '{"error": "No se pudo consultar el documento"}',
                headers=[('Content-Type', 'application/json')]
            )


    @http.route('/document/types', type='http', auth='public', csrf=False)
    def get_identification_types(self):
        types = request.env['l10n_latam.identification.type'].sudo().search([('name', 'in', ['DNI', 'RUC'])])
        return request.make_response(
            json.dumps([{'id': t.id, 'name': t.name} for t in types]),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/get/provincias', type='http', auth='public', csrf=False)
    def get_provincias(self, **kwargs):
        data = json.loads(request.httprequest.data)
        state_id = data.get('state_id')
        cities = request.env['res.city'].sudo().search([('state_id', '=', int(state_id))])
        return request.make_response(
            json.dumps([{'id': c.id, 'name': c.name} for c in cities]),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/get/distritos', type='http', auth='public', csrf=False)
    def get_distritos(self, **kwargs):
        data = json.loads(request.httprequest.data)
        city_id = data.get('city_id')
        distritos = request.env['l10n_pe.res.city.district'].sudo().search([('city_id', '=', int(city_id))])
        return request.make_response(
            json.dumps([{'id': d.id, 'name': d.name} for d in distritos]),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/get_zip_from_district', type='json', auth='public', csrf=False)
    def get_zip_from_district(self):
        data = request.jsonrequest
        district_id = data.get('district_id')
        district = request.env['l10n_pe.res.city.district'].sudo().browse(int(district_id))
        return {"zip": district.code or ""}


class CustomPortalDetails(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        return values


    @http.route(['/my/account'], type='http', auth="user", website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if post and request.httprequest.method == 'POST':
            error, error_message = {}, []

            # Validaciones básicas
            name = post.get('name', '').strip()
            email = post.get('email', '').strip()

            if not name:
                error['name'] = 'missing'
                error_message.append("El nombre es obligatorio.")
            if not email:
                error['email'] = 'missing'
                error_message.append("El correo electrónico es obligatorio.")

            if not error:
                partner_vals = {
                    'name': name,
                    'email': email,
                    'phone': post.get('phone', '').strip(),
                    'vat': post.get('vat', '').strip(),
                    'company_name': post.get('company_name', '').strip(),
                    'street': post.get('street', '').strip(),
                    'street2': post.get('street2', '').strip(),
                    'zip': post.get('zipcode', '').strip(),
                    'country_id': int(post['country_id']) if post.get('country_id') else False,
                    'state_id': int(post['state_id']) if post.get('state_id') else False,
                    'city_id': int(post['city_id']) if post.get('city_id') else False,
                    'l10n_pe_district': int(post['l10n_pe_district']) if post.get('l10n_pe_district') else False,
                    'mercado': post.get('mercado', '').strip() if post.get('mercado') else False,
                    'l10n_latam_identification_type_id': int(post.get('l10n_latam_identification_type_id')) if post.get('l10n_latam_identification_type_id') else False,
                }

                partner.sudo().write(partner_vals)
                return request.redirect('/my/account')

            # Si hay errores, mostrar formulario nuevamente
            values.update({
                'error': error,
                'error_message': error_message,
                'partner': partner,
                'name': name,
                'email': email,
                'phone': post.get('phone'),
                'vat': post.get('vat'),
                'company_name': post.get('company_name'),
                'street': post.get('street'),
                'street2': post.get('street2'),
                'zipcode': post.get('zipcode'),
                'country_id': int(post['country_id']) if post.get('country_id') else False,
                'state_id': int(post['state_id']) if post.get('state_id') else False,
                'city_id': int(post['city_id']) if post.get('city_id') else False,
                'l10n_pe_district': int(post['l10n_pe_district']) if post.get('l10n_pe_district') else False,
                'mercado': post.get('mercado'),
                'identification_type_id': int(post.get('l10n_latam_identification_type_id')) if post.get('l10n_latam_identification_type_id') else False,
                'countries': request.env['res.country'].sudo().search([]),
                'states': request.env['res.country.state'].sudo().search([]),
                'cities': request.env['res.city'].sudo().search([('state_id', '=', int(post.get('state_id', 0)))]) if post.get('state_id') else [],
                'districts': request.env['l10n_pe.res.city.district'].sudo().search([('city_id', '=', int(post.get('city_id', 0)))]) if post.get('city_id') else [],
                'partner_can_edit_vat': partner.can_edit_vat(),
            })
            return request.render("portal.portal_my_details", values)

        # Render inicial GET
        state_id = partner.state_id.id
        city_id = partner.city_id.id

        values.update({
            'partner': partner,
            'identification_type_id': partner.l10n_latam_identification_type_id.id,
            'countries': request.env['res.country'].sudo().search([]),
            'states': request.env['res.country.state'].sudo().search([]),
            'cities': request.env['res.city'].sudo().search([('state_id', '=', state_id)]) if state_id else [],
            'districts': request.env['l10n_pe.res.city.district'].sudo().search([('city_id', '=', city_id)]) if city_id else [],
            'partner_can_edit_vat': partner.can_edit_vat(),
            'name': partner.name,
            'email': partner.email,
            'phone': partner.phone,
            'vat': partner.vat,
            'company_name': partner.commercial_company_name,
            'street': partner.street,
            'street2': partner.street2,
            'zipcode': partner.zip,
            'country_id': partner.country_id.id,
            'state_id': state_id,
            'city_id': city_id,
            'l10n_pe_district': partner.l10n_pe_district.id,
            'mercado': partner.mercado,
            'identification_types': request.env['l10n_latam.identification.type'].sudo().search([
                ('country_id.code', '=', 'PE')
            ]),
            'error': {},
            'error_message': [],
        })

        return request.render("portal.portal_my_details", values)
