# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

from werkzeug.routing import Map,Rule
from odoo.addons.easy_restjson.restjson import RestJson
from odoo.http import request


class RestJson(RestJson):

    def url_match(self):
        """Identify parameters from URL.

        /res.partner/search_read
        /custom_endpoint
        """
        endpoint = request.base_endpoint
        urls = Map([
            Rule(f'/{endpoint}/<string:model>/<string:method>'),
            Rule(f'/{endpoint}/<string:custom_endpoint>'),
        ]).bind('')
        return urls.match(self.request.httprequest.path)[1]
