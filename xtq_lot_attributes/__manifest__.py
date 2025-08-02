# -*- coding: utf-8 -*-
{
    'name': "Atributos para Lotes/Números de Serie (XTQ)",
    'summary': "Permite registrar un conjunto de atributos y valores personalizables en lotes y números de serie.",
    'description': "Este módulo extiende la funcionalidad de seguimiento por lotes de Odoo, permitiendo a los usuarios definir y registrar un conjunto de atributos específicos para cada lote o número de serie. CARACTERÍSTICAS PRINCIPALES: - Añade una nueva pestaña 'Atributos' en el formulario de Lote/Nº de Serie. - Tabla flexible para añadir un número ilimitado de atributos por lote. - Reutiliza el modelo nativo de Atributos y Valores de Odoo (product.attribute). - Incluye un campo para marcar atributos específicos para lotes. - Proporciona un menú de configuración dedicado en Inventario para administrar todas las líneas de atributos. BENEFICIOS: - Mejora drásticamente la trazabilidad y la caracterización de productos. - Flexible y adaptable a cualquier industria. - Se integra de forma nativa con la lógica de Odoo.",
    'author': "XTQ GROUP (Liderado por: Omar Ruelas Principe)",
    'website': "https://www.xtqgroup.com",
    'category': 'Inventory/Inventory',
    'version': '18.0.3.0.0',
    'depends': [
        'stock',
        'product'
    ],
    'data': [
        'security/ir.model.access.csv',
        #'views/stock_lot_attribute_line_views.xml',
        'views/stock_lot_views.xml',
        'views/product_attribute_views.xml',
    ],
    'license': 'OEEL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}