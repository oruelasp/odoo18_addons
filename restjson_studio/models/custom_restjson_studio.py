# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

import json
from werkzeug.datastructures import Headers
from odoo import models
from odoo.http import request, Response



class MyRestJsonCustomStudio(models.AbstractModel):
    _inherit = 'easy.restjson.customstudio'

    @classmethod
    def my_custom_restjson(cls):
        res = super().my_custom_restjson()
        res.update(
            {
                'getContacts': {'method': 'GET'},
                'getContactDetails': {'method': 'GET'},
                'createContact': {'method': 'POST'},
                'resetPasswordMail': {'method': 'POST'},
            }
            # Add Your Custom Endpoint Here. And it needs a function below.
            # i.e. {your-web-domain[:port]}/{your-api-endpoint}/{your-custom-endpoint}
            # Example: https://www.ekika.co/api/newlead
          )
        return res

    @classmethod
    def getContacts(cls, params) -> dict:
        """Get list of contacts
        return list of contacts with name, email fields.
        """
        try:
            partners = request.env['res.partner'].search_read([], fields=['name', 'email'])
            result = {'data': {'contacts': partners}}
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def getContactDetails(cls, params) -> dict:
        try:
            partner = request.env['res.partner'].browse(int(params['partner_id']))
            result = {'data': {'contactDetails': partner.read(fields=['name', 'email', 'phone'])}}
            data = json.dumps(result, ensure_ascii=False)
            headers = Headers()
            headers['Content-Length'] = len(data)
            headers['Content-Type'] = 'application/json; charset=utf-8'
            return Response(data, headers=headers ,status=200)
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def _doc_getContactDetails(cls) -> dict:
        return {
            'tags': ['Custom'],
            'summary': 'Partner Details',
            'description': 'Get Details of Particular Partner',
            'parameters': [
              {
                    "name": "partner_id",
                    "in": "query",
                    "required": True,
                    "type": "integer"
              },
              {
                    "name": "x-api-key",
                    "in": "header",
                    "required": True,
                    "type": "string"
              },
            ],
            'responses': cls._swagger_default_responses()
        }

    @classmethod
    def createContact(cls, params) -> dict:
        try:
            partner = request.env['res.partner'].create({'name': params['name'], 'email': params['email']})
            result = {'data': {'contactDetails': partner.read(fields=['name', 'email'])}}
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def _doc_createContact(cls) -> dict:
        return {
            'tags': ['Create Contact'],
            'summary': 'Create Partner Contact',
            'description': 'Create partner using name and email',
            'parameters': [
              {
                    "name": "x-api-key",
                    "in": "header",
                    "required": True,
                    "type": "string"
              },
              {
                "in": "body",
                "name": "create-contact",
                "description": "Create Contact Body",
                "required": True,
                "schema": {
                  "type": "object",
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "email": {
                        "type": "string"
                      },
                    },
                }
              }
            ],
            'responses': cls._swagger_default_responses()
        }

    @classmethod
    def resetPasswordMail(cls, params) -> dict:
        try:
            user = request.env['res.users'].browse(int(params['user_id']))
            user.action_reset_password()
            result = {'data': {'message': 'Password reset email sent successfully.'}}
        except Exception as exc:
            result = {'errors': {'message': 'Failed to send the password reset email.'}}
        return result

    @classmethod
    def _doc_resetPasswordMail(cls) -> dict:
        return {
            'tags': ['Custom'],
            'parameters': [
              {
                    "name": "user_id",
                    "in": "query",
                    "required": True,
                    "type": "integer"
              },
              {
                    "name": "x-api-key",
                    "in": "header",
                    "required": True,
                    "type": "string"
              },
            ],
            'responses': cls._swagger_default_responses()
        }
