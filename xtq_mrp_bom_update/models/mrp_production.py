# models/mrp_production.py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sample_bom_id = fields.Many2one('mrp.bom', string="Orden de Muestra (BOM Base)", readonly=True)

    def action_create_production_sheet(self):
        self.ensure_one()
        if not self.bom_id:
            raise UserError(_("Por favor, establezca una Lista de Materiales base antes de crear la Ficha de Producción."))

        # 1. Duplicar el BOM
        new_bom = self.bom_id.copy({
            'code': self.name,
            'product_qty': self.product_qty,
            'state': 'draft',
        })

        # 2. Recalcular cantidades de componentes
        factor = self.product_qty / self.bom_id.product_qty if self.bom_id.product_qty else 1
        for line in new_bom.bom_line_ids:
            line.product_qty = line.product_qty * factor

        # 3. Asignar los BOMs a la OP
        self.write({
            'sample_bom_id': self.bom_id.id,
            'bom_id': new_bom.id,
        })

        # 4. Abrir el nuevo BOM en una nueva ventana
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'form',
            'res_id': new_bom.id,
            'target': 'current',
        }
    
    def action_update_bom(self):
        # Heredar y extender la función estándar
        if self.bom_id and self.bom_id.state != 'approved':
            raise UserError(_("Solo se pueden usar Fichas de Producción (BOM) aprobadas para actualizar la OP."))
        return super(MrpProduction, self).action_update_bom()
