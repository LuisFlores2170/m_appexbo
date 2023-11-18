# -*- coding: utf-8 -*-
{
    'name': 'Libro de ventas (BO-EDI) V16',
    'version': '1.0',
    'depends': [
        'base', 
        'account_accountant',
        'l10n_bo',
        'account_discount_global',
    ],
    'author': 'APPEX BOLIVA SRL',
    'summary': 'Registro de datos de factura de clientes para el libro de ventas',
    'data': [
        'templates/sequences.xml',
        'views/views.xml',
    ],
    'post_init_hook': 'post_install_hook',
    'contributors': [
        'Luis Fernando Hinojosa Flores <soporte@appexbo.com>',
    ],
    'installable': True,
}