# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import models, fields
from odoo.http import request
from odoo.http import Controller as JsonAPIController
from odoo.http import route as jsonapiRoute
from odoo.addons.easy_jsonapi.models import easy_jsonapi

CUSTOM_HELP = '''Enabling this option allows you to define private methods with json:api dynamic calls.

You can define private method as following.

from odoo.addons.easy_jsonapi.models.easy_jsonapi import JsonAPIQuery

class YourOwnJsonAPI(models.AbstractModel):
    _inherit = 'easy.jsonapi.customstudio'

    @classmethod
    def my_custom_jsonapis(cls):
        res = super().my_custom_jsonapis()
        res.extend(['myownapiendpoint'])  # define your custom api handle/endpoint
        return res

    @classmethod
    def myownapiendpoint(self, query: JsonAPIQuery) -> dict:
        """This is your custom api endpoint works dynamic with configured APIs."""
        result = {
            'data': 'My Own API Endpoing Call Successful',
        }
        return result
'''

class EasyApi(models.Model):
    _inherit = 'easy.api'

    enable_custom_jsonapi_studio = fields.Boolean('Activate JsonAPI Studio', tracking=True, help=CUSTOM_HELP)


class CustomStudioEasyJsonAPI(models.TransientModel):
    _inherit = 'easy.jsonapi'

    @classmethod
    def serve_private_jsonapi(cls):
        if not request.env.user:
            raise Exception('Not Allowed')

        request_query = easy_jsonapi.JsonAPIQuery(request=request)
        request_query.parse_request()
        custom_endpoint = request_query.model
        jsonapiStudioObj = request.env['easy.jsonapi.customstudio']
        if hasattr(jsonapiStudioObj, custom_endpoint):
            response = easy_jsonapi.JsonAPIResponse(meta={"version": "1.1"})
            result = getattr(jsonapiStudioObj, custom_endpoint)(request_query)
            if not 'data' in result and not 'errors' in result:
                raise Exception('Please provide "data" or "errors" in response')
            if 'errors' in result:
                response.jsonapi_errors = result['errors']
                return response
            response.jsonapi_data = result['data']
            response.jsonapi_included = result.get('included', [])
            response.jsonapi_links = result.get('links', {})
            return response
        else:
            raise Exception('Method Not Found')


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _generate_routing_rules(self, modules, converters):
        if not request:
            yield from super()._generate_routing_rules(modules, converters)
            return
        else:
            all_custom_apis = request.env['easy.api'].sudo().search([('api_type', '=', 'jsonapi'), ('enable_custom_jsonapi_studio', '=', True)])
            private_endpoints_to_register = request.env['easy.jsonapi.customstudio'].my_custom_jsonapis()
            all_endpoints = []
            for api in all_custom_apis:
                all_endpoints.extend(
                    [f'/{api.base_endpoint}/{customendpoint}' for customendpoint in private_endpoints_to_register]
                )
            for url, endpoint in super()._generate_routing_rules(modules, converters):
                if url == '/_jsonapi_dynamic_custom_apiroute':
                    for endpoint_url in all_endpoints:
                        yield endpoint_url, endpoint
                else:
                    yield url, endpoint


class CustomJsonAPI(JsonAPIController):

    @jsonapiRoute(['/_jsonapi_dynamic_custom_apiroute'], auth='api', csrf=False, type='api', cors='api')
    def customStudioJsonApiController(self):
        return request.env['easy.jsonapi'].serve_private_jsonapi()
