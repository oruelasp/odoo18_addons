# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from odoo import models


class JsonAPICustomStudio(models.AbstractModel):
    """Base Json:API Custom Studio Method's. Inherit this and define your own api handler.
    
    For example implementation take a look at commented code after this class.
    """
    _name = 'easy.jsonapi.customstudio'

    @classmethod
    def my_custom_jsonapis(cls):
        """Override this method and return supper's result by adding your methods
        defined in it which are allowed for private custom calls.

        See an example bellow.
        """
        return []


# from odoo.addons.easy_jsonapi.models.easy_jsonapi import JsonAPIQuery
# class YourOwnJsonAPI(models.AbstractModel):
#     _inherit = 'easy.jsonapi.customstudio'

    # @classmethod
    # def my_custom_jsonapis(cls):
    #     res = super().my_custom_jsonapis()
    #     res.extend(['myownapiendpoint'])  # define your custom api handle/endpoint
    #     return res

    # @classmethod
    # def myownapiendpoint(self, query: JsonAPIQuery) -> dict:
    #     """This is your custom api endpoint works dynamic with configured APIs."""
    #     result = {
    #         'data': 'My Own API Endpoing Call Successful',
    #     }
    #     return result
