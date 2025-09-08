# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    liquidation_product_categ_ids = fields.Many2many(
        comodel_name='product.category',
        string='Categorías de Productos para Liquidación',
        related='company_id.liquidation_product_categ_ids',
        readonly=False,
        help="Seleccione las categorías de productos que serán elegibles para el proceso de 'Liquidación de Corte' en las Órdenes de Producción."
    )
    module_xtq_mrp_cut_liquidation = fields.Boolean(
        string='Activar Liquidación de Corte en Órdenes de Producción'
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    liquidation_product_categ_ids = fields.Many2many(
        comodel_name='product.category',
        string='Categorías de Productos para Liquidación por Defecto',
    )
