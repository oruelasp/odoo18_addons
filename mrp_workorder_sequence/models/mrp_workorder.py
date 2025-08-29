# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"
    _order = "production_id, sequence, id"

    sequence = fields.Integer(string="Sequence", default=0)
