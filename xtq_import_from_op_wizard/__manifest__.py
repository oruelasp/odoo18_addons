# -*- coding: utf-8 -*-
{
    'name': 'XTQ | Asistente para Importar desde OP',
    'version': '18.0.1.0.1',
    'category': 'Inventory/Inventory',
    'summary': 'Permite a los usuarios crear transferencias de inventario importando componentes desde Órdenes de Producción.',
    'author': 'XTQ Group',
    'website': 'https://www.xtqgroup.com',
    'depends': [
        'stock',
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/import_from_op_wizard_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False
}