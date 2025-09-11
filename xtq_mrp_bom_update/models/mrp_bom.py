# models/mrp_bom.py
# -*- coding: utf-8 -*-
from odoo import models, fields

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ], string='Estado', default='draft', copy=False, index=True, readonly=True)

    rejection_note = fields.Text(string="Motivo del Rechazo", copy=False)

    def action_send_for_approval(self):
        self.write({'state': 'in_progress'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Motivo del Rechazo',
            'res_model': 'mrp.bom.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bom_id': self.id,
            }
        }
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
