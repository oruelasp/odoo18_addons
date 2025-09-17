# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

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
        
    def button_finish(self):
        """
        Hereda el método para finalizar una OT y añade la lógica de validación de albaranes.
        """
        ICP = self.env['ir.config_parameter'].sudo()
        restriction = ICP.get_param('xtq_import_from_op_wizard.workorder_picking_restriction', 'none')

        if restriction == 'none':
            return super(MrpWorkorder, self).button_finish()

        for workorder in self:
            if not workorder.has_related_pickings:
                raise UserError(_("Esta orden de trabajo no se puede finalizar porque no tiene ningún albarán relacionado."))

            picking_types = workorder.picking_ids.mapped('picking_type_id.code')
            has_incoming = 'incoming' in picking_types
            has_outgoing = 'outgoing' in picking_types
            
            if restriction == 'one_step':
                if not has_incoming and not has_outgoing:
                    raise UserError(_("Para finalizar esta orden de trabajo se requiere al menos un albarán de tipo 'Entrada' o 'Salida'. Actualmente, solo existen movimientos internos o ningún movimiento de este tipo."))

            elif restriction == 'two_steps':
                if not has_incoming or not has_outgoing:
                    raise UserError(_("Para finalizar esta orden de trabajo se requiere al menos un albarán de tipo 'Entrada' Y uno de tipo 'Salida'. Falta uno o ambos tipos."))
        
        return super(MrpWorkorder, self).button_finish()
