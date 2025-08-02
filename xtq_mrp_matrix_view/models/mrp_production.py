# -*- coding: utf-8 -*-
from odoo import models, api
from collections import defaultdict

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Se asume que cada MO de corte tendrá un lote de producción final esperado
    # y que en ese lote se definirán los atributos de Tono y Talla.
    # El campo lot_producing_id es estándar en Odoo.

    @api.model
    def get_mrp_planning_matrix_data(self, domain):
        mos = self.search(domain)
        if not mos:
            return {'is_empty': True}

        origin = mos[0].origin if mos else False
        
        matrix_data = defaultdict(dict)
        mo_map = defaultdict(dict)
        tones = set()
        sizes = set()

        # Buscamos los atributos "Tono" y "Talla Cortada" una sola vez
        attribute_tone = self.env['product.attribute'].search([('name', '=', 'Tono')], limit=1)
        attribute_size = self.env['product.attribute'].search([('name', '=', 'Talla Cortada')], limit=1)

        for mo in mos.filtered(lambda m: m.lot_producing_id):
            lot = mo.lot_producing_id
            
            tone_line = lot.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute_tone)
            size_line = lot.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute_size)
            
            if tone_line and size_line:
                tone_val = tone_line.value_id.name
                size_val = size_line.value_id.name
                tones.add(tone_val)
                sizes.add(size_val)
                
                matrix_data[tone_val][size_val] = mo.product_qty
                mo_map[tone_val][size_val] = mo.id

        # Lógica de resumen (ejemplo)
        committed_meters = 1154.0 
        suggested_production = 961

        return {
            'is_empty': False,
            'product_name': mos[0].product_id.product_tmpl_id.name,
            'origin': origin,
            'tones': sorted(list(tones)),
            'sizes': sorted(list(sizes)),
            'matrix_data': matrix_data,
            'mo_map': mo_map,
            'committed_meters': committed_meters,
            'suggested_production': suggested_production,
            'curve': {'28': 4, '30': 5, '32': 4, '34': 2, '36': 1},
        }

    # Los métodos recalculate y save permanecen igual, ya que la lógica
    # de negocio no cambia, solo la forma de obtener los datos.
    @api.model
    def recalculate_mrp_matrix_distribution(self, mo_ids, new_total_qty, curve):
        # ... (Implementación de la regla de tres) ...
        pass

    def save_mrp_planning_matrix_data(self, matrix_data):
        with self.env.cr.savepoint():
            for mo_id, new_qty in matrix_data.items():
                self.browse(int(mo_id)).write({'product_qty': new_qty})
        return True 