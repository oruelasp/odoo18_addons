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
        """
        Computes visibility based on the product's category and its ancestors.
        The button is visible if the product's category or any of its parent
        categories are present in the company's liquidation category settings.
        """
        config_categ_ids = set(self.env.company.liquidation_product_categ_ids.ids)
        if not config_categ_ids:
            self.liquidation_visible = False
            return

        # Memoization cache for category visibility to avoid redundant computations
        categ_visibility_cache = {}

        for move in self:
            if not move.product_id.categ_id:
                move.liquidation_visible = False
                continue

            product_categ = move.product_id.categ_id
            if product_categ.id in categ_visibility_cache:
                move.liquidation_visible = categ_visibility_cache[product_categ.id]
                continue

            # Traverse up the category hierarchy using the parent_path field for efficiency
            ancestor_ids = {int(cid) for cid in product_categ.parent_path.split('/') if cid}
            
            is_visible = bool(config_categ_ids.intersection(ancestor_ids))
            
            categ_visibility_cache[product_categ.id] = is_visible
            move.liquidation_visible = is_visible

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
