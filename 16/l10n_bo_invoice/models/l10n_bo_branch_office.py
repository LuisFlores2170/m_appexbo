# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import UserError
from odoo.addons.l10n_bo_invoice.tools.siat_soap_services import SiatSoapServices as SiatService
from odoo.addons.l10n_bo_invoice.tools.constants import SiatSoapMethod as siatConstant
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class L10nBoBranchOffice(models.Model):
    _name = 'l10n.bo.branch.office'
    _description = 'Sucursales'

    
    name = fields.Char(
        string='Nombre',
        copy=False
    )
    
    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    
    
    code = fields.Integer(
        string='Código',
        required=True,
        copy=False
    )
    address = fields.Text(
        string='Dirección',
        copy=False
    )
    l10n_bo_pos_ids = fields.One2many(
        string='Puntos de venta',
        comodel_name='l10n.bo.pos',
        inverse_name='branch_office_id', 
        copy=False
    )
    
    def getCode(self):
        return self.code
    
    def _prepare_params_select_pos(self):
        company = self.company_id
        request_data = {
            'codigoAmbiente': int(company.getL10nBoCodeEnvironment()),
            'codigoSistema': company.getL10nBoCodeSystem(),
            'codigoSucursal': self.code,
            'cuis': self.env['l10n.bo.pos'].search([('code','=',0)],limit=1).getCuis(),
            'nit': company.getNit()
        }
        return {'SolicitudConsultaPuntoVenta': request_data}
    
    def update_pos_from_siat(self):
        _wsdl, _delegate_token = self.company_id.get_wsdl_operations()
        siat = SiatService(_wsdl, _delegate_token, self._prepare_params_select_pos(), siatConstant.SELECT_POS)
        res = siat.process_soap_siat()
        self.createPosS(res)

    def createPosS(self, res):
        if res.get('success', False):
            res_data = res.get('data',{})
            if res_data:
                if res_data.transaccion:
                    for pos in res_data.listaPuntosVentas:
                        pos_id = self.env['l10n.bo.pos'].search([('code','=',pos.codigoPuntoVenta)], limit=1)
                        if not pos_id:
                            type_id = self.env['l10n.bo.type.point.sale'].search([('descripcion','=',pos.tipoPuntoVenta)], limit=1)

                            self.env['l10n.bo.pos'].create(
                                {
                                    'code' : pos.codigoPuntoVenta,
                                    'name' : pos.nombrePuntoVenta,
                                    'pos_type_id' : type_id.id if type_id else False,
                                    'branch_office_id' : self.id
                                }
                            )
                else:
                    pass

    def _prepare_params_cuisMasivo(self):
        company = self.company_id
        request_data = {
            'codigoAmbiente': int(company.getL10nBoCodeEnvironment()),
            'codigoModalidad': int(company.getL10nBoCodeModality()),
            'codigoSistema': company.getL10nBoCodeSystem(),
            'nit': company.getNit(),
            'datosSolicitud' :{
                    'codigoPuntoVenta':0
            },
            'codigoSucursal': int(0),
            'codigoPuntoVenta' : 0
            
        }
        return {'SolicitudCuisMasivoSistemas': request_data}
    
    def cuis_massive_request(self):
        _wsdl, _delegate_token = self.company_id.get_wsdl_obtaining_codes()
        siat = SiatService(_wsdl, _delegate_token, getattr(self, f'_prepare_params_cuisMasivo')(), siatConstant.MASSIVE_CUIS)
        res = siat.process_soap_siat()
        raise UserError(f'{res}')
    
    '''
        {
            'success': False, 
            'error': TypeError("{https://siat.impuestos.gob.bo/}solicitudCuisMasivoSistemas() got an unexpected keyword argument 'codigoSucursal'. Signature: `codigoAmbiente: xsd:int, codigoModalidad: xsd:int, codigoSistema: xsd:string, datosSolicitud: {https://siat.impuestos.gob.bo/}solicitudListaCuisDto[], nit: xsd:long`")
        }
    '''