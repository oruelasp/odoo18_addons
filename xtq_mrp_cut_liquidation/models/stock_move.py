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

    @api.depends('product_id.categ_id')
    def _compute_liquidation_visible(self):
        # Correctly read the configured categories from the company
        config_categs = self.env.company.liquidation_product_categ_ids
        if not config_categs:
            for move in self:
                move.liquidation_visible = False
            return

        # Get all child categories of the configured ones in a single search for efficiency
        all_allowed_categs = self.env['product.category'].search([('id', 'child_of', config_categs.ids)])
        allowed_categ_ids = set(all_allowed_categs.ids)

        for move in self:
            move.liquidation_visible = move.product_id.categ_id.id in allowed_categ_ids

    def action_open_cut_liquidation(self):
        self.ensure_one()
        # Explicitly define the custom view to be used in the action
        view_id = self.env.ref('xtq_mrp_cut_liquidation.stock_move_cut_liquidation_form_view').id
        return {
            'name': 'Liquidación de Corte',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'views': [[view_id, 'form']],
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
