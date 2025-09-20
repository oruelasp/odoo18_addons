# -*- coding: utf-8 -*-
from odoo import api, models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # --- CAMPOS GENÉRICOS PARA ATRIBUTOS ---
    x_attr_1 = fields.Char(string="Atributo 1", compute='_compute_lot_attributes_data', store=False)
    x_attr_2 = fields.Char(string="Atributo 2", compute='_compute_lot_attributes_data', store=False)
    x_attr_3 = fields.Char(string="Atributo 3", compute='_compute_lot_attributes_data', store=False)
    x_attr_4 = fields.Char(string="Atributo 4", compute='_compute_lot_attributes_data', store=False)
    x_attr_5 = fields.Char(string="Atributo 5", compute='_compute_lot_attributes_data', store=False)
    x_attr_6 = fields.Char(string="Atributo 6", compute='_compute_lot_attributes_data', store=False)

    def _get_attributes_to_display(self):
        """ Determina qué atributos se deben mostrar, en un orden predecible. """
        product_id = self.env.context.get('lot_attributes_product_id')
        # La lógica se mantiene simple: todos los atributos de lote del sistema.
        # Podría extenderse para ser específico del producto si es necesario.
        return self.env['product.attribute'].search(
            [('is_lot_attribute', '=', True)], order='name', limit=6
        )

    def _compute_lot_attributes_data(self):
        """
        Calcula y asigna los valores de los atributos a los campos genéricos.
        Esta parte sigue siendo responsabilidad de Python por eficiencia.
        """
        attributes_to_display = self._get_attributes_to_display()
        lot_ids = self.mapped('lot_id')

        if not lot_ids or not attributes_to_display:
            for quant in self:
                for i in range(1, 7):
                    setattr(quant, f'x_attr_{i}', '')
            return

        attribute_data = self.env['stock.lot'].get_attributes_for_lots_view(lot_ids.ids)
        lot_values = attribute_data.get('data', {})

        for quant in self:
            if not quant.lot_id:
                for i in range(1, 7):
                    setattr(quant, f'x_attr_{i}', '')
                continue

            values_for_lot = lot_values.get(quant.lot_id.id, {})
            for i, attr in enumerate(attributes_to_display):
                field_name = f'x_attr_{i + 1}'
                value = values_for_lot.get(attr.name, '')
                setattr(quant, field_name, value)
            
            for i in range(len(attributes_to_display) + 1, 7):
                 setattr(quant, f'x_attr_{i}', '')

    @api.model
    def get_attribute_field_map(self, product_id):
        """
        Devuelve un mapeo de campos genéricos a nombres de atributos reales.
        Este método es llamado por JS para construir las cabeceras de las columnas.
        """
        # Usamos un contexto temporal para llamar al método helper
        context = dict(self.env.context, lot_attributes_product_id=product_id)
        attributes = self.with_context(context)._get_attributes_to_display()
        
        field_map = {}
        for i, attr in enumerate(attributes):
            field_name = f'x_attr_{i + 1}'
            field_map[field_name] = attr.display_name
            
        return field_map
