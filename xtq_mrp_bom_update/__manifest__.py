# __manifest__.py
# -*- coding: utf-8 -*-
{
    'name': "XTQ - Flujo de Aprobación de BOM para Producción",
    'summary': """
        Introduce un ciclo de vida con estados (Borrador, Aprobado, etc.) 
        y un flujo de trabajo para las Listas de Materiales (Ficha de Producción) 
        vinculadas a Órdenes de Producción.""",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'website': "https://www.xtqgroup.com",
    'category': 'Manufacturing/Manufacturing',
    'version': '18.0.1.0.0',
    'depends': [
        'xtq_mrp_matrix_form',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_bom_rejection_wizard_views.xml',
    ],
    'license': 'OEEL-1',
}
