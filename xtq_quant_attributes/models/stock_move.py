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
            line_vals = {'quant_id': quant.id}
            # Mapear valores de atributos a columnas genéricas
            for i, attr in enumerate(lot_attributes):
                attr_line = quant.lot_id.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == attr
                )
                field_name = f'attr_col_{i + 1}'
                line_vals[field_name] = attr_line.value_id.name if attr_line else ''
            wizard_lines_vals.append(line_vals)

        # 4. Crear el wizard y sus líneas
        wizard = self.env['quant.attribute.selection.wizard'].create({
            'move_id': self.id,
            'line_ids': [(0, 0, vals) for vals in wizard_lines_vals]
        })

        # 5. Generar la vista de formulario/lista dinámica
        arch_base = """
            <form string="Seleccionar Lotes por Atributos">
                <sheet>
                    <field name="line_ids" nolabel="1">
                        <list editable="bottom">
                            <field name="selected"/>
                            <field name="lot_id"/>
                            <field name="location_id"/>
                            <field name="available_quantity"/>
                            <field name="quantity_to_reserve"/>
                            <field name="product_uom_id" string="UdM"/>
                            {dynamic_fields}
                        </list>
                    </field>
                </sheet>
                <footer>
                    <button name="action_confirm_selection" string="Confirmar Selección" type="object" class="btn-primary"/>
                    <button string="Cancelar" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        """
        dynamic_fields_str = ""
        for i, attr in enumerate(lot_attributes):
            field_name = f'attr_col_{i + 1}'
            dynamic_fields_str += f'<field name="{field_name}" string="{attr.name}"/>'

        view_arch = arch_base.format(dynamic_fields=dynamic_fields_str)

        # 6. Crear la vista ir.ui.view temporal
        view = self.env['ir.ui.view'].create({
            'name': 'dynamic.quant.attribute.selection.form',
            'type': 'form',
            'model': 'quant.attribute.selection.wizard',
            'arch': view_arch,
        })

        # 7. Devolver la acción
        return {
            'name': 'Seleccionar Lotes por Atributos',
            'type': 'ir.actions.act_window',
            'res_model': 'quant.attribute.selection.wizard',
            'views': [[view.id, 'form']],
            'res_id': wizard.id,
            'target': 'current',  # Abrir en la vista principal
        }
