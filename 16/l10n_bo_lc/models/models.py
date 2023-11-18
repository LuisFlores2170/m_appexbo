from odoo import api, models, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = ['account.move']
    

    # BASE
    #1
    sequence = fields.Integer(
        string='N°', 
        min_value=1,  
        max_value=999999,
        help='Dato correlativo y secuencial que permite identificar el número de registro o fila.'
    )
    # BASE
    #2
    specification = fields.Integer(
        string='ESPECIFICACIÓN', 
        min_value=1,  
        max_value=2,
        help='Valor predeterminado “1”, propio de registro de Facturas Estándar. Solo en caso de importacion del archivo deberá contener esta columna en la segunda posicion.'
    )
    #3
    lc_provider_nit = fields.Char(
        string='NIT PROVEEDOR',
        related='partner_id.vat',
        readonly=True,
        store=True,
        help='Número de Identificación Tributaria del proveedor. En el caso de DUI/DIM consignar Número de Identificación Tributaria de la Agencia Despachante de Aduana o si es la misma empresa la que realiza la importación deberá consignar su mismo NIT.'
    )
    #4
    lc_provider_name = fields.Char(
        string='RAZON SOCIAL PROVEEDOR',
        size=240,
        help='Nombre o Razón Social del proveedor. En el caso de DUI/ DIM consignar el nombre o Razón Social de la Agencia Despachante de Aduana o si es la misma empresa la que realiza la importación deberá consignar su misma Razón Social.'
    )
    # BASE
    #5
    authorization_code = fields.Char(
        string='CODIGO DE AUTORIZACION',
        size=100,
        help='Registrar el Codigo de Autorización de la Factura o Nota Fiscal, con valor distinto de cero (0). En casos excepcionales consignar uno de los siguientes valores: 1 = cuando se registre un Boleto Aéreo. 3 = cuando se registre una DUI/DIM.'        
    )
    #6
    lc_invoice_number = fields.Char(
        string='NUMERO FACTURA',
        size=20,
        help='Registrar el Codigo de Autorización de la Factura o Nota Fiscal, con valor distinto de cero (0). En casos excepcionales consignar uno de los siguientes valores: 1 = cuando se registre un Boleto Aéreo. 3 = cuando se registre una DUI/DIM.'
    )
    #7
    lc_dui_dim_number = fields.Char(
        string='NÚMERO DUI/DIM',
        size=15,  
        help="""
            Número de la Declaración Única de Importación/Declaración de Mercaderias de Importación. Este dato es obligatorio solamente cuando la compra se trate de una importación.
            Número de la DUI/DIM.
            (DUI) Formato AAAADDDCNNNNNNNN
            Donde:
            AAAA = Año
            DDD = Código de la Aduana
            C= Tipo de tramite
            NNNNNNNN = Número Correlativo
            Ej.: 2020211C30695
            (DIM) Formato AAAADDDNNNNNNNN
            Donde:
            AAAA = Año
            DDD = Código de la Aduana
            NNNNNNNN = Número Correlativo
            Ej.: 20215212014770
            (Cuando se haya registrado una Factura, Nota Fiscal o Documento Equivalente, consignar el valor cero (0)).
        """        
    )
    #8
    lc_amount_total_purchase = fields.Float(
        string='IMPORTE TOTAL COMPRA',
        compute='_compute_amount_total_purchase', 
        help='Importe Total de la Compra que figura en la Factura, sin deducir Impuestos ICE - IEHD - IPJ, Tasas, Otros No Sujeto a Crédito Fiscal, Importes Exentos, Importe de Compras Gravadas a Tasa Cero, Descuentos, Bonificaciones o Rebajas, Gift Card.'
    )
    #9
    
    

    # -- METHODS --

    def _compute_amount_total_purchase(self):
        for record in self:
            record.lc_amount_total_purchase = record.getAmountTotal()
    
    def getAmountTotal(self):
        if self.tax_totals:
            amount_total = self.tax_totals.get('amount_total', 0.0)
            if amount_total > 99999999999999.99:
                raise UserError('El monto total supera la cantidad maxima valida en el sistema')
            return amount_total
        return 0.0
    
    