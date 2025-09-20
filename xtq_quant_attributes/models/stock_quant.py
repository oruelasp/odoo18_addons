# -*- coding: utf-8 -*-
from odoo import api, models, fields
from lxml import etree

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # --- CAMPOS GENÉRICOS PARA ATRIBUTOS ---
    # Usamos campos Char para máxima compatibilidad. Se pueden añadir más si es necesario.
    x_attr_1 = fields.Char(string="Atributo 1", compute='_compute_lot_attributes_data', store=False)
    x_attr_2 = fields.Char(string="Atributo 2", compute='_compute_lot_attributes_data', store=False)
    x_attr_3 = fields.Char(string="Atributo 3", compute='_compute_lot_attributes_data', store=False)
    x_attr_4 = fields.Char(string="Atributo 4", compute='_compute_lot_attributes_data', store=False)
    x_attr_5 = fields.Char(string="Atributo 5", compute='_compute_lot_attributes_data', store=False)
    x_attr_6 = fields.Char(string="Atributo 6", compute='_compute_lot_attributes_data', store=False)

    def _get_attributes_to_display(self):
        """
        Determina qué atributos se deben mostrar.
        Se basa en el contexto si está disponible, o en todos los atributos de lote como fallback.
        """
        product_id = self.env.context.get('lot_attributes_product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            # Podríamos filtrar por atributos específicos del producto si fuera necesario.
            # Por ahora, usamos todos los que son de tipo lote para consistencia.
        
        return self.env['product.attribute'].search([('is_lot_attribute', '=', True)], limit=6)

    def _compute_lot_attributes_data(self):
        """
        Calcula y asigna los valores de los atributos a los campos genéricos.
        """
        attributes_to_display = self._get_attributes_to_display()
        lot_ids = self.mapped('lot_id')

        if not lot_ids or not attributes_to_display:
            for quant in self:
                for i in range(1, 7):
                    setattr(quant, f'x_attr_{i}', '')
            return

        # Usamos el método existente para obtener todos los datos en una sola consulta
        attribute_data = self.env['stock.lot'].get_attributes_for_lots_view(lot_ids.ids)
        lot_values = attribute_data.get('data', {})

        for quant in self:
            values_for_lot = lot_values.get(quant.lot_id.id, {})
            for i, attr in enumerate(attributes_to_display):
                field_name = f'x_attr_{i + 1}'
                value = values_for_lot.get(attr.name, '')
                setattr(quant, field_name, value)
            # Limpiar los campos restantes
            for i in range(len(attributes_to_display) + 1, 7):
                 setattr(quant, f'x_attr_{i}', '')

    @api.model
    def fields_view_get(self, view_id=None, view_type='list', toolbar=False, submenu=False):
        """
        Intercepta la construcción de la vista para cambiar las etiquetas de las columnas
        y ocultar las que no se usan.
        """
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        if view_type == 'list' and self.env.context.get('show_lot_attributes'):
            attributes_to_display = self._get_attributes_to_display()
            
            doc = etree.XML(res['arch'])
            
            # Cambiar etiquetas y visibilidad de las columnas genéricas
            for i, attr in enumerate(attributes_to_display):
                field_node = doc.find(f".//field[@name='x_attr_{i + 1}']")
                if field_node is not None:
                    field_node.set('string', attr.name)
                    # Eliminamos el 'invisible' por si estaba en la vista base
                    if 'invisible' in field_node.attrib:
                        del field_node.attrib['invisible']
            
            # Ocultar las columnas genéricas que no se están usando
            for i in range(len(attributes_to_display) + 1, 7):
                field_node = doc.find(f".//field[@name='x_attr_{i + 1}']")
                if field_node is not None:
                    field_node.set('invisible', '1')

            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res
