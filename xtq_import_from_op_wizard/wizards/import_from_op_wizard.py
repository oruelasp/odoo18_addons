# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ImportFromOpWizard(models.TransientModel):
    _name = 'import.from.op.wizard'
    _description = 'Asistente para Importar Producto Terminado desde OP'

    picking_id = fields.Many2one('stock.picking', string='Transferencia', readonly=True)
    production_id = fields.Many2one(
        'mrp.production',
        string='Orden de Producción',
        required=True,
        domain="[('state', 'in', ('confirmed', 'planned', 'progress', 'to_close'))]"
    )
    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Orden de Trabajo',
        domain="[('production_id', '=', production_id), ('state', 'not in', ('done', 'cancel'))]"
    )
    line_ids = fields.One2many(
        'import.from.op.wizard.line',
        'wizard_id',
        string='Producto a Importar'
    )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and 'picking_id' in self._fields:
            vals.setdefault('picking_id', active_id)
        return vals

    def action_load_product(self):
        self.ensure_one()
        if not self.production_id:
            raise UserError(_("Seleccione primero una Orden de Producción."))
        
        commands = [(5, 0, 0)]  # Limpiar líneas existentes
        
        production = self.production_id
        commands.append((0, 0, {
            'product_id': production.product_id.id,
            'planned_qty': production.product_qty,
            'quantity_to_move': production.qty_producing,
            'product_uom_id': production.product_uom_id.id,
        }))
        
        self.line_ids = commands
        
        # Mantener el modal abierto y conservar active_id del picking
        ctx = dict(self.env.context)
        if self.picking_id:
            ctx.update({'active_id': self.picking_id.id, 'active_model': 'stock.picking'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.from.op.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('production_id')
    def _onchange_production_workorder(self):
        return

    def action_import_lines(self):
        self.ensure_one()
        picking = self.picking_id or self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if not picking:
            raise UserError(_("No se pudo encontrar la transferencia de inventario activa."))

        if not self.line_ids:
            self.action_load_product()

        lines_to_import = self.line_ids.filtered(
            lambda l: l.selected and l.product_id and l.product_uom_id and l.quantity_to_move > 0
        )

        if not lines_to_import:
            raise UserError(_("No hay líneas válidas para importar. Verifique selección y cantidades."))

        commands = []
        for line in lines_to_import:
            commands.append((0, 0, {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'product_uom_qty': line.quantity_to_move,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'company_id': picking.company_id.id,
            }))
        picking.write({'move_ids': commands})
        _logger.info("Insertadas %s líneas en picking %s mediante move_ids write", len(commands), picking.name)

        # 2. Asignar origen de OP (sobrescribiendo)
        picking.origin = self.production_id.name

        # 3. Asignar Orden de Trabajo (sobrescribiendo)
        if self.workorder_id:
            picking.workorder_id = self.workorder_id.id
        else:
            picking.workorder_id = False

        # 4. Propagar proyecto (solo si está vacío)
        if 'project_id' in picking._fields and self.production_id.project_id and not picking.project_id:
            picking.project_id = self.production_id.project_id.id

        return {'type': 'ir.actions.act_window_close'}


class ImportFromOpWizardLine(models.TransientModel):
    _name = 'import.from.op.wizard.line'
    _description = 'Línea de Producto para Asistente de Importación desde OP'

    wizard_id = fields.Many2one('import.from.op.wizard', string='Asistente', required=True, ondelete='cascade')
    selected = fields.Boolean(string='Seleccionar', default=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    planned_qty = fields.Float(string='Cantidad Programada', digits='Product Unit of Measure', readonly=True)
    quantity_to_move = fields.Float(string='Cantidad a Mover', digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UdM', readonly=True)
