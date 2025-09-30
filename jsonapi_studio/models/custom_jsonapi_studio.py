# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import models
from odoo.http import request
from odoo.addons.easy_jsonapi.models.easy_jsonapi import JsonAPIQuery


class MyJsonAPICustomStudio(models.AbstractModel):
    _inherit = 'easy.jsonapi.customstudio'

    @classmethod
    def my_custom_jsonapis(cls):
        res = super().my_custom_jsonapis()
        res.extend([
            'getContacts',
            'getContactDetails',
            'createContact',
            'resetPasswordMail'
            # Add Your Custom Endpoint Here. And it needs a function below.
            # i.e. {your-web-domain[:port]}/{your-api-endpoint}/{your-custom-endpoint}
            # Example: https://www.ekika.co/api/newlead
        ])
        return res

    @classmethod
    def getContacts(cls, query: JsonAPIQuery) -> dict:
        try:
            partners = request.env['res.partner'].search_read([], fields=['name', 'email'])
            result = {'data': {'contacts': partners}}
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def getContactDetails(cls, query: JsonAPIQuery) -> dict:
        try:
            partner = request.env['res.partner'].browse(int(query.params['partner_id']))
            result = {'data': {'contactDetails': partner.read(fields=['name', 'email', 'phone'])}}
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def createContact(cls, query: JsonAPIQuery) -> dict:
        try:
            data = request.get_json_data()
            partner = request.env['res.partner'].create({'name': data['name'], 'email': data['email']})
            result = {'data': {'contactDetails': partner.read(fields=['name', 'email'])}}
        except Exception as exc:
            result = {'errors': exc.args}
        return result

    @classmethod
    def resetPasswordMail(cls, query: JsonAPIQuery) -> dict:
        try:
            user = request.env['res.users'].browse(int(query.params['user_id']))
            user.action_reset_password()
            result = {'data': {'message': 'Password reset email sent successfully.'}}
        except Exception as exc:
            result = {'errors': {'message': 'Failed to send the password reset email.'}}
        return result
