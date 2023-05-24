# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ordenes de trabajo',
    'version': '1.1',
    'author' : 'Luis Fernando Hinojosa Flores',
    'summary': 'This is a module for order works in sales',
    'description': "The works orders are register before sale",
    'depends': ['stock','contacts'],
    'category': 'sale',
    'demo': [],
    'data': [
        'data/ir_sequence_data.xml',
        'security/model_security.xml',
        'security/ir.model.access.csv',
        'views/model_menu.xml',
        #'report/header.xml',
        'report/reporte_work_order.xml'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': '',
    'post_init_hook': '',
    'assets': {},
    'license': 'LGPL-3',
    'author': 'APPEX Bolivia',
    'website': 'www.appexbo.com',
    'maintainer': 'APPEX Bolivia',
    'contributors': ['Luis Fernando Hinojosa Flores']
}
