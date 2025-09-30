# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment.tests.http_common import PaymentHttpCommon


@tagged('post_install', '-at_install')
class TestNiubizRedirect(PaymentHttpCommon):
    @mute_logger('odoo.addons.payment.models.payment_transaction')
    def test_no_input_missing_from_redirect_form(self):
        """ Test that no key is omitted from the rendering values for Niubiz. """
        # Crea una transacción de tipo 'redirect' para Niubiz
        tx = self._create_transaction(flow='redirect')

        expected_input_keys = [
            'merchantId',
            'amount',
            'orderRef',
            'session_token',
            'action_url',
            'timeout_url',
        ]

        # Obtén los valores de procesamiento para el flujo 'redirect'
        processing_values = tx._get_processing_values()

        # Extrae los valores del formulario de redirección a partir del HTML
        form_info = self._extract_values_from_html_form(processing_values['redirect_form_html'])

        # Verifica que los valores en 'processing_values' se estén reflejando en el formulario
        self.assertEqual(form_info['inputs']['merchantId'], processing_values['merchantId'])
        self.assertEqual(form_info['inputs']['amount'], str(processing_values['amount']))
        self.assertEqual(form_info['inputs']['orderRef'], processing_values['orderRef'])
        self.assertEqual(form_info['inputs']['session_token'], processing_values['session_token'])
        self.assertEqual(form_info['inputs']['action_url'], processing_values['action_url'])
        self.assertEqual(form_info['inputs']['timeout_url'], processing_values['timeout_url'])

