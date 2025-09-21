{
    'name': "PLM Customization for Sample Orders (OM)",
    'summary': """
        Extends the PLM module to manage Sample Orders by enriching
        the mrp.eco model and adding a custom operation cost structure.""",
    'description': """
        - Adds custom fields to mrp.eco to track sample attributes.
        - Adds a new model to register operation costs for an ECO.
        - Extends mrp.bom to categorize components into different tabs.
        - Provides an Excel report summarizing the sample's cost sheet.
    """,
    'author': "Brandint, Odoo AI Assistant",
    'website': "https://www.brandint.com",
    'category': 'Manufacturing/PLM',
    'version': '18.0.1.0.0',
    'depends': ['mrp_plm'],
    'data': [
        'views/mrp_eco_views.xml',
        'views/mrp_bom_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# Encoding fix 2
