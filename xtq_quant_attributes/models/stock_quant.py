# -*- coding: utf-8 -*-
from odoo import api, models
from lxml import etree

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _sanitize_header_for_field_name(self, header):
        """Convierte un string en un nombre de campo válido."""
        return f"x_attr_{''.join(c if c.isalnum() else '_' for c in header)}"

    @api.model
    def _get_lot_attributes_for_product(self, product_id):
        """Obtiene los atributos de tipo lote para un producto específico."""
        if not product_id:
            return self.env['product.attribute']
        
        product = self.env['product.product'].browse(product_id)
        # Se buscan los atributos que son de tipo 'lote' en la configuración general.
        return self.env['product.attribute'].search([
            ('is_lot_attribute', '=', True)
        ])

    @api.model
    def fields_view_get(self, view_id=None, view_type='list', toolbar=False, submenu=False):
        """
        Intercepta la construcción de la vista para inyectar las columnas de atributos.
        """
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        if view_type == 'list' and self.env.context.get('show_lot_attributes'):
            product_id = self.env.context.get('lot_attributes_product_id')
            if not product_id:
                return res

            lot_attributes = self._get_lot_attributes_for_product(product_id)
            if not lot_attributes:
                return res

            doc = etree.XML(res['arch'])
            # Prioritize <list> for Odoo 18+, fallback to <tree> for compatibility
            parent_node = doc.find('.//list')
            if parent_node is None:
                 parent_node = doc.find('.//tree')
            if parent_node is None:
                return res
            
            # Elige un campo de referencia para insertar las columnas después (ej. lot_id)
            ref_node = parent_node.find(".//field[@name='lot_id']")
            if ref_node is not None:
                # Insertar columnas en orden inverso para mantener el orden original
                for attr in reversed(lot_attributes):
                    field_name = self._sanitize_header_for_field_name(attr.name)
                    new_node = etree.Element('field', name=field_name, string=attr.name, readonly="1")
                    ref_node.addnext(new_node)
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Intercepta la lectura de datos para inyectar los valores de los atributos.
        """
        records = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        
        if self.env.context.get('show_lot_attributes') and records:
            product_id = self.env.context.get('lot_attributes_product_id')
            lot_attributes = self._get_lot_attributes_for_product(product_id)
            if not lot_attributes:
                return records

            lot_ids = [rec['lot_id'][0] for rec in records if rec.get('lot_id')]
            if not lot_ids:
                return records

            attribute_data = self.env['stock.lot'].get_attributes_for_lots_view(lot_ids)
            lot_values = attribute_data.get('data', {})

            for rec in records:
                lot_id = rec.get('lot_id') and rec['lot_id'][0]
                if lot_id in lot_values:
                    for attr in lot_attributes:
                        field_name = self._sanitize_header_for_field_name(attr.name)
                        rec[field_name] = lot_values[lot_id].get(attr.name, '')
                else:
                    for attr in lot_attributes:
                        field_name = self._sanitize_header_for_field_name(attr.name)
                        rec[field_name] = ''
        
        return records
