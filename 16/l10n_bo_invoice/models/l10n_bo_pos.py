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
    
    
    cuis = fields.Char(
        string='Cuis',
        copy=False
    )

    
    cuis_id = fields.Many2one(
        string='Cuis',
        comodel_name='l10.bo.cuis',
        copy=False
    )
    

    def getCuis(self):
        if self.cuis:
            return self.cuis
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
    def button_process_siat(self):
        self.ensure_one()
        _today_now = datetime.now()
        _update = False
        if not self.effective_date:
            _update = True
        if self.effective_date:
            if _today_now >= self.effective_date:
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
            'codigoAmbiente': int(self.branch_office_id.company_id.l10n_bo_code_environment),
            'codigoModalidad': int(self.branch_office_id.company_id.l10n_bo_code_modality),
            'codigoPuntoVenta': int(self.code),
            'codigoSistema': self.branch_office_id.company_id.l10n_bo_code_system,
            'codigoSucursal': self.bo_branch_office_id.code,
            'nit': self.branch_office_id.company_id.vat
        }
    

class l10nBoCuis(models.Model):
    _name = "l10.bo.cuis"
    _description = "Cuis de Punto de venta"

    name = fields.Char(
        string='Cuis',
    )
    
    effective_date = fields.Datetime(
        string='Fecha efectiva',
        copy=False,
        readonly=True 
    )

    

    