# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    has_related_eco_and_op = fields.Boolean(
        compute='_compute_has_related_eco_and_op',
        string="Tiene ECO y OP relacionados",
        help="Indica si esta revisión de BoM fue generada por un ECO que a su vez está vinculado a una Orden de Producción."
    )
    
    related_production_id = fields.Many2one(
        'mrp.production',
        compute='_compute_has_related_eco_and_op',
        string="Orden de Producción Relacionada"
    )

    def _compute_has_related_eco_and_op(self):
        for bom in self:
            # Búsqueda en dos pasos para evitar errores del ORM con campos One2many anidados.
            # 1. Buscar las líneas de cambio de BoM que apuntan a este BoM como una nueva revisión.
            eco_bom_lines = self.env['mrp.eco.bom.line'].search([
                ('new_bom_id', '=', bom.id)
            ])
            
            # 2. Buscar el ECO que contiene esas líneas y que además está ligado a una OP.
            eco = self.env['mrp.eco'].search([
                ('bom_ids', 'in', eco_bom_lines.ids),
                ('production_id', '!=', False)
            ], limit=1)
            
            if eco:
                bom.has_related_eco_and_op = True
                bom.related_production_id = eco.production_id.id
            else:
                bom.has_related_eco_and_op = False
                bom.related_production_id = False

    def action_update_proportional_quantities(self):
        self.ensure_one()
        if self.related_production_id:
            production = self.related_production_id
            
            # Recalcular la cantidad del BoM
            self.product_qty = production.product_qty

            # Recalcular cantidades de componentes
            factor = production.product_qty / production.sample_bom_id.product_qty if production.sample_bom_id.product_qty else 1
            for line in self.bom_line_ids:
                original_line = production.sample_bom_id.bom_line_ids.filtered(lambda l: l.product_id == line.product_id)
                if original_line:
                    line.product_qty = original_line[0].product_qty * factor
        return True
