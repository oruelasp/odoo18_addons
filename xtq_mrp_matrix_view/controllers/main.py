# controllers/main.py
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class MrpMatrixAppController(http.Controller):
    @http.route('/xtq_mrp_matrix_view/get_data', type='json', auth='user')
    def get_data(self, domain):
        return request.env['mrp.production'].get_mrp_planning_matrix_data(domain)

    @http.route('/xtq_mrp_matrix_view/recalculate', type='json', auth='user')
    def recalculate(self, mo_ids, new_total_qty, curve):
        return request.env['mrp.production'].recalculate_mrp_matrix_distribution(mo_ids, new_total_qty, curve)

    @http.route('/xtq_mrp_matrix_view/save', type='json', auth='user')
    def save_data(self, matrix_data):
        # Es mejor llamar el método sobre un recordset si es posible
        mo_ids = [int(k) for k in matrix_data.keys()]
        return request.env['mrp.production'].browse(mo_ids).save_mrp_planning_matrix_data(matrix_data) 