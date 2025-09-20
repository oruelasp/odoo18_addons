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
            
            # Limpiar campos 'x_attr_' existentes que podrían ser de una ejecución anterior
            self.env['ir.model.fields'].search([
                ('model', '=', 'stock.quant'),
                ('name', 'like', 'x_attr_')
            ]).unlink()

            doc = etree.XML(res['arch'])
            parent_node = doc.find('.//list')
            if parent_node is None:
                 parent_node = doc.find('.//tree')
            if parent_node is None:
                return res
            
            ref_node = parent_node.find(".//field[@name='lot_id']")
            if ref_node is not None:
                for attr in reversed(lot_attributes):
                    field_name = self._sanitize_header_for_field_name(attr.name)
                    # Crear el campo en el modelo ir.model.fields
                    self.env['ir.model.fields'].create({
                        'name': field_name,
                        'model_id': self.env['ir.model']._get_id('stock.quant'),
                        'ttype': 'char',
                        'string': attr.name,
                        'readonly': True,
                    })
                    # Añadir el campo a la arquitectura de la vista
                    new_node = etree.Element('field', name=field_name, string=attr.name, readonly="1", optional="hide")
                    ref_node.addnext(new_node)
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res
    
    # Se elimina la sobrecarga de search_read ya que los datos se manejarán en JS.
