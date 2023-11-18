#-*- coding:utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError
import pytz
from pytz import timezone

class resPartner(models.Model):
    _inherit = ['res.partner']
    
    complement = fields.Char(
        string='Complemento',
        size=5,
        copy=False
    )

class accountJournal(models.Model):
    _inherit = ['account.journal']

    edi_format_bo = fields.Boolean(
        string='Factura (BO)',
        default=False,
        copy=False
    )

    @api.constrains('edi_format_bo')
    def _check_edi_format_bo(self):
        for record in self:
            account_journal_ids = record.env['account.journal'].search([('edi_format_bo','=',True)])
            if len(account_journal_ids) > 1:
                raise UserError('No puede tener mas de 1 diario para los registros de la Factura (BO)')
    


class AccountMove(models.Model):
    _inherit = ['account.move']
    
    # BASE
    #1
    lv_sequence = fields.Integer(
        string='N°', 
        min_value=0,  
        max_value=99999999,
        default=0,
        help='Dato correlativo y secuencial que permite identificar el número de registro o fila.',
        copy=False
    )
    # BASE
    #2
    lv_specification = fields.Integer(
        string='ESPECIFICACIÓN', 
        default=2,
        help='Valor predeterminado “2”, propio de registro de Facturas Estándar. Solo en caso de importacion del archivo deberá contener esta columna en la segunda posicion.',
    )
    
    
    emision_date = fields.Datetime(
        string='Fecha de emision',
        copy=False
    )

    #3
    lv_invoice_date = fields.Date(
        string='FECHA DE LA FACTURA',
        compute='_compute_lv_invoice_date' 
    )
    
    @api.depends('emision_date')
    def _compute_lv_invoice_date(self):
        for record in self:
            record.lv_invoice_date = record.emision_date
    
    
    
    #4
    lv_invoice_number = fields.Char(
        string='N° DE LA FACTURA',
        size=15,
        copy=False
    )
    
    #5
    lv_authorization_code = fields.Char(
        string='CODIGO DE AUTORIZACION',
        size=15,
        help='Registrar el Codigo de Autorización de la Factura o Nota Fiscal, con valor distinto de cero (0). En casos excepcionales consignar uno de los siguientes valores: 1 = cuando se registre un Boleto Aéreo. 3 = cuando se registre una DUI/DIM.',
        copy=False
    )

    #6
    
    lv_nit_ci = fields.Char(
        string='NIT / CI CLIENTE',
        size=15,
        related='partner_id.vat',
        readonly=True,
        store=True
    )

    #7
    lv_complement = fields.Char(
        string='COMPLEMENTO',
        related='partner_id.complement',
        readonly=True,
        store=True
    )

    #8
    lv_client_name = fields.Char(
        string='NOMBRE O RAZÓN SOCIAL',
        size=240,
        related='partner_id.name',
        readonly=True,
        store=True
    )

    #9
    lv_amount_total = fields.Float(
        string='IMPORTE TOTAL DE LA VENTA',
        compute='_compute_lv_amount_total' 
    )
    
    @api.depends('tax_totals', 'lv_amount_discount', 'lv_amount_gift_card')
    def _compute_lv_amount_total(self):
        for record in self:
            amount = 0.0
            if record.tax_totals:
                amount = record.getAmountTotal() + record.lv_amount_discount + record.lv_amount_gift_card
            record.lv_amount_total = round(amount, 2)


    #10
    
    lv_amount_ice = fields.Float(
        string='IMPORTE ICE',
        default=0.0
    )

    #11
    
    lv_amount_iehd = fields.Float(
        string='IMPORTE IEHD',
        default=0.0
    )
    
    #12
    lv_amount_ipj = fields.Float(
        string='IMPORTE IPJ',
        default=0.0
    )
    
    #13
    lv_amount_rate = fields.Float(
        string='TASAS',
        default=0.0
    )

    #14
    
    lv_amount_no_iva = fields.Float(
        string='OTROS NO SUJETOS AL IVA',
        default=0.0
    )
    
    #15
    
    lv_amount_exports_exempt = fields.Float(
        string='EXPORTACIONES Y OPERACIONES EXENTAS',
        default=0.0
    )
    
    #16
    
    lv_amount_zero_rate = fields.Float(
        string='VENTAS GRAVADAS A TASA CERO',
        default=0.0
    )
    
    #17
    lv_amount_subtotal = fields.Float(
        string='SUBTOTAL',
        compute='_compute_lv_amount_subtotal' )
    
    @api.depends('lv_amount_total', 'lv_amount_ice', 'lv_amount_iehd', 'lv_amount_ipj', 'lv_amount_rate', 'lv_amount_no_iva', 'lv_amount_exports_exempt', 'lv_amount_zero_rate')
    def _compute_lv_amount_subtotal(self):
        for record in self:
            amount = record.lv_amount_total - record.lv_amount_ice - record.lv_amount_iehd - record.lv_amount_ipj - record.lv_amount_rate - record.lv_amount_no_iva - record.lv_amount_exports_exempt - record.lv_amount_zero_rate
            record.lv_amount_subtotal = round(amount, 2)
    #18
    lv_amount_discount = fields.Float(
        string='DESCUENTOS, BONIFICACIONES Y REBAJAS SUJETAS AL IVA',
        compute='_compute_lv_amount_discount' 
    )
    
    @api.depends('invoice_line_ids')
    def _compute_lv_amount_discount(self):
        for record in self:
            amount = 0.0
            for line in record.invoice_line_ids:
                if line.product_id.global_discount:
                    amount += line.price_unit *-1
            record.lv_amount_discount = round(amount, 2)
    
    #19
    lv_amount_gift_card = fields.Float(
        string='IMPORTE GIFT CARD',
        default=0.0
    )

    #20
    lv_amount_tax_debit = fields.Float(
        string='IMPORTE BASE PARA DÉBITO FISCAL',
        compute='_compute_lv_amount_tax_debit' 
    )
    
    @api.depends('lv_amount_subtotal', 'lv_amount_discount', 'lv_amount_gift_card')
    def _compute_lv_amount_tax_debit(self):
        for record in self:
            amount = record.lv_amount_subtotal - record.lv_amount_discount - record.lv_amount_gift_card
            record.lv_amount_tax_debit = round(amount, 2)

    #21
    lv_amount_fiscal_debit = fields.Float(
        string='DEBITO FISCAL',
        compute='_compute_lv_amount_fiscal_debit' 
    )
    
    @api.depends('lv_amount_tax_debit')
    def _compute_lv_amount_fiscal_debit(self):
        for record in self:
            record.lv_amount_fiscal_debit = round(record.lv_amount_tax_debit * 0.13, 2)

    #22
    lv_state = fields.Char(
        string='ESTADO',
        copy=False
    )
    

    #23
    lv_control_code = fields.Char(
        string='CÓDIGO DE CONTROL',
        size=17,
        copy=False,
        help='Registrar el Código de Control, el cual está constituido por pares de datos alfanuméricos separado por guiones (-) y expresado en formato hexadecimal (A, B, C, D, E y F), no debe contener la letra “O” solamente el número cero (0). Caso contrario deberá consignar el valor cero (0).'        
    )

    #24
    lv_sale_type = fields.Selection(
        string='TIPO DE VENTA',
        selection=[
            ('0', 'OTROS'), 
            ('1', 'GIFT CARD (Venta de gift card)')
        ],
        default='0',
        copy=False
    )
    
    
    
    
    
    
    def getAmountTotal(self):
        amount = 0.0
        if self.tax_totals:
            amount = self.tax_totals.get('amount_total', 0.0)
            if amount > 99999999999999.99:
                raise UserError('El monto total supera la cantidad maxima valida en el sistema')
        return round(amount, 2)
    
    

    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.sale_book_methods()
        return res
    
    def sale_book_methods(self):
        if self.move_type in ['out_invoice'] and self.journal_id.edi_format_bo:
            if self.lv_sequence == 0:
                self.next_customer_sequence()
            self.getSaleSpesification()
            self.getSaleInvoiceDate()
    
    def next_customer_sequence(self):
        self.write({'lv_sequence' : self.env['ir.sequence'].next_by_code('sequence_out_invoice')})
    
    def getSaleSpesification(self):
        if self.move_type in ['out_invoice']:
            self.write({'lv_specification' : 2})

    def getSaleInvoiceDate(self):
        if self.move_type in ['out_invoice']:
            self.write({'emision_date' : self.getFechaHora().astimezone(pytz.UTC).replace(tzinfo=None),})

    def getFechaHora(self):
        fechaHora = fields.Datetime.now().astimezone(timezone(self.company_id.partner_id.tz))
        return fechaHora