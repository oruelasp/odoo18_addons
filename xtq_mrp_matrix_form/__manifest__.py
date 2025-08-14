{
    'name': 'XTQ: Matriz de Producción X,Y',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Widget de matriz X,Y para entrada rápida  en Órdenes de Producción.',
    'author': 'xtqgroup',
    'website': 'https://www.xtqgroup.com', # Puedes poner tu sitio web aquí
    'depends': ['mrp', 'xtq_lot_attributes'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # El orden es importante: primero el JS, luego la plantilla XML
            'xtq_mrp_matrix_form/static/src/components/production_matrix_widget.js',
            'xtq_mrp_matrix_form/static/src/components/production_matrix_widget.xml',
        ],
    },
    'installable': True,
    'application': False, # Es un módulo que extiende una app, no una app nueva
    'license': 'LGPL-3',
}