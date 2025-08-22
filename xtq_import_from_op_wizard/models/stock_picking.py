# -*- coding: utf-8 -*-
from odoo import fields, models

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
