# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Control de galpon',
    'version': '1.1',
    'summary': 'This is a module for galpon control',
    'description': "This is a module for galpon control",
    'depends': ['stock'],
    'category': 'Inventory/Inventory',
    'sequence': 25,
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/view_control_galpon.xml',
        'report/reporte_control.xml'
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook': '',
    'post_init_hook': '',
    'assets': {},
    'license': 'LGPL-3',
}
