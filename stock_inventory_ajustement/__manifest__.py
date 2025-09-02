# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2022  - feddad.imad@gmail.com

{
    "name": "Ajuste de Inventario de Stock",
    "version": "18.0.0.0.0",
    "license": "LGPL-3",
    "category": "Inventory/Inventory",
    "summary": "Permite hacer un seguimiento más fácil de los Ajustes de Inventario",
    "author": "feddad.imad@gmail.com",
    "website": "",
    "depends": ["stock","base"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/stock_inventory.xml",
        "views/stock_quant.xml",
        "views/stock_move_line.xml",
        "views/res_config_settings_view.xml",
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
}
