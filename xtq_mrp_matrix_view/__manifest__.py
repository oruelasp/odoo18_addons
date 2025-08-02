# __manifest__.py
# -*- coding: utf-8 -*-
{
    'name': "XTQ - Vista Matriz para Planificación de Corte",
    'summary': "Implementa la vista de matriz editable para las Órdenes de Producción.",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'version': '18.0.1.0.0',
    'depends': [
        'mrp',
        'xtq_web_matrix_view',
    ],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'license': 'OEEL-1',
} 