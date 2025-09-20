# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


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

        # 1. Encontrar atributos de lote
        lot_attributes = self.env['product.attribute'].search([
            ('is_lot_attribute', '=', True)
        ])
        if not lot_attributes:
            raise UserError("No se han configurado atributos de calidad de tipo 'lote' en el sistema.")

        # Limitar a un máximo de 5 para coincidir con los campos genéricos del wizard
        lot_attributes = lot_attributes[:5]

        # 2. Encontrar quants disponibles
        available_quants = self.env['stock.quant']._gather(
            self.product_id,
            self.location_id,
            strict=False
        ).filtered(lambda q: q.quantity > 0 and q.lot_id)  # Asegurarse de que tengan lote

        if not available_quants:
            raise UserError("No se encontraron lotes/números de serie disponibles para este producto en la ubicación de origen.")

        # 3. Preparar los datos para las líneas del wizard
        wizard_lines_vals = []
        for quant in available_quants:
            line_vals = {
                'quant_id': quant.id,
                'selection_status': 'available',
            }
            for i, attr in enumerate(lot_attributes):
                attr_line = quant.lot_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attr
                )
                field_name = f'attr_col_{i + 1}'
                line_vals[field_name] = attr_line.value_id.name if attr_line else ''
            wizard_lines_vals.append((0, 0, line_vals))
        
        # 4. Preparar los filtros de búsqueda
        search_filters_vals = []
        for attr in lot_attributes:
            search_filters_vals.append((0, 0, {'attribute_id': attr.id}))

        # 5. Crear el wizard. La lista de líneas se deja vacía intencionadamente.
        # El usuario debe buscar activamente los lotes que desea ver.
        wizard = self.env['quant.attribute.selection.wizard'].create({
            'move_id': self.id,
            'line_ids': [],
            'search_filter_ids': search_filters_vals,
        })

        # 6. Generar la vista dinámica que hereda de la base
        
        # Definición de la lista base para reutilizar
        list_view_arch = """
            <list editable="bottom">
                <field name="selected"/>
                <field name="lot_id"/>
                <field name="location_id"/>
                <field name="available_quantity"/>
                <field name="quantity_to_reserve"/>
                <field name="product_uom_id" string="UdM"/>
                {dynamic_fields}
            </list>
        """
        dynamic_fields_str = ""
        for i, attr in enumerate(lot_attributes):
            field_name = f'attr_col_{i + 1}'
            dynamic_fields_str += f'<field name="{field_name}" string="{attr.name}"/>'
        
        final_list_arch = list_view_arch.format(dynamic_fields=dynamic_fields_str)

        # Usamos XPATH para inyectar las listas en los placeholders
        view_arch = f"""
            <data>
                <xpath expr="//div[@id='available_lines_placeholder']" position="replace">
                    <field name="line_ids" nolabel="1" domain="[('selection_status', '=', 'available'), ('is_visible_in_search', '=', True)]">
                        {final_list_arch}
                    </field>
                </xpath>
                <xpath expr="//div[@id='selected_lines_placeholder']" position="replace">
                    <field name="line_ids" nolabel="1" domain="[('selection_status', '=', 'selected')]">
                         {final_list_arch}
                    </field>
                </xpath>
            </data>
        """

        # 7. Crear la vista ir.ui.view que hereda de la vista base
        base_view_id = self.env.ref('xtq_quant_attributes.view_quant_attribute_selection_wizard_form').id
        view = self.env['ir.ui.view'].create({
            'name': 'dynamic.quant.attribute.selection.form.inherit',
            'type': 'form',
            'model': 'quant.attribute.selection.wizard',
            'inherit_id': base_view_id,
            'arch': view_arch,
            'mode': 'primary',
        })

        # 8. Devolver la acción
        return {
            'name': 'Seleccionar Lotes por Atributos',
            'type': 'ir.actions.act_window',
            'res_model': 'quant.attribute.selection.wizard',
            'views': [[view.id, 'form']],
            'res_id': wizard.id,
            'target': 'current',
        }

    def action_open_stock_quant_list(self):
        self.ensure_one()
        return {
            'name': f"Stock Disponible para: {self.product_id.display_name}",
            'type': 'ir.actions.act_window',
            'res_model': 'stock.quant',
            'view_mode': 'list,form',
            'domain': [
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', self.location_id.id),
                ('quantity', '>', 0),
            ],
            'target': 'current',
        }
