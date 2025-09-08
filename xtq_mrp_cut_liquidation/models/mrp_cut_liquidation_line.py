# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpCutLiquidationLine(models.Model):
    _name = 'mrp.cut.liquidation.line'
    _description = 'Línea de Liquidación de Corte de Producción'

    stock_move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Movimiento de Stock',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Nº Tendido',
        default=10,
    )
    fabric_width = fields.Float(
        string='Ancho Tela',
        digits='Product Unit of Measure',
    )
    fabric_out_qty = fields.Float(
        string='Salida Tela',
        digits='Product Unit of Measure',
    )
    actual_spread_meters = fields.Float(
        string='Tendido Real',
        digits='Product Unit of Measure',
    )
    difference_qty = fields.Float(
        string='Difer.',
        compute='_compute_quantities',
        store=True,
        digits='Product Unit of Measure',
    )
    marker_length = fields.Float(
        string='Trazo',
        digits='Product Unit of Measure',
    )
    number_of_plies = fields.Integer(
        string='Paños',
    )
    final_marker_qty = fields.Float(
        string='Trazo Final',
        compute='_compute_quantities',
        store=True,
        digits='Product Unit of Measure',
    )
    scrap_percentage = fields.Float(
        string='Merma (%)',
    )
    scrap_quantity = fields.Float(
        string='Cant. Merma',
        compute='_compute_quantities',
        store=True,
        digits='Product Unit of Measure',
    )
    effective_consumption = fields.Float(
        string='Consumo Efectivo',
        compute='_compute_quantities',
        store=True,
        digits='Product Unit of Measure',
    )

    @api.depends('fabric_out_qty', 'actual_spread_meters', 'marker_length', 'number_of_plies', 'scrap_percentage')
    def _compute_quantities(self):
        for line in self:
            line.difference_qty = line.fabric_out_qty - line.actual_spread_meters
            line.final_marker_qty = line.marker_length * line.number_of_plies
            
            consumption = line.final_marker_qty
            if line.scrap_percentage > 0:
                line.scrap_quantity = consumption * (line.scrap_percentage / 100)
            else:
                line.scrap_quantity = 0
            
            line.effective_consumption = consumption + line.scrap_quantity
