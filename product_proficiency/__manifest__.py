{
    'name': 'Dominio de productos',
    'version': '1.0',
    'category': 'Custom',
    'description': 'Módulo para el dominio de productos en registros. de compra, venta, inventario',
    'author': 'Luis Fernando Hinojosa Flores',
    'depends': ['base', 'sale_management','stock'],
    'data': [
        'security/ir.model.access.csv',
        
        'views/views.xml'

    ],
    'installable': True,
}
