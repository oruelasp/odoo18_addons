# -*- coding: utf-8 -*-
from odoo import fields, models, _

class StockPicking(models.Model):
    """
    Extiende el modelo stock.picking para añadir campos de trazabilidad
    relacionados con la importación desde Órdenes de Producción.
    """
    _inherit = 'stock.picking'

    workorder_origin = fields.Text(
        string='Origen de OT',
        copy=False,
        readonly=True,
        help="Órdenes de Trabajo de las cuales se importaron componentes."
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
