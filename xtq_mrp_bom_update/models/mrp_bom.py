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
        # Búsqueda optimizada y directa para encontrar los ECOs relacionados.
        # 1. Buscar todos los ECOs que apuntan a cualquiera de los BoMs del recordset actual
        #    y que además tienen una Orden de Producción vinculada.
        ecos = self.env['mrp.eco'].search([
            ('new_bom_id', 'in', self.ids),
            ('production_id', '!=', False)
        ])
        
        # 2. Crear un mapa para una asignación eficiente: {bom_id: eco_record}
        eco_map = {eco.new_bom_id.id: eco for eco in ecos}

        # 3. Asignar los valores a cada BoM del recordset.
        for bom in self:
            eco = eco_map.get(bom.id)
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
