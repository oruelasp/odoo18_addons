# -*- coding: utf-8 -*-
from odoo import api, fields, models
from lxml import etree

class StockQuantAttributeSelectionWizard(models.TransientModel):
    _name = 'stock.quant.attribute.selection.wizard'
    _description = 'Asistente para Seleccionar Lotes por Atributos de Calidad'

    # Campo para vincular con el movimiento de stock original
    move_id = fields.Many2one('stock.move', string="Movimiento")
    
    # Lotes disponibles para la selección
    quant_ids = fields.Many2many(
        'stock.quant', 
        string="Lotes Disponibles",
        compute='_compute_quant_ids',
        readonly=False, # Permitir la selección en la vista
    )

    @api.depends('move_id')
    def _compute_quant_ids(self):
        """
        Calcula los quants (lotes) disponibles para el producto y ubicación
        del movimiento de stock asociado.
        """
        for wizard in self:
            if wizard.move_id:
                product = wizard.move_id.product_id
                location = wizard.move_id.location_id
                
                # Buscar quants disponibles en la ubicación de origen
                available_quants = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', location.id),
                    ('quantity', '>', 0),
                    ('lot_id', '!=', False),
                ])
                wizard.quant_ids = [(6, 0, available_quants.ids)]
            else:
                wizard.quant_ids = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockQuantAttributeSelectionWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        # Forzar que los strings de la vista se recalculen para que las cabeceras sean dinámicas
        res['arch'] = self.env['ir.qweb']._render(res['arch'], {'_force_dynamic_string': True})
        return res

    def action_apply_selection(self):
        """
        Toma los lotes seleccionados en el wizard y los aplica como
        líneas de movimiento en el 'stock.move' original.
        """
        self.ensure_one()
        move = self.move_id
        
        # Eliminar las líneas de movimiento existentes para este move
        move.move_line_ids.unlink()

        # Crear nuevas líneas de movimiento para cada quant seleccionado
        for quant in self.quant_ids:
            # La cantidad a mover es la cantidad demandada o la disponible en el lote
            move_qty = min(move.product_uom_qty - sum(move.move_line_ids.mapped('quantity')), quant.quantity)
            if move_qty <= 0:
                continue

            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'lot_id': quant.lot_id.id,
                'quantity': move_qty,
                'product_uom_id': move.product_uom.id,
            })
        
        return {'type': 'ir.actions.act_window_close'}
