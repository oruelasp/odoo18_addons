# -*- coding: utf-8 -*-
from odoo import api, fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    picking_ids = fields.One2many(
        'stock.picking',
        'workorder_id',
        string='Albaranes Relacionados'
    )
    
    picking_count = fields.Integer(
        string='Contador de Albaranes',
        compute='_compute_picking_count',
        store=True
    )
    
    has_related_pickings = fields.Boolean(
        string='Tiene Albaranes Relacionados',
        compute='_compute_has_related_pickings',
        store=True
    )

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for workorder in self:
            workorder.picking_count = len(workorder.picking_ids)
            
    @api.depends('picking_count')
    def _compute_has_related_pickings(self):
        for workorder in self:
            workorder.has_related_pickings = workorder.picking_count > 0

    def action_view_pickings(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('id', 'in', self.picking_ids.ids)]
        action['context'] = {'create': False}
        return action
