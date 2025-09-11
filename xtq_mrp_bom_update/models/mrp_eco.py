# -*- coding: utf-8 -*-
from odoo import models, fields

class MrpEco(models.Model):
    _inherit = 'mrp.eco'

    rejection_note = fields.Text(string="Motivo del Rechazo", copy=False, readonly=True)

    def action_reject(self):
        """
        Abre un wizard para solicitar la nota de rechazo antes de
        mover el ECO a una etapa de rechazo o borrador.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Motivo del Rechazo',
            'res_model': 'mrp.eco.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_eco_id': self.id,
            }
        }
