{
    'name': 'New stock - theme prime',
    'version': '1.0',
    'description': 'Modulo para canbias el uso de campo nuevo para el stock en el e-commerce',
    'summary': '',
    'author': 'MYR CONSULTORIA EN SISTEMAS S.A.C',
    'website': 'https://myrconsulting.net/',
    'license': 'LGPL-3',
    'category': 'website',
    'depends': [
        'base', 'stock', 'web', 'website'
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/form_product_inherit.xml',
        'view/server/ir_action.xml',
        'wizard/wizard_action_form.xml',
    ],
    'auto_install': False,
    'application': False,
}