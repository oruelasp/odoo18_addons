# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
import re

class StockMove(models.Model):
    _inherit = 'stock.move'

    show_quality_attrs_button = fields.Boolean(
        compute='_compute_show_quality_attrs_button'
    )

    def _compute_show_quality_attrs_button(self):
        for move in self:
            move.show_quality_attrs_button = (
                move.has_tracking != 'none' and
                move.product_id.show_quality_attrs_in_picking
            )

    def action_show_attribute_selection(self):
        self.ensure_one()
        
        lot_attributes = self.env['product.attribute'].search([
            ('is_lot_attribute', '=', True)
        ])
        available_quants = self.env['stock.quant']._gather(
            self.product_id,
            self.location_id,
            strict=False
        ).filtered(lambda q: q.quantity > 0)

        # Construir tabla HTML segura
        headers = [
            'Lote', 'Ubicación', 'Cantidad', 'UoM'
        ] + [attr.display_name for attr in lot_attributes]

        def td(val):
            return f"<td>{(val or '')}</td>"

        rows_html = []
        for quant in available_quants:
            base_cols = [
                quant.lot_id.name if quant.lot_id else '',
                quant.location_id.display_name,
                quant.quantity,
                quant.product_uom_id.name or ''
            ]
            attr_cols = []
            for attr in lot_attributes:
                attr_line = quant.lot_id.attribute_line_ids.filtered(lambda l: l.attribute_id == attr) if quant.lot_id else False
                attr_cols.append(attr_line.value_id.name if attr_line else '')
            row_html = '<tr>' + ''.join([td(v) for v in base_cols + attr_cols]) + '</tr>'
            rows_html.append(row_html)

        table_html = (
            '<table class="table table-sm table-striped">'
            '<thead><tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr></thead>'
            '<tbody>' + ''.join(rows_html) + '</tbody>'
            '</table>'
        )

        wizard = self.env['quant.attribute.selection.wizard'].create({
            'html_table': table_html,
        })

        # Vista mínima que muestra el HTML
        arch_string = """
            <form string="Atributos de Lotes">
                <sheet>
                    <div class="oe_title"><h2>Atributos de Calidad</h2></div>
                    <field name="html_table" nolabel="1"/>
                </sheet>
                <footer>
                    <button string="Cerrar" special="cancel" class="btn-secondary"/>
                </footer>
            </form>
        """

        view = self.env['ir.ui.view'].create({
            'name': 'dynamic_quant_attr_wizard_view_html',
            'type': 'form',
            'model': 'quant.attribute.selection.wizard',
            'arch': arch_string,
        })

        return {
            'name': 'Atributos de Lotes',
            'type': 'ir.actions.act_window',
            'res_model': 'quant.attribute.selection.wizard',
            'views': [[view.id, 'form']],
            'res_id': wizard.id,
            'target': 'new',
        }
