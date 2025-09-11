# -*- coding: utf-8 -*-

from odoo import models, fields

class MrpEcoRejectionWizard(models.TransientModel):
    _name = 'mrp.eco.rejection.wizard'
    _description = 'Wizard para Rechazo de ECO'

    rejection_reason = fields.Text(string="Motivo del Rechazo", required=True)
    eco_id = fields.Many2one('mrp.eco', string="ECO a Rechazar", readonly=True)
    
    def action_confirm_rejection(self):
        self.ensure_one()
        if self.eco_id:
            # Encuentra la primera etapa que no sea 'final' ni 'aprobada', idealmente una etapa de 'rechazado' o 'borrador'.
            rejected_stage = self.env['mrp.eco.stage'].search([
                ('final_stage', '=', False),
                ('approved', '=', False)
            ], limit=1, order='sequence asc')

            if rejected_stage:
                self.eco_id.write({
                    'rejection_note': self.rejection_reason,
                    'stage_id': rejected_stage.id,
                })
        return {'type': 'ir.actions.act_window_close'}
