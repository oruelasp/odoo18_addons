# -*- coding: utf-8 -*-
{
    'name': "Odoo Users Limiter",
    'version': '18.0.0.0',
    'author': "Ben Taieb Med Amine",
    'maintainer': "iifast2",
    'website': "http://medaminebt.com",
    'depends': ['base'],
    'license': "AGPL-3",
    'category': "Tools",
    'summary': "Limit the number of internal users created in the system.",
    'description': """
        The Users Limits module enables administrators to define a maximum limit for internal user creation. Once the limit is reached, new user creation is blocked. This restriction applies only to internal users, while portal and public users are unaffected.
    """,
    'data': ['views/res_users_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
}
