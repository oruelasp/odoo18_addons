from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models



class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_total_sale_orders(self, partner_id):
        date_from = fields.Date.to_string(date.today().replace(day=1))
        date_to = fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
        model = self.env['sale.order']
        count_mes = model.search_count(
            [('partner_id', '=', partner_id), ('date_order', '>=', date_from), ('date_order', '<=', date_to),
             ('state', '=', 'sale')])
        if count_mes > 5: return 1
        return 0
