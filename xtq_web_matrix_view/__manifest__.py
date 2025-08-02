# -*- coding: utf-8 -*-
{
    'name': "XTQ - Framework de Vista Matriz Editable",
    'summary': "Introduce un nuevo tipo de vista 'matrix_editable' genérico y reutilizable en el framework de Odoo.",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'version': '18.0.1.0.0',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'xtq_web_matrix_view/static/src/matrix_view/matrix_view.js',
            'xtq_web_matrix_view/static/src/matrix_view/matrix_view.xml',
            'xtq_web_matrix_view/static/src/matrix_view/matrix_view.scss',
        ],
    },
    'license': 'OEEL-1',
} 