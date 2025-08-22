# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

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

    def _get_moves_source(self):
        self.ensure_one()
        # La OT es referencial: no filtra ni modifica los componentes cargados
        return self.production_id.move_raw_ids

    def action_load_components(self):
        self.ensure_one()
        if not self.production_id:
            raise UserError(_("Seleccione primero una Orden de Producción."))
        moves = self._get_moves_source()
        commands = [(5, 0, 0)]
        for move in moves:
            commands.append((0, 0, {
                'product_id': move.product_id.id,
                'planned_qty': move.product_uom_qty,
                'quantity_to_move': move.product_uom_qty,
                'product_uom_id': move.product_uom.id,
            }))
        self.line_ids = commands
        # Mantener el modal abierto recargando el mismo registro
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.from.op.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.onchange('production_id')
    def _onchange_production_workorder(self):
        # No recargar automáticamente; el usuario usará el botón "Cargar Componentes"
        return

    def action_import_lines(self):
        """
        Acción principal que importa las líneas seleccionadas del wizard
        a la transferencia de inventario activa.
        """
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if not picking:
            raise UserError(_("No se pudo encontrar la transferencia de inventario activa."))

        if not self.line_ids:
            # Cargar si aún no se ha hecho
            self.action_load_components()

        # Filtrar solo líneas válidas: seleccionadas, con producto/UdM y cantidad > 0
        lines_to_import = self.line_ids.filtered(
            lambda l: l.selected and l.product_id and l.product_uom_id and l.quantity_to_move > 0
        )
        
        _logger.info(
            "Asistente: Importando %s líneas desde OP %s para el picking %s",
            len(lines_to_import), self.production_id.name, picking.name
        )

        if not lines_to_import:
            raise UserError(_("No hay líneas válidas para importar. Verifique selección y cantidades."))

        # 1. Crear movimientos de stock únicamente con datos completos
        move_vals = []
        for line in lines_to_import:
            move_vals.append({
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity_to_move,
                'product_uom': line.product_uom_id.id,
                'name': line.product_id.display_name,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
            })
        self.env['stock.move'].create(move_vals)
        
        # 2. Concatenar origen de OP evitando duplicados y normalizando espacios
        def _concat_unique(existing, new):
            tokens = [t.strip() for t in (existing or '').split(',') if t.strip()]
            if new not in tokens:
                tokens.append(new)
            return ', '.join(tokens)

        picking.origin = _concat_unique(picking.origin, self.production_id.name)

        # 3. Concatenar origen de OT (si aplica). Es referencial, no afecta componentes
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
