# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpBomRejectionWizard(models.TransientModel):
    _name = 'mrp.bom.rejection.wizard'
    _description = 'Wizard para Rechazo de BoM'

    rejection_reason = fields.Text(string="Motivo del Rechazo", required=True)
    bom_id = fields.Many2one('mrp.bom', string="BoM a Rechazar", readonly=True)

    def action_confirm_rejection(self):
        self.ensure_one()
        if self.bom_id:
            self.bom_id.write({
                'rejection_note': self.rejection_reason,
                'state': 'rejected',
            })
        return {'type': 'ir.actions.act_window_close'}
