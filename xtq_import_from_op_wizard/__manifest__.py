{
    'name': 'XTQ | Asistente para Importar desde OP',
    'summary': 'Permite a los usuarios crear transferencias de inventario importando componentes desde Órdenes de Producción.',
    'version': '18.0.1.0.1',
    'category': 'Inventory/Inventory',
    'author': 'XTQ Group',
    'website': 'https://www.xtqgroup.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'wizards/import_from_op_wizard_views.xml',
    ],
    'application': False,
    'installable': True,
}

