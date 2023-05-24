# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Colores de referencia',
    'version': '1.0',
    'author' : 'Luis Fernando Hinojosa Flores',
    'summary': 'Colors',
    'description': "This is a module define color",
    'depends': ['base'],
    'category': 'color',
    'demo': [],
    'data': [
        'security/color_security.xml',
        'security/ir.model.access.csv',
        'views/color_menu.xml'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': '',
    'post_init_hook': '',
    'assets': {},
    'license': 'LGPL-3',
}
