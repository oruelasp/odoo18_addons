{
    'name': 'Proceso de Pago - Contact',
    'version': '1.0',
    'description': 'proceso de rellenado de datos del cliente en la pasarela de pago',
    'summary': '',
    'author': 'MYR CONSULTORIA EN SISTEMAS S.A.C',
    'website': 'https://myrconsulting.net/',
    'license': 'LGPL-3',
    'category': 'website',
    'depends': [
        'base', "web","contacts", "website_sale", "l10n_latam_base", "l10n_pe_website_sale", "portal"
    ],
    'data': [
        'view/form_company_view.xml',
        'view/form_res_partner.xml',
        'view/web/resumen_pedido_inherit.xml',
        "view/web/new-form_address.xml",
        "view/web/info_user_inherit.xml",
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_frontend': [
            'custom_myr_cummins_payment/static/src/js/form.js',
            'custom_myr_cummins_payment/static/src/js/index.js'
        ]
    }
}
