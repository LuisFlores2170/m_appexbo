# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.l10n_bo_invoice.tools.siat_soap_services import SiatSoapServices as SiatService
from odoo.addons.l10n_bo_invoice.tools.constants import SiatSoapMethod as siatConstant
from odoo.exceptions import UserError
from datetime import datetime
import logging
from pytz import timezone
import pytz
_logger = logging.getLogger(__name__)

class L10nBoPos(models.Model):
    _name ="l10n.bo.pos"
    _description="Punstos de venta de sucursale"

    name = fields.Char(
        string='Nombre',
        compute='_compute_name'
    )
    
    @api.depends('code')
    def _compute_name(self):
        for record in self:
            record.name = f'Punto de venta {record.code}'

    
    code = fields.Integer(
        string='Código',
        copy=False
    )

    branch_office_id = fields.Many2one(
        string='Sucursal',
        comodel_name='l10n.bo.branch.office',
        readonly=True,
        copy=False
    )

    def getCode(self):
        return self.code

    
    cuis_id = fields.Many2one(
        string='Cuis',
        comodel_name='l10n.bo.cuis',
        readonly=True, 
        copy=False
    )
    

    def getCuis(self):
        if self.cuis_id:
            return self.cuis_id.getCode()
        raise UserError('El punto de venta seleccionado no tiene un cuis valido')
    
    
    cufd = fields.Char(
        string='Cufd',
        copy=False
    )
    
    def getCufd(self):
        if self.cufd:
            return self.cufd
        raise UserError('El punto de venta selccionado no tiene un cufd valido')
    

    # CUIS METHODS
    def cuis_request(self):
        self.ensure_one()
        _today_now = datetime.now()
        _update = False
        if not self.cuis_id:
            _update = True
        if self.cuis_id:
            if _today_now >= self.cuis_id.fechaVigencia:
                _update = True
        if _update:
            self.process_siat('cuis')

    def process_siat(self, request):
        _wsdl, _delegate_token = self.branch_office_id.company_id.get_wsdl_obtaining_codes()
        siat = SiatService(_wsdl, _delegate_token, getattr(self, f'_prepare_params_soap_{request}')(), request)
        res = siat.process_soap_siat()
        getattr(self,f'prepare_process_reponse_{request}')(res)

    def _prepare_params_soap_cuis(self):
        return {'SolicitudCuis': self.get_default_params()}
    
    
    
    def get_default_params(self):
        return {
            'codigoAmbiente': int(self.branch_office_id.company_id.getL10nBoCodeEnvironment()),
            'codigoModalidad': int(self.branch_office_id.company_id.getL10nBoCodeModality()),
            'codigoPuntoVenta': int(self.code),
            'codigoSistema': self.branch_office_id.company_id.getL10nBoCodeSystem(),
            'codigoSucursal': self.branch_office_id.getCode(),
            'nit': self.branch_office_id.company_id.getNit()
        }
    
    
    error = fields.Char(
        string='error',
    )
    
    
    def prepare_process_reponse_cuis(self, response):
        
        if response.get('success'):
            res_data = response.get('data', {})
            if res_data:
                _vals = {
                    'fechaVigencia' : res_data.fechaVigencia.strftime('%Y-%m-%d %H:%M:%S'),
                    'codigo'        : res_data.codigo,
                    'transaccion'    : res_data.transaccion
                }
                if self.cuis_id:
                    self.cuis_id.write(_vals)
                else:
                    self.cuis_id = self.env['l10n.bo.cuis'].create(_vals)
                
                _logger.info(f'{res_data.mensajesList}')
                self.cuis_id.setMessageList(res_data.mensajesList) if res_data.mensajesList else []

        else:
            self.write({'error':response.get('error')})
    
    def getDatetimeNow(self):
        return fields.Datetime.now().astimezone(timezone(self.branch_office_id.company_id.partner_id.tz)).astimezone(pytz.UTC).replace(tzinfo=None)

class l10nBoCuis(models.Model):
    _name = "l10n.bo.cuis"
    _description = "Cuis de Punto de venta"


    name = fields.Char(
        string='Cuis',
        related='codigo',
        readonly=True,
        store=True
    )

    
    codigo = fields.Char(
        string='Codigo',
        copy=False,
        readonly=True 
    )
    
    
    fechaVigencia = fields.Datetime(
        string='Fecha vigencia',
        copy=False,
        readonly=True 
    )

    
    messageList = fields.Many2many(
        string='Lista de mensajes',
        comodel_name='l10n.bo.message.service',
        readonly=True ,
        copy=False
    )
    
    def setMessageList(self, _lists):
        _message_ids = []
        for _list in _lists:
            _message_id = self.env['l10n.bo.message.service'].search(
                [
                    (
                        'codigoClasificador','=', _list.codigo
                    )
                ],
                limit=1
            )
            if _message_id:
                _message_ids.append(_message_id.id)

        self.write(
            {
                'messageList': [
                    (
                        6,0,_message_ids
                    )
                ]
            }
        )   
    
    
    transaccion = fields.Boolean(
        string='Transacción',
        default=False,
        copy=False,
        readonly=True 
    )
    
    

    def getCode(self):
        if self.codigo:
            return self.codigo
        raise UserError('No se encontro un CUIS valido')

    

    