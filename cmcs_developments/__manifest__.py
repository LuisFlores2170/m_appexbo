# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Desarrollo APPEX',
    'version': '1.0',
    'author' : 'APPEX Bolivia',
    'summary': 'Module develop by APPEX for COMCIS PLAS',
    'description': "This is a module with all customer develop for COMICS PLAS",
    'depends': ['contacts','sale','purchase', 'stock'],
    'category': 'customizations',
    'demo': [],
    'data': [
        # security
        'security/model_security.xml',
        'security/ir.model.access.csv',

        # views
        'views/form_category.xml',
        'views/form_contact.xml',
        'views/form_product.xml',
        'views/menu_product_references.xml',
        'views/form_sale.xml',
        'views/list_stock_view.xml',
        'views/form_picking_type.xml',

        # reports
        'reports/paper_format.xml',
        'reports/layout_standard.xml',
        'reports/report_sale_troquelado.xml',
        'reports/report_sale.xml',
        'reports/report_inventory.xml',

        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': '',
    'post_init_hook': '',
    'assets': {},
    'license': 'OPL-1',
    'website': 'www.appexbo.com',
    'maintainer': 'APPEX Bolivia',
    'contributors': ['Luis Fernando Hinojosa Flores']
}
