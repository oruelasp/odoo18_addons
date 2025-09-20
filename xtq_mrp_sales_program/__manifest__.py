# -*- coding: utf-8 -*-
{
    'name': 'XTQ MRP Sales Program',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Allows the creation of sales programs to project demand and generate manufacturing orders.',
    'author': 'XTQ',
    'website': 'https://www.xtq.com',
    'license': 'OEEL-1',
    'depends': [
        'mrp',
        'mrp_tag',
        'mrp_plm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_program_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
