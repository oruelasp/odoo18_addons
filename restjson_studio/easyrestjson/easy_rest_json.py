# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

import logging
import json
from odoo import models, fields
from odoo.http import request
from odoo.http import Controller
from odoo.http import route

_logger = logging.getLogger(__name__)

CUSTOM_HELP = '''Enabling this option allows you to define private methods with restjson dynamic calls.

You can define private method as following.


class YourOwnRestJson(models.AbstractModel):
    _inherit = 'easy.restjson.customstudio'

    @classmethod
    def my_custom_restjson(cls):
        res = super().my_custom_restjson()
        res.update({
            'myownapiendpoint': {'method': 'GET'}
        })  # define your custom api handle/endpoint with HTTP Method
        return res

    @classmethod
    def myownapiendpoint(cls, params) -> dict:
        """This is your custom api endpoint works dynamic with configured APIs."""
        result = {
            'data': 'My Own API Endpoing Call Successful',
        }
        return result
'''

class EasyApi(models.Model):
    _inherit = 'easy.api'

    enable_custom_restjson_studio = fields.Boolean('Activate RestJson Studio', tracking=True, help=CUSTOM_HELP)

    def action_open_restjson_doc(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'restjson_studio.restjson_doc_client_action',
            'params': {
                'api_base_endpoint': self.base_endpoint,
            },
            'context': {
                'api_base_endpoint': self.base_endpoint,
            }
        }


class RestJsonSwaggerDoc(models.AbstractModel):
    _inherit = 'restjson.swagger.doc'

    @classmethod
    def swagger_doc(cls, api_endpoint):
        values = super().swagger_doc(api_endpoint)
        swagger_values = request.env['easy.restjson.customstudio'].swagger_doc(api_endpoint)
        values['paths'].update(swagger_values['paths'])
        values['tags'].append({
            "name": "Custom",
            "description": "Custom endpoints defined by the user",
        })
        return values


class CustomStudioEasyRestJson(models.AbstractModel):
    _inherit = 'easy.rest.json'

    @classmethod
    def serve_private_restjson(cls):
        if not request.env.user:
            raise Exception('Not Allowed')

        custom_endpoint = request.easyapi['custom_endpoint']
        restjsonStudioObj = request.env['easy.restjson.customstudio']
        if hasattr(restjsonStudioObj, custom_endpoint):
            params = {
                **request.httprequest.args,
                **request.httprequest.form,
                **request.httprequest.files,
            }
            json_data = request.httprequest.get_data(as_text=True)
            if json_data:
                params.update(json.loads(request.httprequest.get_data(as_text=True)))
            result = getattr(restjsonStudioObj, custom_endpoint)(params)
            return result
        else:
            raise Exception('Method Not Found')


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _generate_routing_rules(self, modules, converters):
        if not request:
            yield from super()._generate_routing_rules(modules, converters)
            return
        else:
            all_custom_apis = request.env['easy.api'].sudo().search([('api_type', '=', 'rest_json'), ('enable_custom_restjson_studio', '=', True)])
            private_endpoints_to_register = request.env['easy.restjson.customstudio'].my_custom_restjson()
            all_endpoints = []
            if isinstance(private_endpoints_to_register, dict):
                for api in all_custom_apis:
                    for key,val in private_endpoints_to_register.items():
                        all_endpoints.append({
                            'url':f'/{api.base_endpoint}/{key}',
                            'method': val.get('method', 'POST'),
                    })
            else:
                _logger.warning("EASY API RestJson 'my_custom_restjson' must return dict of Custom APIs.")
            for url, endpoint in super()._generate_routing_rules(modules, converters):
                if url == '/_restjson_dynamic_custom_apiroute':
                    for endpoint_url in all_endpoints:
                        endpoint.routing['methods'] = [endpoint_url['method']]
                        yield endpoint_url['url'], endpoint
                else:
                    yield url, endpoint


class CustomRestJson(Controller):

    @route(['/_restjson_dynamic_custom_apiroute'], auth='api', csrf=False, type='api', cors='api')
    def customStudioRestJsonController(self):
        return request.env['easy.rest.json'].serve_private_restjson()
