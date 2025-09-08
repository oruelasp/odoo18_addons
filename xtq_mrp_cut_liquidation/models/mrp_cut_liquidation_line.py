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
        compute='_compute_quantities',
        store=True,
        readonly=True,
    )
    scrap_quantity = fields.Float(
        string='Cant. Merma',
        compute='_compute_quantities',
        store=True,
        readonly=True,
        digits='Product Unit of Measure',
    )
    effective_consumption = fields.Float(
        string='Consumo Efectivo',
        compute='_compute_quantities',
        store=True,
        readonly=True,
        digits='Product Unit of Measure',
    )

    @api.depends('fabric_out_qty', 'actual_spread_meters', 'marker_length', 'number_of_plies')
    def _compute_quantities(self):
        for line in self:
            line.difference_qty = line.fabric_out_qty - line.actual_spread_meters
            
            final_marker_qty = line.marker_length * line.number_of_plies
            line.final_marker_qty = final_marker_qty

            scrap_quantity = line.actual_spread_meters - final_marker_qty
            line.scrap_quantity = scrap_quantity

            if line.actual_spread_meters > 0:
                line.scrap_percentage = (scrap_quantity / line.actual_spread_meters) * 100
            else:
                line.scrap_percentage = 0.0
            
            line.effective_consumption = line.actual_spread_meters
