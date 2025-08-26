# -*- coding: utf-8 -*-
from odoo import fields, models, _

class StockPicking(models.Model):
    """
    Extiende el modelo stock.picking para añadir una relación directa con la
    Orden de Trabajo de la cual se importaron los componentes.
    """
    _inherit = 'stock.picking'

    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Orden de Trabajo',
        copy=False,
        readonly=True,
        tracking=True,
        help="Orden de Trabajo de la cual se importaron los componentes."
    )

    def action_open_import_from_op_wizard(self):
        self.ensure_one()
        action = self.env.ref('xtq_import_from_op_wizard.action_import_from_op_wizard').read()[0]
        action.update({
            'context': {
                'default_production_id': False,
                'active_id': self.id,
                'active_ids': [self.id],
                'active_model': 'stock.picking',
            }
        })
        return action
