# -*- coding: utf-8 -*-
{
    'name': "XTQ - Atributos de Calidad en Vista de Inventario",
    'summary': """
        Extiende la vista de selección de lotes (quants) para mostrar
        atributos de calidad del módulo xtq_lot_attributes como columnas dinámicas.""",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'website': "https://www.xtqgroup.com",
    'category': 'Inventory/Inventory',
    'version': '18.0.1.0.0',
    'depends': [
        'stock',
        'xtq_lot_attributes', # Dependencia del módulo de atributos
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/stock_move_views.xml',
        'views/stock_quant_views.xml', # Añadir la nueva vista
        'wizards/quant_attribute_selection_wizard_views.xml',
    ],
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            # Se elimina el archivo JS, ya no es necesario
            # 'xtq_quant_attributes/static/src/views/stock_quant_list_with_attributes_renderer.js',
        ],
    },
}
