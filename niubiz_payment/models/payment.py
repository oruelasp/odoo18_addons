# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import requests
import werkzeug
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime
from odoo import api, fields, models, _
from odoo.http import request
from odoo.addons.payment.models.payment_provider import ValidationError
import json
import pprint

_logger = logging.getLogger(__name__)
ENV = {
    'test': {
        'security_token': 'https://apisandbox.vnforappstest.com/api.security/v1/security',
        'session_token': 'https://apisandbox.vnforappstest.com/api.ecommerce/v2/ecommerce/token/session/{merchantId}',
        'transaction': 'https://apisandbox.vnforappstest.com/api.authorization/v3/authorization/ecommerce/{merchantId}',
        'reverse': 'https://apisandbox.vnforappstest.com/api.authorization/v3/reverse/ecommerce/{merchantId}',
        'confirm': 'https://apisandbox.vnforappstest.com/api.confirmation/v1/confirmation/ecommerce/{merchantId}',
        'checkout_form': 'https://static-content-qas.vnforapps.com/v2/js/checkout.js?qa=true',
    },
    'enabled': {
        'security_token': 'https://apiprod.vnforapps.com/api.security/v1/security',
        'session_token': 'https://apiprod.vnforapps.com/api.ecommerce/v2/ecommerce/token/session/{merchantId}',
        'transaction': 'https://apiprod.vnforapps.com/api.authorization/v3/authorization/ecommerce/{merchantId}',
        'reverse': 'https://apiprod.vnforapps.com/api.authorization/v3/reverse/ecommerce/{merchantId}',
        'confirm': 'https://apiprod.vnforapps.com/api.confirmation/v1/confirmation/ecommerce/{merchantId}',
        'checkout_form': 'https://static-content.vnforapps.com/v2/js/checkout.js',
    }
}


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[
        ('niubiz', 'Niubiz')
    ], ondelete={'niubiz': 'set default'})

    _description = 'Niubiz Payment Provider'
    niubiz_merchant_id = fields.Char(string='Merchant ID - Moneda Principal', required_if_provider='niubiz', groups='base.group_user')
    niubiz_username = fields.Char(string='User - Moneda Principal', required_if_provider='niubiz', groups='base.group_user')
    niubiz_password = fields.Char(string='Password - Moneda Principal', required_if_provider='niubiz', groups='base.group_user')

    niubiz_merchant_id_secondary_currency = fields.Char(string='Merchant ID - Moneda Secundaria', required_if_provider='niubiz', groups='base.group_user')
    niubiz_username_secondary_currency = fields.Char(string='User  - Moneda Secundaria', required_if_provider='niubiz', groups='base.group_user')
    niubiz_password_secondary_currency = fields.Char(string='Password  - Moneda Secundaria', required_if_provider='niubiz', groups='base.group_user')

    niubiz_countable = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Automático'),
    ], string='Tipo de validación', default='auto', required_if_provider='niubiz', groups='base.group_user')
    niubiz_channel = fields.Selection([
        ('web', 'Web'),
        ('recurrent', 'Recurrente'),
        ('callcenter', 'Call center'),
    ], 'Canal', required_if_provider='niubiz', default='web', groups='base.group_user')
    # niubiz_merchantlogo = fields.Char(string='Niubiz_merchantlogo', required=False)

    def _niubiz_get_security_token(self):
        username = self.niubiz_username
        password = self.niubiz_password
        currency_id = 1 # Asumimos 1 = USD, 156 = PEN

        # 1. Detectar desde payment.transaction si está en contexto
        if self._context.get('active_model') == 'payment.transaction':
            tx = self.env['payment.transaction'].browse(self._context.get('active_id'))
            if tx and tx.sale_order_ids:
                currency_id = tx.sale_order_ids.currency_id.id

        # 2. Alternativa: desde sale.order directamente
        elif self._context.get('active_model') == 'sale.order':
            order = self.env['sale.order'].browse(self._context.get('active_id'))
            currency_id = order.currency_id.id if order else None

        # 3. Lógica por defecto
        if currency_id and currency_id != 1:  # Asumimos 1 = USD, 156 = PEN
            username = self.niubiz_username_secondary_currency
            password = self.niubiz_password_secondary_currency
        
            

        auth = HTTPBasicAuth(username, password)
        token_response = requests.post(ENV[self.state]['security_token'], auth=auth)
        _logger.info('TOKEN 1111111111111 ' + token_response.text)
        if token_response.status_code == 401:
            raise ValidationError(_("Acceso no autorizado"))
        return token_response.text


    def _niubiz_get_session_token(self, values, security_token):
        payment_acquirer = self.env.ref('niubiz_payment.payment_provider_niubiz')
        merchant_define_data = {}

        if values.get('partner_email'):
            merchant_define_data['MDD4'] = values.get('partner_email')
        if values.get('billing_partner_id'):
            merchant_define_data['MDD32'] = values.get('billing_partner_id')

        partner_id = values.get("partner_id")
        partner = self.env['res.partner'].browse(partner_id)

        # Cliente frecuente
        # 0 o 1
        merchant_define_data['MDD21'] = partner.get_total_sale_orders(partner.id)

        if len(partner.user_ids) > 0:
            merchant_define_data['MDD75'] = "Registrado"
            user_id = partner.user_ids[0]
            created_date = user_id.create_date
            today = datetime.today()
            merchant_define_data['MDD77'] = abs((today - created_date).days)
        else:
            merchant_define_data['MDD75'] = "Invitado"
            merchant_define_data['MDD77'] = 0

        ip_address = request.httprequest.environ['REMOTE_ADDR']

        session_request = {
            "amount": values['amount'],
            "antifraud": {
                "clientIp": ip_address,
                "merchantDefineData": merchant_define_data
            },
            "channel": payment_acquirer.niubiz_channel
        }

        session_header = {
            'Content-Type': 'application/json',
            'Authorization': security_token
        }
        _logger.info('SESSION SELF x1 : %s', values)
        currency_id = values.get("currency_id")
        x_niubiz_merchant = self.niubiz_merchant_id
        if currency_id != 1:
            _logger.info('TOKEN MONEDA SECUNDARIA SOLES 156 : %s', currency_id)
            x_niubiz_merchant = self.niubiz_merchant_id_secondary_currency
        else:
            _logger.info('TOKEN MONEDA PRIMARIA USD 1 : %s', currency_id)
            

        session_response = requests.post(ENV[self.state]['session_token'].format(merchantId=x_niubiz_merchant),
                                         json=session_request, headers=session_header)
        if session_response.status_code == 401:
            raise ValidationError(_("Acceso no autorizado"))
        json = session_response.json()
        _logger.info('SESSION TOKEN: %s', json)
        return json

    def niubiz_form_generate_values(self, values):
        _logger.info('SESSION GENERATE VALUES SELF: %s', self)

        currency_id = values.get("currency_id")
        x_niubiz_merchant = self.niubiz_merchant_id
        if currency_id != 1:
            _logger.info('TOKEN MONEDA SECUNDARIA SOLES 156 : %s', currency_id)
            x_niubiz_merchant = self.niubiz_merchant_id_secondary_currency
        else:
            _logger.info('TOKEN MONEDA PRIMARIA USD 1 : %s', currency_id)

        self.ensure_one()

        payment_acquirer = self.env['payment.provider'].sudo().search([('provider', '=', 'niubiz')], limit=1)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        security_token = self._niubiz_get_security_token()
        _logger.info("SECURITY TOKEN:" + security_token)
        amount = float(values.get('amount'))
        values.update({
            'amount': amount
        })
        session_token = self._niubiz_get_session_token(values, security_token)
        order_sequence = self.env.ref('niubiz_payment.niubiz_order_seq').next_by_id()
        tx = values["reference"].replace("/", "_")
        checkout_url = werkzeug.urls.url_join(base_url, ENV[self.state]['checkout_form'])
        timeout_url = werkzeug.urls.url_join(base_url, '/payment/niubiz/timeout')
        action_url = werkzeug.urls.url_join(base_url, f'/payment/niubiz/capture/{tx}/{order_sequence}')
        values.update({
            'checkout_form': checkout_url,
            'timeout_url': timeout_url,
            'action_url': action_url,
            'session_token': session_token['sessionKey'],
            'merchant_id': x_niubiz_merchant,
            'amount': values.get('amount'),
            'order_sequence': order_sequence,
            'payment_state': payment_acquirer.state
            # 'reference': order_sequence,
            # 'name': values.get('partner_name'),
            # 'contact': values.get('partner_phone'),
            # 'email': values.get('partner_email'),
            # 'order_id': values.get('reference'),
        })
        return values


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    niubiz_purchase_number = fields.Char('Purchase number')
    niubiz_response_name = fields.Char('Nombre de response', readonly=True, default='response.json')
    niubiz_response = fields.Binary('Niubiz response')
    niubiz_status_cancelled = fields.Boolean('Niubiz estado de cancelacion')
    niubiz_status_cancelled_msg = fields.Char('Niubiz mensaje cancelación')
    niubiz_response_cancelled = fields.Binary('Niubiz response cancelled')
    niubiz_status_confirm = fields.Boolean('Niubiz estado de confirmación')
    niubiz_status_confirm_msg = fields.Char('Niubiz mensaje confirmación')
    niubiz_response_confirm = fields.Binary('Niubiz response confirmación')
    niubiz_session_token = fields.Char("Niubiz Session Token")
    niubiz_action_url = fields.Char()
    niubiz_timeout_url = fields.Char()
    niubiz_checkout_form = fields.Char()
    niubiz_order_sequence = fields.Char()
    niubiz_merchant_id = fields.Char()
    niubiz_amount = fields.Float()


    @classmethod
    def _get_tx_from_feedback_data(cls, provider_code, data):
        tx = super()._get_tx_from_feedback_data(provider_code, data)
        if provider_code == 'niubiz':
            tx.operation = 'validation'
        return tx

    @api.model
    def _create_niubiz_capture(self, data):
        _logger.info("➡️ Captura Niubiz Payload CAPTURE: %s", data)
        payment_provider = self.env['payment.provider'].sudo().search([('code', '=', 'niubiz')], limit=1)
        security_token = payment_provider._niubiz_get_security_token()
        tx_url = ENV[payment_provider.state]['transaction']

        transaction = self.search([('reference', '=', data['reference'])], limit=1)
        order = transaction.sale_order_ids
        purchase_number = data['purchase_number']

        tx_request = {
            "captureType": 'manual',
            "channel": payment_provider.niubiz_channel,
            "countable": payment_provider.niubiz_countable == 'auto',
            "order": {
                "amount": order.amount_total,
                "currency": order.currency_id.name,
                "purchaseNumber": purchase_number,
                "tokenId": data['transactionToken'],
            },
        }

        _logger.info("➡️ Captura Niubiz Payload: %s", tx_request)

        x_niubiz_merchant = payment_provider.niubiz_merchant_id
        if order.currency_id.id != 1:
            _logger.info('TOKEN MONEDA SECUNDARIA B SOLES 156 : %s', order.currency_id.id)
            x_niubiz_merchant = payment_provider.niubiz_merchant_id_secondary_currency
        else:
            _logger.info('TOKEN MONEDA PRIMARIA B USD 1 : %s', order.currency_id.id)


        tx_response = requests.post(
            tx_url.format(merchantId=x_niubiz_merchant),
            json=tx_request,
            headers={'Authorization': security_token}
        )
        _logger.info("➡️ Captura RESPUESTA NIUBIZ: %s", tx_response.json())
        if tx_response.status_code == 200:
            tx_response_json = tx_response.json()
            encoded_response = base64.b64encode(tx_response.content)

            niubiz_transaction = base64.b64encode(tx_response.content)
            niubiz_amount = order.amount_total,

            transaction.write({
                'niubiz_purchase_number': purchase_number,
                'niubiz_response': encoded_response,
            })

            order.write({
                "is_niubiz": True,
                "niubiz_transaction_msg": tx_response_json['dataMap']['TRANSACTION_ID'],
                "niubiz_transaction": niubiz_transaction,
                "niubiz_countable": tx_response_json.get('fulfillment', {}).get('countable'),
                "niubiz_amount": tx_response_json.get('dataMap', {}).get('AMOUNT'),
                "niubiz_confirm": tx_response_json['dataMap']['ACTION_DESCRIPTION'],
                "numero_tarjeta": tx_response_json['dataMap']['CARD'],
                "tipo_tarjeta": tx_response_json['dataMap']['BRAND'],
            })

            if order.state in ['draft', 'sent']:
                order.action_confirm()
            return {
                'status': 'authorized',
                'purchase_number': purchase_number,
                'reference': data['reference'],
                'amount': order.amount_total,
            }

        else:
            try:
                error_response = tx_response.text
                response_json = json.loads(error_response)
                description_transc = response_json.get('data', {}).get('ACTION_DESCRIPTION') or response_json.get('errorMessage', 'Error desconocido')
                eci_description = response_json.get('data', {}).get('ECI_DESCRIPTION')

                order.write({
                    "is_niubiz": False,
                    "niubiz_transaction_msg": eci_description or "Sin detalle",
                    "niubiz_cancel": description_transc or "Rechazado",
                })

                error_response = tx_response.text
                transaction.write({
                    'niubiz_purchase_number': purchase_number,
                    'niubiz_response': base64.b64encode(error_response.encode('utf-8')),
                })
                description = response_json.get('data', {}).get('ACTION_DESCRIPTION') or response_json.get('errorMessage', 'Error desconocido')
            except Exception as e:
                _logger.error("Error parsing Niubiz response: %s", e)
                description = "Error desconocido"

            return {
                'status': 'denied',
                'purchase_number': purchase_number,
                'reference': data['reference'],
                'description': description,
                'amount': order.amount_total,
            }


    @api.model
    def _niubiz_form_get_tx_from_data(self, data):
        reference, txn_id = data.get('reference'), data.get('purchase_number')
        if not reference or not txn_id:
            error_msg = _('Niubiz: no se recibio datos para las variables reference (%s) or txn_id (%s)') % (
                reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = _('Niubiz: datos de la referencia %s') % (reference)
            if not txs:
                error_msg += '; no se encontro orden'
            else:
                error_msg += '; multiples ordenes encontradas.'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _niubiz_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        # if float_compare(data.get('amount', 0.0), self.amount, precision_digits=2) != 0:
        #    invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))

        return invalid_parameters


    def _niubiz_form_validate(self, data):
        status = data.get('status')
        if status == 'captured':
            _logger.info('Validated Niubiz payment for tx %s: set as done' % (self.reference))
            self.write({'provider_reference': data.get('reference')})
            self._set_transaction_done()
            return True
        if status == 'authorized':
            _logger.info('Validated Niubiz payment for tx %s: set as authorized' % (self.reference))
            self.write({'provider_reference': data.get('reference')})
            self._set_transaction_done()
            return True
        if status == 'denied':
            self.write({'provider_reference': data.get('reference')})
            self._set_transaction_error("Error al procesar el pago.")
            return True
        else:
            error = 'Received unrecognized status for Niubiz payment %s: %s, set as canceled' % (self.reference, status)
            _logger.info(error)
            self.write({
                'provider_reference': data.get('reference'),
                'state_message': data.get('error', 'Error desconocido')
            })
            self._set_transaction_cancel()
            return False


    def niubiz_reverse_order(self):
        _logger.info("➡️ Captura Niubiz REVERSE ORDER: %s", self)
        self.ensure_one()
        payment_acquirer = self.env['payment.acquirer'].sudo().search([('provider', '=', 'niubiz')], limit=1)
        if payment_acquirer.niubiz_countable == 'auto' or self.niubiz_status_cancelled:
            return True

        days = abs((datetime.today() - self.create_date).days)
        if days > 7:
            self.write({
                'niubiz_status_cancelled_msg': f"Se superó la cantidad de días para "
                                               f"confirmar este pedido. {days} ",
                'niubiz_status_cancelled': False
            })
            raise ValidationError(_(f"Se superó la cantidad de días para "
                                    f"cancelar este pedido. {days} "))

        response = base64.b64decode(self.niubiz_response)
        niubiz_response = json.loads(response)
        if "dataMap" not in niubiz_response:
            self.write({
                'niubiz_status_cancelled_msg': "La operacion fue rechazada, no se pudo anular.",
                'niubiz_status_cancelled': False
            })
            return False

        url = ENV[payment_acquirer.state]['reverse']
        if self.niubiz_purchase_number:
            purchase_number = self.niubiz_purchase_number
        else:
            purchase_number = niubiz_response.get("order").get("purchaseNumber")

        security_token = payment_acquirer._niubiz_get_security_token()
        cancelled_json = {
            "order": {
                "purchaseNumber": purchase_number,
                "transactionDate": niubiz_response.get("dataMap").get("TRANSACTION_DATE")
            }
        }
        session_header = {
            'Content-Type': 'application/json',
            'Authorization': security_token
        }

        x_niubiz_merchant = niubiz_response.get("fulfillment").get("merchantId")

        response = requests.post(url.format(merchantId=x_niubiz_merchant),
                                 json=cancelled_json, headers=session_header)
        if response.status_code == 200:
            response_json = response.json()
            self.write({
                'niubiz_status_cancelled_msg': response_json.get("dataMap").get("STATUS"),
                'niubiz_status_cancelled': True,
                'niubiz_response_cancelled': base64.b64encode(response.content)
            })
            return True
        else:
            response_json = json.loads(response.text)
            self.write({
                'niubiz_status_cancelled_msg': response_json.get("errorMessage"),
                'niubiz_status_cancelled': False,
                'niubiz_response_cancelled': base64.b64encode(response.text.encode('utf-8'))
            })
            return False

    def niubiz_confirm_order(self, values, only_validate=False):
        _logger.info("➡️ Captura CONFIRME ORDER: %s", values)
        self.ensure_one()
        payment_acquirer = self.env['payment.acquirer'].sudo().search([('provider', '=', 'niubiz')], limit=1)
        if payment_acquirer.niubiz_countable == 'auto':
            return True

        if self.niubiz_status_confirm:
            raise ValidationError(_("Esta operación ya fue confirmada anteriormente."))

        response = base64.b64decode(self.niubiz_response)
        niubiz_response = json.loads(response)

        current_amount = values.get("current_amount")
        new_amount = values.get("new_amount")

        url = ENV[payment_acquirer.state]['confirm']
        if self.niubiz_purchase_number:
            purchase_number = self.niubiz_purchase_number
        else:
            purchase_number = niubiz_response.get("order").get("purchaseNumber")

        security_token = payment_acquirer._niubiz_get_security_token()
        confirm_json = {
            "channel": "web",
            "captureType": 'manual',
            "order": {
                "purchaseNumber": purchase_number,
                "amount": current_amount,
                "authorizedAmount": float("%.2f" % float(new_amount)),
                "currency": niubiz_response.get("order").get("currency"),
                "transactionId": niubiz_response.get("order").get("transactionId")
            },
        }
        session_header = {
            'Content-Type': 'application/json',
            'Authorization': security_token
        }
        _logger.info(confirm_json)

        currency_code = niubiz_response.get("order").get("currency")
        x_niubiz_merchant = payment_acquirer.niubiz_merchant_id
        if currency_code == 'PEN':
            _logger.info('TOKEN MONEDA SECUNDARIA SOLES 156 : %s', currency_code)
            x_niubiz_merchant = payment_acquirer.niubiz_merchant_id_secondary_currency
        else:
            _logger.info('TOKEN MONEDA PRIMARIA USD 1 : %s', currency_code)

        response = requests.post(url.format(merchantId=x_niubiz_merchant),
                                 json=confirm_json, headers=session_header)
        if response.status_code == 200:
            response_json = response.json()
            _logger.info(response_json)
            self.write({
                'niubiz_status_confirm_msg': response_json.get("dataMap").get("ACTION_DESCRIPTION"),
                'niubiz_status_confirm': True,
                'niubiz_response_confirm': base64.b64encode(response.content)
            })
            return True
        else:
            response_json = json.loads(response.text)
            _logger.info(response.text)
            error = response_json.get("errorMessage")
            if error == "Not Authorized":
                raise ValidationError(_(error))

            self.write({
                'niubiz_status_confirm_msg': error,
                'niubiz_status_confirm': False,
                'niubiz_response_confirm': base64.b64encode(response.text.encode('utf-8'))
            })
            return False

    def _get_processing_values(self):
        _logger.info("➡️ Captura PROCESSING VALUES: %s", self)

        currency_id = self.currency_id.id
        x_niubiz_merchant = self.provider_id.niubiz_merchant_id
        if currency_id != 1:
            _logger.info('TOKEN MONEDA SECUNDARIA SOLES 156 : %s', currency_id)
            x_niubiz_merchant = self.provider_id.niubiz_merchant_id_secondary_currency
        else:
            _logger.info('TOKEN MONEDA PRIMARIA USD 1 : %s', currency_id)

        # 🧠 Llama al método original y guarda el resultado
        processing_values = super()._get_processing_values()

        # 🔒 Si el proveedor no es 'niubiz', simplemente devuelve los valores originales
        if self.provider_code != 'niubiz':
            return processing_values

        # ✅ Lógica personalizada para niubiz (DESPUÉS del flujo estándar)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        payment_acquirer = self.env['payment.provider'].sudo().search([('code', '=', 'niubiz')], limit=1)
        security_token = payment_acquirer._niubiz_get_security_token()
        _logger.info("SECURITY TOKEN: %s", security_token)

        amount = float(processing_values.get('amount', 0.0))
        session_token = payment_acquirer._niubiz_get_session_token(processing_values, security_token)
        order_sequence = self.env.ref('niubiz_payment.niubiz_order_seq').next_by_id()
        tx = processing_values.get("reference", "").replace("/", "_")

        checkout_url = werkzeug.urls.url_join(base_url, ENV[payment_acquirer.state]['checkout_form'])
        timeout_url = werkzeug.urls.url_join(base_url, '/payment/niubiz/timeout')
        action_url = werkzeug.urls.url_join(base_url, f'/payment/niubiz/capture/{tx}/{order_sequence}')

        processing_values.update({
            'checkout_form': checkout_url,
            'company_id_name': self.company_id.name,
            'merchant_id': x_niubiz_merchant,
            'order_sequence': order_sequence,
            'amount': amount,
            'session_token': session_token['sessionKey'],
            'action_url': action_url,
            'timeout_url': timeout_url,
            'reference': self.reference,
            'payment_state': payment_acquirer.state,
        })
        self.write({
            'niubiz_session_token': session_token['sessionKey'],
            'niubiz_order_sequence': order_sequence,
            'niubiz_amount': self.amount,
            'niubiz_action_url': action_url,
            'niubiz_timeout_url': timeout_url,
            'niubiz_checkout_form': checkout_url,
            'niubiz_merchant_id': x_niubiz_merchant,
        })

        _logger.info("Updated processing values for niubiz:\n%s", pprint.pformat(processing_values))

        return processing_values