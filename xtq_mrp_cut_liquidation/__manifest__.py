{
    'name': "XTQ - Liquidación de Corte en MO",
    'summary': """
        Añade una funcionalidad de Liquidación de Corte detallada
        en las líneas de componentes de las Órdenes de Producción.""",
    'author': "Omar Ruelas Principe, XTQ GROUP",
    'website': "https://www.xtqgroup.com",
    'category': 'Manufacturing/Manufacturing',
    'version': '18.0.1.0.0',
    'depends': ['mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/mrp_cut_liquidation_views.xml',
        'views/mrp_production_views.xml',
    ],
    'license': 'OEEL-1',
}
