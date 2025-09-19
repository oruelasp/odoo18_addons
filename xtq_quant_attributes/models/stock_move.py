# -*- coding: utf-8 -*-
from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_open_attribute_selection_wizard(self):
        self.ensure_one()
        
        wizard = self.env['stock.quant.attribute.selection.wizard'].create({
            'move_id': self.id,
        })

        return {
            'name': 'Seleccionar Lotes por Atributos',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.quant.attribute.selection.wizard',
            'res_id': wizard.id,
            'target': 'new',
            'context': self.env.context,
        }
