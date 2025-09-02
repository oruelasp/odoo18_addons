# -*- coding: utf-8 -*-
{
    'name': "Stock User Restrictions",
    'summary': """
        Allows granular access control for users on specific Warehouses
        and Picking Types.""",
    'description': """
        This module enhances Odoo's security by allowing administrators to
        configure inventory access restrictions directly on the user form.
        - Activate restrictions per user.
        - Define rules by allowed Warehouse.
        - Specify allowed Picking Types for each Warehouse.
        - If no Picking Types are specified for a Warehouse, all are allowed.
        - Security rules are applied to Picking and Picking Type views.
        - Location visibility is not restricted to allow inter-warehouse transfers.
    """,
    'author': "xtendoo",
    'website': "https://xtendoo.es",
    'category': 'Inventory/Security',
    'version': '18.0.1.0.0',
    'license': 'OPL-1',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': True,
}
