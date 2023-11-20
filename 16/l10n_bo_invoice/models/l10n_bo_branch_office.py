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

    
    quant_online = fields.Integer(
        string='Cant. en linea',
    )
    quant_offline = fields.Integer(
        string='Cant. fuera de linea',
    )
    
    quant_inactive = fields.Integer(
        string='Cant. inactiva',
    )
    
    quant_pos = fields.Integer(
        string='Cantidad de POS',
    )
    

    
    @api.constrains('l10n_bo_pos_ids')
    def _check_l10n_bo_pos_ids(self):
        for record in self:
            record.quant_online = len( [ pos for pos in record.l10n_bo_pos_ids if pos.emision_id and pos.emision_id.getCode() == 1 ] )
            record.quant_offline = len( [ pos for pos in record.l10n_bo_pos_ids if pos.emision_id and pos.emision_id.getCode() == 2 ] )
            record.quant_inactive = len( [ pos for pos in record.l10n_bo_pos_ids if not pos.emision_id ] )
            record.quant_pos = len(record.l10n_bo_pos_ids)
            
    
    
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
        pos = self.env['l10n.bo.pos'].search([('code','=',0)],limit=1)
        if pos:
            _wsdl, _delegate_token = self.company_id.get_wsdl_operations()
            siat = SiatService(_wsdl, _delegate_token, self._prepare_params_select_pos(), siatConstant.SELECT_POS)
            res = siat.process_soap_siat()
            self.createPosS(res)
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Respuesta',
                    'message': 'Debe registrar y obtener el cuis del Punto de venta 0, en primera instancia',
                    'sticky': False,
                }
            }

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
                    self._check_l10n_bo_pos_ids()
                else:
                    pass

    
    
    def cuis_massive_request(self):
        pos_id = self.env['l10n.bo.pos'].search([('code','=',0)],limit=1)
        if pos_id:
            if pos_id.siat_connection():
                for pos in self.l10n_bo_pos_ids:
                    if pos.siat_connection:
                        pos.cuis_request(True)
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Respuesta',
                    'message': 'Debe registrar y obtener el cuis del Punto de venta 0, en primera instancia',
                    'sticky': False,
                }
            }
    
    def cufd_massive_request(self):
        if self.env['l10n.bo.pos'].search([('code','=',0)],limit=1).siat_connection():
            for pos in self.l10n_bo_pos_ids:
                if pos.siat_connection():
                    pos.cufd_request(True)