# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ImportFromOpWizard(models.TransientModel):
    _name = 'import.from.op.wizard'
    _description = 'Asistente para Importar Componentes desde OP'

    production_id = fields.Many2one(
        'mrp.production',
        string='Orden de Producción',
        required=True,
        domain="[('state', 'in', ('confirmed', 'planned', 'progress', 'to_close'))]"
    )
    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Orden de Trabajo',
        domain="[('production_id', '=', production_id)]"
    )
    line_ids = fields.One2many(
        'import.from.op.wizard.line',
        'wizard_id',
        string='Componentes a Importar'
    )

    @api.onchange('production_id', 'workorder_id')
    def _onchange_production_workorder(self):
        """
        Al cambiar la Orden de Producción o la Orden de Trabajo, se pueblan
        las líneas de componentes correspondientes.
        """
        self.line_ids = [(5, 0, 0)]  # Limpiar líneas existentes
        
        if not self.production_id:
            return

        moves = self.production_id.move_raw_ids
        if self.workorder_id:
            # Intentar limitar por la operación asociada a la OT si existe en los movimientos
            operation = getattr(self.workorder_id, 'operation_id', False)
            if operation and 'operation_id' in moves._fields:
                filtered = moves.filtered(lambda m: m.operation_id == operation)
                if filtered:
                    moves = filtered

        lines_to_create = []
        for move in moves:
            lines_to_create.append((0, 0, {
                'product_id': move.product_id.id,
                'planned_qty': move.product_uom_qty,
                'quantity_to_move': move.product_uom_qty,
                'product_uom_id': move.product_uom.id,
            }))
        
        self.line_ids = lines_to_create

    def action_import_lines(self):
        """
        Acción principal que importa las líneas seleccionadas del wizard
        a la transferencia de inventario activa.
        """
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if not picking:
            raise UserError(_("No se pudo encontrar la transferencia de inventario activa."))

        lines_to_import = self.line_ids.filtered('selected')
        if not lines_to_import:
            raise UserError(_("No ha seleccionado ninguna línea para importar."))

        # 1. Crear movimientos de stock
        for line in lines_to_import:
            self.env['stock.move'].create({
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity_to_move,
                'product_uom': line.product_uom_id.id,
                'name': line.product_id.display_name,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })
        
        # 2. Concatenar origen de OP evitando duplicados y normalizando espacios
        def _concat_unique(existing, new):
            tokens = [t.strip() for t in (existing or '').split(',') if t.strip()]
            if new not in tokens:
                tokens.append(new)
            return ', '.join(tokens)

        picking.origin = _concat_unique(picking.origin, self.production_id.name)

        # 3. Concatenar origen de OT (si aplica)
        if self.workorder_id:
            picking.workorder_origin = _concat_unique(getattr(picking, 'workorder_origin', False), self.workorder_id.name)

        # 4. Propagar proyecto (solo si el campo existe y está vacío)
        if 'project_id' in picking._fields and self.production_id.project_id and not picking.project_id:
            picking.project_id = self.production_id.project_id.id

        return {'type': 'ir.actions.act_window_close'}


class ImportFromOpWizardLine(models.TransientModel):
    _name = 'import.from.op.wizard.line'
    _description = 'Línea de Componente para Asistente de Importación desde OP'

    wizard_id = fields.Many2one('import.from.op.wizard', string='Asistente', required=True, ondelete='cascade')
    selected = fields.Boolean(string='Seleccionar', default=True)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    planned_qty = fields.Float(string='Cantidad Prevista', digits='Product Unit of Measure', readonly=True)
    quantity_to_move = fields.Float(string='Cantidad a Mover', digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UdM', readonly=True)
