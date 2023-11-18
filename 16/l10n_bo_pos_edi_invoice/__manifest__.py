# -*- coding:utf-8 -*-
{
    'name': 'Punto de venta BO - EDI',
    'version': '1.0',
    'depends': [
        'l10n_bo_invoice'
    ],
    'author': 'APPEX BOLIVA SRL',
    'summary': 'Regsitro de ventas integradas con POS',
    'data': [
        'templates/sequences.xml',
        'views/views.xml',
    ],
    'post_init_hook': 'post_install_hook',
    'installable': True,
}
