# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

import logging
import json
from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)

def doc_cleaner(docstring: str) -> str:
    if not docstring:
        return docstring
    docstring = ' '.join([x for x in docstring.split(' ') if x])
    docstring = '\n'.join([x for x in docstring.split('\n ') if x])
    return docstring

def first_line(multi_line: str) -> str:
    if not multi_line:
        return multi_line
    return multi_line.strip().splitlines()[0].strip()
class RestJsonCustomStudio(models.AbstractModel):
    """Base Rest Json Custom Studio Method's. Inherit this and define your own api handler.
    
    For example implementation take a look at commented code after this class.
    """
    _name = 'easy.restjson.customstudio'
    _description = 'Easy RestJson Custom Studio'

    @classmethod
    def my_custom_restjson(cls):
        """Override this method and return supper's result by adding your methods
        defined in it which are allowed for private custom calls.

        See an example bellow.
        """
        return {}

    @classmethod
    def _swagger_api_parameters(cls) -> list:
        return [
            {
                "name": "Content-Type",
                "in": "header",
                "required": True,
                "type": "string",
                "default": "application/json"
            },
            {
                "name": "x-api-key",
                "in": "header",
                "required": True,
                "type": "string"
            },
        ]

    @classmethod
    def swagger_doc(cls, api_endpoint):
        doc = cls._swagger_doc(api_endpoint)
        return doc

    @classmethod
    def _swagger_doc(cls, api_endpoint):
       return {
            'swagger': cls._swagger_version(api_endpoint),
            'info': cls._swagger_info(api_endpoint),
            'host': cls._swagger_host(api_endpoint),
            'basePath': cls._swagger_base_path(api_endpoint),
            'schemes': cls._swagger_schemes(api_endpoint),
            'paths': cls._register_paths(api_endpoint)
        }

    @classmethod
    def _swagger_version(cls, api_endpoint):
        return '2.0'

    @classmethod
    def _swagger_info(cls, api_endpoint) -> dict:
        return {
            "title": api_endpoint.name,
            "description": api_endpoint.description,
            "version": "1.0.0",
        }

    @classmethod
    def _swagger_host(cls, api_endpoint):
        return request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', default=''
        ).replace('http://', '').replace('https://', '')

    @classmethod
    def _swagger_base_path(cls, api_endpoint):
        return f'/{api_endpoint.base_endpoint}'

    @classmethod
    def _swagger_schemes(cls, api_endpoint):
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', default=''
        )
        return ['https'] if base_url.startswith('https') else ['http']

    @classmethod
    def _register_paths(cls, api_endpoint):
        values = {}
        all_custom_methods = cls.my_custom_restjson()
        for key, val in all_custom_methods.items():
            if hasattr(cls, key):
                method = getattr(cls, key)
                doc_method = hasattr(cls, f'_doc_{method.__name__}')
                if doc_method:
                    method_vals = cls._swagger_method_user(method, api_endpoint)
                else:
                    method_vals = cls._swagger_method_default(method, api_endpoint)
                method_vals.update({
                    'consumes': ['application/json'],
                    'produces': ['application/json'],
                })
                values[f'/{key}'] = {
                    val.get('method', 'POST').lower(): method_vals
                }
            else:
                _logger.warning(f"EASY API RestJson Custom Method '{key}' declared but not implemented.")
        return values

    @classmethod
    def _swagger_method_default(cls, method, api_endpoints):
        return {
            'tags': ["Custom"],
            'summary': first_line(method.__doc__ or ''),
            'description': doc_cleaner(method.__doc__ or ''),
            'parameters': cls._swagger_api_parameters(),
            'responses': cls._swagger_default_responses(),
        }

    @classmethod
    def _swagger_method_user(cls, method, api_endpoints):
        method_vals = getattr(cls, f'_doc_{method.__name__}')()
        method_vals.setdefault('parameters', []).append({
            "name": "Content-Type",
            "in": "header",
            "required": True,
            "type": "string",
            "default": "application/json"
        })
        return method_vals

    @classmethod
    def _swagger_default_responses(cls) -> dict:
        return {
          "200": cls._default_200_response(),
          "401": cls._default_401_response(),
          "400": cls._default_400_response()
        }

    @classmethod
    def _default_200_response(cls):
        return {
            "description": "successful operation",
            "schema": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "properties": {
                        "values": {
                            "type": "array",
                            "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                "type": "integer",
                                "format": "int32",
                                },
                            }
                            }
                        }
                        },
                    },
                }
            }
        }

    @classmethod
    def _default_401_response(cls):
        return {
            "description": "Unauthorized",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "example": "Unauthorized"
                    },
                    "detail": {
                        "type": "string",
                        "example": "Access Denied"
                    },
                    "debug": {
                        "type": "string",
                    },
                },
                "required": ["title"]
            }
        }

    @classmethod
    def _default_400_response(cls):
        return {
            "description": "Bad Request",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "example": "Bad Request"
                    },
                    "detail": {
                        "type": "string",
                        "example": "Invalid Values"
                    },
                    "debug": {
                        "type": "string",
                    },
                },
                "required": ["title"]
            }
        }


# class YourOwnRestJson(models.AbstractModel):
#     _inherit = 'easy.restjson.customstudio'

    # @classmethod
    # def my_custom_restjson(cls):
    #     res = super().my_custom_restjson()
    #     res.update({
    #         'myownapiendpoint': {'method': 'GET'}
    #     })  # define your custom api handle/endpoint with HTTP Method
    #     return res

    # @classmethod
    # def myownapiendpoint(cls, params) -> dict:
    #     """This is your custom api endpoint works dynamic with configured APIs."""
    #     result = {
    #         'data': 'My Own API Endpoing Call Successful',
    #     }
    #     return result
