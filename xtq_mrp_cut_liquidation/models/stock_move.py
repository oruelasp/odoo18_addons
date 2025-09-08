# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    liquidation_line_ids = fields.One2many(
        comodel_name='mrp.cut.liquidation.line',
        inverse_name='stock_move_id',
        string='Líneas de Liquidación',
    )
    liquidation_visible = fields.Boolean(
        string='Liquidación Visible',
        compute='_compute_liquidation_visible',
        store=False,
    )
    total_scrap_qty = fields.Float(
        string='Merma Total',
        compute='_compute_liquidation_totals',
        store=True,
        digits='Product Unit of Measure',
    )
    total_effective_consumption = fields.Float(
        string='Consumo Real Total',
        compute='_compute_liquidation_totals',
        store=True,
        digits='Product Unit of Measure',
    )

    @api.depends('liquidation_line_ids.scrap_quantity', 'liquidation_line_ids.effective_consumption')
    def _compute_liquidation_totals(self):
        for move in self:
            move.total_scrap_qty = sum(move.liquidation_line_ids.mapped('scrap_quantity'))
            move.total_effective_consumption = sum(move.liquidation_line_ids.mapped('effective_consumption'))

    def _get_liquidation_categ_ids(self):
        """ Helper to get configured categories """
        return self.env['res.config.settings'].get_values().get('liquidation_product_categ_ids', [])

    def _compute_liquidation_visible(self):
        categ_ids = self._get_liquidation_categ_ids()
        if not categ_ids:
            for move in self:
                move.liquidation_visible = False
            return
        
        # This approach avoids making a search for each move
        all_categs = self.env['product.category'].browse(categ_ids)
        child_categ_ids = self.env['product.category'].search([('id', 'child_of', all_categs.ids)]).ids

        for move in self:
            if move.product_id.categ_id.id in child_categ_ids:
                move.liquidation_visible = True
            else:
                move.liquidation_visible = False

    def action_open_cut_liquidation(self):
        self.ensure_one()
        return {
            'name': 'Liquidación de Corte',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }
