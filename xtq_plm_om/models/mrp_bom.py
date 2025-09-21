# -*- coding: utf-8 -*-
from odoo import models, fields

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    cost = fields.Float(string="Costo", digits='Product Price')
