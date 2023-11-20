# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.addons.l10n_bo_invoice.tools.siat_soap_services import SiatSoapServices as SiatService
from odoo.addons.l10n_bo_invoice.tools.constants import SiatSoapMethod as siatConstant
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
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

    @api.model
    def create(self, vals):
        if self.search([('code','=',vals.get('code'))]):
            raise ValidationError('No puede tener codigos de puntos de venta iguales')
        res = super(L10nBoPos, self).create(vals)
        return res
    
    
    @api.onchange('code')
    def _onchange_code(self):
        if self.create_date and self.search([('code','=',self.code)]):
            raise ValidationError('No puede tener codigos de puntos de venta iguales')
    
    
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
    
    
    
    cufd_id = fields.Many2one(
        string='Cufd',
        comodel_name='l10n.bo.cufd',
        readonly=True,
        copy=False
    )
    
    
    def getCufd(self):
        if self.cufd:
            return self.cufd
        raise UserError('El punto de venta selccionado no tiene un cufd valido')
    
    
    address = fields.Char(
        string='Dirección',
        store=True,
        copy=False
    )

    

    
    pos_type_id = fields.Many2one(
        string='Tipo',
        comodel_name='l10n.bo.type.point.sale',
        copy=False
    )

    
    requested_cuis = fields.Boolean(
        string='Cuis activo',
        copy=False,
        readonly=True,
    )
    
    @api.constrains('cuis_id')
    def _check_cuis_id(self):
        for record in self:
            record.requested_cuis = True if record.cuis_id else False
    
    
    
    
    # CUIS METHODS
    def cuis_request(self, massive = False):
        if not massive:
            if self.siat_connection():
                self.ensure_one()
                _today_now = self.getDatetimeNow()
                _update = False
                if not self.cuis_id:
                    _update = True
                if self.cuis_id:
                    if _today_now >= self.cuis_id.fechaVigencia:
                        _update = True
                if _update:
                    self.process_siat('cuis')
        else:
            self.ensure_one()
            _today_now = self.getDatetimeNow()
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

    
    emision_id = fields.Many2one(
        string='Emision',
        comodel_name='l10n.bo.type.emision',
        copy=False
    )
    

    def cufd_request(self, massive = False):
        if not massive:
            if self.siat_connection():
                if self.emision_id:
                    if self.emision_id.getCode() == 1:
                        self.process_siat('cufd')
        else:
            if self.emision_id:
                if self.emision_id.getCode() == 1:
                    self.process_siat('cufd')

    
    def _prepare_params_soap_cufd(self):
        request_data = self.get_default_params()
        request_data['cuis'] = self.cuis_id.getCode()
        return {'SolicitudCufd': request_data}

    def prepare_process_reponse_cuis(self, response):
        
        if response.get('success'):
            res_data = response.get('data', {})
            if res_data:
                _vals = {
                    'fechaVigencia' : res_data.fechaVigencia.strftime('%Y-%m-%d %H:%M:%S'),
                    'codigo'        : res_data.codigo,
                    'transaccion'    : res_data.transaccion,
                    'success'       : response.get('success')
                }
                if self.cuis_id:
                    self.cuis_id.write(_vals)
                else:
                    self.cuis_id = self.env['l10n.bo.cuis'].create(_vals)
                
                _logger.info(f'{res_data.mensajesList}')
                self.cuis_id.setMessageList(res_data.mensajesList) if res_data.mensajesList else []

        else:
            self.write({'error':response.get('error')})

    def prepare_process_reponse_cufd(self, response):
        if response.get('success'):
            res_data = response.get('data', {})
            if res_data:
                if res_data.transaccion:
                    _vals = {
                        'codigo'        : res_data.codigo,
                        'codigoControl' : res_data.codigoControl,
                        'direccion'     : res_data.direccion,
                        'fechaVigencia' : res_data.fechaVigencia.strftime('%Y-%m-%d %H:%M:%S'),
                        'transaccion'    : res_data.transaccion,
                        'success'       : response.get('success')
                    }
                    if self.cufd_id:
                        self.cufd_id.write(_vals)
                    else:
                        self.cufd_id = self.env['l10n.bo.cufd'].create(_vals)
                    
                    _logger.info(f'{res_data.mensajesList}')
                self.cufd_id.setMessageList(res_data.mensajesList) if res_data.mensajesList else []

        else:
            self.write({'error':response.get('error')})
    
    def getDatetimeNow(self):
        return fields.Datetime.now().astimezone(timezone(self.branch_office_id.company_id.partner_id.tz)).astimezone(pytz.UTC).replace(tzinfo=None)


    def siat_connection(self):
        _ws_method = siatConstant.WSDLS['server.verification']
        _wsdl, _delegate_token = getattr(self.branch_office_id.company_id, _ws_method[self.branch_office_id.company_id.getL10nBoCodeModality()])()
        siat = SiatService(_wsdl, _delegate_token, {}, _ws_method['method_verification'])
        response = siat.process_soap_siat()
        if response.get('success', False):
            res_data = response.get('data')
            if res_data.transaccion:
                for obs in res_data.mensajesList:
                    if obs.codigo == 926:
                        return True
            return False
        else:
            return False
    
    def test_siat_connection(self):
        if self.siat_connection():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Coneccion exitosa',
                    'message': 'Coneccion exitosa con el SIAT',
                    'sticky': False,
                }
            }
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Coneccion fallida',
                    'message': 'No se tiene coneccion con la base de datos del SIAT',
                    'sticky': False,
                }
        }
    
    # CREATE RECORDS

    
    type_pos_id = fields.Many2one(
        string='Tipo',
        comodel_name='l10n.bo.type.point.sale'
    )
    
    
    transaccion = fields.Boolean(
        string='Trassacción',
        default=False
    )
    

    # OPEN POS
    def open_pos_request(self):
        if not self.existPos(self.code):
            _wsdl, _delegate_token = self.branch_office_id.company_id.get_wsdl_operations()
            _params = self.prepare_params_open_pos()
            siat = SiatService(_wsdl, _delegate_token, _params, siatConstant.CREATE_POS)
            response = siat.process_soap_siat()
            if response.get('success', False):
                res_data = response.get('data', {})
                if res_data.transaccion:
                    self.create({'code': res_data.codigoPuntoVenta, 'transaccion': res_data.transaccion})
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Respuesta',
                    'message': 'El punto de venta que intenta crear ya existe en la base de datos del SIN',
                    'sticky': False,
                }
            }
                
        
    def prepare_params_open_pos(self):
        company = self.branch_office_id.company_id
        request_data = {
            'codigoAmbiente': int(company.getL10nBoCodeEnvironment()),
            'codigoModalidad': int(company.getL10nBoCodeModality()),
            'codigoSistema': company.getL10nBoCodeSystem(),
            'codigoSucursal': int(self.branch_office_id.code),
            'codigoTipoPuntoVenta': int(self.type_pos_id.getCode() or '5'),
            'cuis': self.search([('code','=',0)],limit=1).getCuis(),
            'descripcion': self.address or '',
            'nit': company.getNit(),
            'nombrePuntoVenta': self.name or ''
        }
        return {'SolicitudRegistroPuntoVenta': request_data}
    
    def _prepare_params_delete(self):
        company = self.branch_office_id.company_id
        request_data = {
            'codigoAmbiente': int(company.getL10nBoCodeEnvironment()),
            'codigoPuntoVenta': self.code,
            'codigoSistema': company.getL10nBoCodeSystem(),
            'codigoSucursal': self.branch_office_id.code,
            'cuis': self.search([('code','=',0)],limit=1).getCuis(),
            'nit': company.getNit()
        }
        return {'SolicitudCierrePuntoVenta': request_data}
    
    def run_reponse(self, response):
        if response.get('success'):
            res_data = response.get('data', {})
            if res_data.transaccion:
                self.unlink()

    def delete_to_siat(self):
        _wsdl, _delegate_token = self.branch_office_id.company_id.get_wsdl_operations()
        siat = SiatService(_wsdl, _delegate_token, self._prepare_params_delete(), siatConstant.DELETE_POS)
        res = siat.process_soap_siat()
        self.run_reponse(res)

    def getAllPos(self):
        poss = []
        _wsdl, _delegate_token = self.company_id.get_wsdl_operations()
        siat = SiatService(_wsdl, _delegate_token, self.branch_office_id._prepare_params_select_pos(), siatConstant.SELECT_POS)
        res = siat.process_soap_siat()
        if res.get('success', False):
            res_data = res.get('data',{})
            if res_data:
                if res_data.transaccion:
                    poss = res_data.listaPuntosVentas
        return poss
    
    def existPos(self, code):
        exist = False
        poss = self.getAllPos()
        if poss:
            for pos in poss:
                if code == pos.codigoPuntoVenta:
                    exist = True
                    break
        return exist

    
    

class l10nBoCuis(models.Model):
    _name = "l10n.bo.cuis"
    _description = "Codigo unico de inicio de sistema"


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

    
    messagesList = fields.Many2many(
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
                'messagesList': [
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

    
    success = fields.Boolean(
        string='Realizado',
        copy=False,
        readonly=True
    )
    
    
    

    def getCode(self):
        if self.codigo:
            return self.codigo
        raise UserError('No se encontro un CUIS valido')
    

    

class l10nBoCufd(models.Model):
    _name = "l10n.bo.cufd"
    _description = "Codigo unico de facturacion diaria"


    name = fields.Char(
        string='Cufd',
        related='codigo',
        readonly=True,
        store=True
    )

    
    codigo = fields.Char(
        string='Codigo',
        copy=False,
        readonly=True 
    )

    
    codigoControl = fields.Char(
        string='Codigo control',
        copy=False,
        readonly=True 
    )
    
    
    direccion = fields.Char(
        string='Dirección',
        copy=False,
        readonly=True 
    )
    
    
    fechaVigencia = fields.Datetime(
        string='Fecha vigencia',
        copy=False,
        readonly=True 
    )

    
    messagesList = fields.Many2many(
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
    
    
    success = fields.Boolean(
        string='Realizado',
        copy=False,
        readonly=True 
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
    
    
    error = fields.Char(
        string='error',
        copy=False, 
        readonly=True 
    )
    