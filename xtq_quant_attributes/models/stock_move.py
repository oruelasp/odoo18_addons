# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare

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
        
        # 1. Encontrar atributos de calidad para este producto
        # Corrección: El campo en product.attribute es 'product_tmpl_ids' (Many2many), no 'product_tmpl_id'.
        lot_attributes = self.env['product.attribute'].search([
            ('is_lot_attribute', '=', True),
            ('product_tmpl_ids', 'in', self.product_id.product_tmpl_id.id)
        ])
        if not lot_attributes:
            # Si no hay atributos, no hacemos nada especial (o podríamos mostrar un mensaje)
            return

        # 2. Encontrar quants disponibles
        available_quants = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', 'child_of', self.location_id.id),
            ('quantity', '>', 0),
        ])

        # 3. Construir la arquitectura de la vista de lista dinámicamente
        arch_string = """
            <form>
                <sheet>
                    <field name='quant_line_ids' nolabel='1'>
                        <list editable='bottom'>
                            <field name='selected'/>
                            <field name='lot_id'/>
                            <field name='location_id'/>
                            <field name='quantity'/>
                            <field name='product_uom_id'/>
                            {}
                        </list>
                    </field>
                </sheet>
                <footer>
                    <button string="Confirmar" type="object" name="action_confirm" class="oe_highlight"/>
                    <button string="Cancelar" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        """.format(" ".join([
            f"<field name='{attr.name}'/>" for attr in lot_attributes
        ]))
        
        # 4. Crear las líneas del asistente y añadir los valores de los atributos
        wizard_lines = []
        for quant in available_quants:
            line_vals = {'quant_id': quant.id}
            for attr in lot_attributes:
                # Buscar el valor del atributo para el lote del quant
                attr_line = quant.lot_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attr
                )
                # Odoo no permite escribir directamente en campos related/compute en un create.
                # En su lugar, lo añadiremos a la vista dinámica.
                # Por ahora, solo creamos la línea base.
            wizard_lines.append((0, 0, line_vals))
        
        # 5. Añadir dinámicamente los campos de atributos al modelo
        LineModel = self.env['quant.attribute.selection.line']
        for attr in lot_attributes:
            if attr.name not in LineModel._fields:
                field = fields.Char(
                    string=attr.display_name,
                    compute='_compute_attribute_value',
                    store=False,
                )
                LineModel._add_field(attr.name, field)
                # Pasamos el nombre del campo en el contexto para el compute
                LineModel = LineModel.with_context(field_name_compute=attr.name)

        # 6. Crear el wizard y devolver la acción para abrirlo
        wizard = self.env['quant.attribute.selection.wizard'].create({
            'quant_line_ids': wizard_lines,
        })

        # 7. Crear una vista dinámica para el wizard
        view = self.env['ir.ui.view'].create({
            'name': 'dynamic_wizard_view',
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
