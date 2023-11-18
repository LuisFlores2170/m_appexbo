{
    'name': 'Cálculo de descuento globales en impuesto',
    'version': '15.0.1.0.1',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': '''
    In the sales invoice it shows a field called "Global Discount" that calculates the percentage of global discount applied to the invoice, 
    based on the negative lines that correspond to the concept of global discount.
    ''',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/global_discount_wizard.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00
}
