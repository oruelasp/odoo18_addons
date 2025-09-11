# __manifest__.py
# -*- coding: utf-8 -*-
{
    'name': "XTQ - Flujo de Aprobación de BOM para Producción con PLM",
    'summary': """
        Gestiona un flujo de 'Ficha de Producción' utilizando Órdenes de Cambio 
        de Ingeniería (ECO) del módulo PLM, vinculadas a Órdenes de Producción.""",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'website': "https://www.xtqgroup.com",
    'category': 'Manufacturing/PLM',
    'version': '18.0.2.0.0',
    'depends': [
        'mrp_plm',
        'xtq_mrp_matrix_form',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'views/mrp_eco_views.xml',
        'views/mrp_eco_rejection_wizard_views.xml',
    ],
    'license': 'OEEL-1',
}
