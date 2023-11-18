# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Facturacion boliviana V16 APPEX ',
    'version': '2.1',
    'author' : 'APPEX Bolivia',
    'summary': 'Facturacion electronica / computarizada',
    'description': """
        Facturacion electronica / computarizada:
         - Factura Compra - venta
         - Emisiones en linea / Fueda de linea
         - Libro de ventas
    """,
    'depends': [
        'base',
        'contacts', 
        'account',
        'l10n_bo', 
        'base_address_extended', 
        'account_discount_global', 
        'sale_management', 
        'l10n_bo_lv'
    ],
    'category': 'services',
    'demo': [],
    # 2.10.1
    'external_dependencies': {'python': ['signxml', 'qrcode']},
    'data': [
        #DATA
        'data/l10n_bo_catalog.xml',
        #'data/mail_templates.xml',
        #'data/res.country.state.csv',
        #'data/res.city.csv',
        #'data/res.municipality.csv',
        #'data/group_tax.xml',
        #'data/account_tax.xml',
        #'data/sequence.xml',
        
        # SECURITY
        'security/security.xml',
        'security/ir.model.access.csv',
        
        #REPORTS
        #'reports/paper_format.xml',
        #'reports/base.xml',
        #'reports/purchase_sale.xml',
        

        #SEQUENCES


        #VIEWS
        'views/l10n_bo_branch_office.xml',
        'views/l10n_bo_pos.xml',
        'views/res_config_settings.xml',
        'views/l10n_bo_catalog.xml',
        #'views/l10n_bo_product.xml',
        #'views/account_move.xml',
        #'views/res_partner.xml',
        #'views/res_currency.xml',
        #'views/significant_event.xml',
        #'views/package_massive.xml',
        #'views/sale_book.xml',
        #'views/sale_order.xml',
        
        
        'views/menu.xml',
        #'data/cron.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook': '',
    'post_init_hook': 'post_install_hook',
    'assets': {},
    'license': 'OPL-1',
    'website': 'www.appexbo.com',
    'maintainer': 'Luis Fernando Hinojosa Flores',
    'contributors': ['Luis Fernando Hinojosa Flores']
}
