# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    workorder_picking_restriction = fields.Selection([
        ('none', 'No aplicar'),
        ('one_step', 'Requiere 1 movimiento (Entrada/Salida)'),
        ('two_steps', 'Requiere 2 movimientos (Entrada y Salida)')
    ], 
    string="Restricción de Finalización de OT",
    config_parameter='xtq_import_from_op_wizard.workorder_picking_restriction',
    default='none',
    help="""Define una regla para poder finalizar una Orden de Trabajo (OT) basada en sus albaranes relacionados.
         - No aplicar: No hay restricciones.
         - Requiere 1 movimiento: La OT debe tener al menos un albarán de tipo Entrada o Salida.
         - Requiere 2 movimientos: La OT debe tener al menos un albarán de Entrada Y uno de Salida."""
    )
