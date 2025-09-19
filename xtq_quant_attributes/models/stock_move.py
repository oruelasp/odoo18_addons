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
        
        # 1. Obtener todos los atributos marcados como "de lote"
        lot_attributes = self.env['product.attribute'].search([
            ('is_lot_attribute', '=', True)
        ])
        
        # 2. Reunir quants disponibles para el producto y ubicación
        available_quants = self.env['stock.quant']._gather(
            self.product_id,
            self.location_id,
            strict=False
        ).filtered(lambda q: q.quantity > 0)

        # 3. Crear (si no existen) los campos dinámicos en el modelo de líneas del wizard
        LineModel = self.env['quant.attribute.selection.line']
        attr_to_field = {}
        for attr in lot_attributes:
            # Generar nombre técnico seguro del campo (sin prefijo x_)
            fname = re.sub(r'[^a-z0-9_]', '_', attr.name.lower())
            if not fname or fname[0].isdigit():
                fname = f'_{fname}'
            fname = f"attr_{fname}"
            attr_to_field[attr.id] = fname
            if fname not in LineModel._fields:
                LineModel._add_field(fname, fields.Char(string=attr.display_name, readonly=True))

        # 4. Construir la arquitectura de la vista usando los nombres técnicos
        extra_columns = " ".join([
            f"<field name='{attr_to_field[attr.id]}' string='{attr.display_name}'/>" for attr in lot_attributes
        ])
        arch_string = f"""
            <form>
                <sheet>
                    <field name='quant_line_ids' nolabel='1'>
                        <list editable='bottom'>
                            <field name='selected'/>
                            <field name='lot_id'/>
                            <field name='location_id'/>
                            <field name='quantity'/>
                            <field name='product_uom_id'/>
                            {extra_columns}
                        </list>
                    </field>
                </sheet>
                <footer>
                    <button string=\"Confirmar\" type=\"object\" name=\"action_confirm\" class=\"oe_highlight\"/>
                    <button string=\"Cancelar\" class=\"btn-secondary\" special=\"cancel\"/>
                </footer>
            </form>
        """

        # 5. Preparar líneas del wizard con valores de atributos
        wizard_lines = []
        for quant in available_quants:
            line_vals = {'quant_id': quant.id}
            if quant.lot_id:
                for attr in lot_attributes:
                    fname = attr_to_field[attr.id]
                    attr_line = quant.lot_id.attribute_line_ids.filtered(lambda l: l.attribute_id == attr)
                    value = attr_line.value_id.name if attr_line else ''
                    line_vals[fname] = value
            wizard_lines.append((0, 0, line_vals))

        # 6. Crear el wizard y la vista dinámica
        wizard = self.env['quant.attribute.selection.wizard'].create({
            'quant_line_ids': wizard_lines,
        })
        view = self.env['ir.ui.view'].create({
            'name': 'dynamic_quant_attr_wizard_view',
            'type': 'form',
            'model': 'quant.attribute.selection.wizard',
            'arch': arch_string,
        })

        return {
            'name': 'Seleccionar Lotes por Atributos',
            'type': 'ir.actions.act_window',
            'res_model': 'quant.attribute.selection.wizard',
            'views': [[view.id, 'form']],
            'res_id': wizard.id,
            'target': 'new',
        }
