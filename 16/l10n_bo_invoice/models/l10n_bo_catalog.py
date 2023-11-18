# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.l10n_bo_invoice.tools.constants import SiatSoapMethod as siatConstant
from odoo.addons.l10n_bo_invoice.tools.siat_soap_services import SiatSoapServices as SiatService
import logging
from odoo.exceptions import UserError
from datetime import datetime
from pytz import timezone, utc

_logger = logging.getLogger(__name__)

"""
Solicitud del Código Único de Facturación Diaria - CUFD
https://siatinfo.impuestos.gob.bo/index.php/facturacion-en-linea/implementacion-servicios-facturacion/codigos/solicitud-cufd
"""


class CatalogRequest(models.Model):
    _name = 'l10n.bo.catalog.request'
    _description = 'Catalogs Request'
    _order = 'id desc'

    
    name = fields.Char(string='Nombre', compute='_compute_name' )
    
    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Borrador'),('imperfect','Imperfecto'), ('success', 'Realizado')],
        default='draft'
    )
    @api.onchange('catalog_status_ids.state')
    def _onchange_registros_relacionados_estado(self):
        if all(catalog_status_id.state == 'done'  for catalog_status_id in self.catalog_status_ids):
            self.state = 'success'
        else:
            self.state = 'imperfect'
    
    
    def _compute_name(self):
        for record in self:
            record.name =  f"Sincronización - {record.id} - {record.branch_office_id.name}" 
    
    catalog_status_ids = fields.One2many(
        comodel_name='l10n.bo.request.catalog.status', 
        string='Sincronizar catalogos',
        inverse_name='request_catalog_id',
        readonly=True 
    )

    
    branch_office_id = fields.Many2one(
        string='Sucursal',
        comodel_name='l10n.bo.branch.office',
        default=lambda self: self._get_default_branch_office_id(),
        required=True
    )
    
    @api.model
    def _get_default_branch_office_id(self):
        branch_office_id = self.env['l10n.bo.branch.office'].search([], limit=1)
        return branch_office_id.id if branch_office_id else False
            
    
    
    def get_l10n_bo_catalog_sync_ids(self):
        for record in self:
            vals_status = []
            for catalog in record.company_id.l10n_bo_catalog_sync_ids:
                vals_status.append([0, 0, {
                    'catalog_id': catalog.id,
                    'state': 'draft',
                    'branch_office_id' : self.branch_office_id.id
                }])
            record.catalog_status_ids = vals_status
    

    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        readonly=True, 
        default=lambda self: self.env.user.company_id
    )

    def button_process_all_siat(self):
        self.ensure_one()
        for catalog in self.catalog_status_ids:
            catalog.button_process_siat()
    
    @api.model
    def update_catalogs(self):
        self = self.sudo()
        branch_office = self.env['l10n.bo.branch.office'].search([('code','=',0)],limit=1)
        catalog_id = self.create(
            {
                'branch_office_id' : branch_office.id,
            }
        )
        catalog_id.get_l10n_bo_catalog_sync_ids()
        catalog_id.button_process_all_siat()


    


class L10nBoRequestCatalogStatus(models.Model):
    _name = 'l10n.bo.request.catalog.status'
    _description = 'Catalogs Request Status'

    catalog_id = fields.Many2one('l10n.bo.catalog', 'Catalogo')
    name = fields.Char('Sevicio SIAT', store=True, compute='_compute_name')
    error = fields.Char('Error', readonly=True)
    
    @api.depends('catalog_id')
    def _compute_name(self):
        for status in self:
            status.name = status.catalog_id.name

    code = fields.Selection(related='catalog_id.code')
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Sincronizado'), ('cancel', 'Cancelado')], string='Estado', default='draft')
    request_catalog_id = fields.Many2one(comodel_name='l10n.bo.catalog.request', string='Request', ondelete='cascade', copy=False)

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    
    branch_office_id = fields.Many2one(
        string='l10n_bo_branch_office',
        comodel_name='l10n.bo.branch.office',
    )    
    
    def button_process_siat(self):
        self._process_siat()

    def _prepare_params_soap(self):
        _pos_code = 0 # DEFECTO PARA TODOS
        request_data = {
            'codigoAmbiente': int(self.company_id.l10n_bo_code_environment),
            'codigoPuntoVenta': int(_pos_code),
            'codigoSistema': self.company_id.l10n_bo_code_system,
            'codigoSucursal': self.branch_office_id.code,
            'cuis': self.env['l10n.bo.pos'].search([('code','=',_pos_code)]).getCuis(),
            'nit': self.company_id.vat
        }
        return {'SolicitudSincronizacion': request_data}
    
    
    transaccion = fields.Boolean(
        string='Transaccion',
    )
    

    def _process_siat(self):
        _wsdl, _delegate_token = self.request_catalog_id.company_id.get_wsdl_data_synchronization()
        siat = SiatService(_wsdl, _delegate_token, self._prepare_params_soap(), self.catalog_id.code)
        response = siat.process_soap_siat()
        if response.get('success'):
            res_data = response.get('data', {})
            self.write({'transaccion':res_data.transaccion})
            if self.transaccion:
                self.catalog_id.create_records(res_data)
                
            else:
                self.write({'error': f'{res_data.mensajesList}'})
        else:
            self.write({'error' : response.get('error')})
        self.write({'state' : 'done' if self.transaccion else 'cancel'})
        return response

'''
Creacion del Catalogo de Códigos de Leyendas Facturas
https://siatanexo.impuestos.gob.bo/index.php/implementacion-servicios-facturacion/sincronizacion-codigos-catalogos
'''

"""
Modelo representacion de todos los catalgos: FacturacionSincronizacion
"""

class CatalogRequest(models.Model):
    _name = 'l10n.bo.catalog'
    _description = 'Catalogs Request'
    name = fields.Char('Nombre')
    code = fields.Selection(selection=siatConstant.SYNC_ALL_TUPLE, string='Name')
    description = fields.Char('Description')
    
    model = fields.Char(
        string='Modelo de actividad',
    )
    def create_records(self, request):
        self.env[self.model].create_records(request)


class L10nBoActivity(models.Model):
    _name = 'l10n.bo.activity'
    _description = 'L10nBo Activities'
    _order = 'codigoCaeb ASC'

    codigoCaeb = fields.Char('Codigo CAEB')
    descripcion = fields.Char('Descripcion')
    tipoActividad = fields.Char('Tipo de actividad')
    name = fields.Char('Nombre', store=True, compute='_compute_name')
    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    @api.depends('codigoCaeb', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoCaeb or '', leg.descripcion or '')
    
    def create_records(self, res_data):
        for activity in res_data.listaActividades:
            activity_exist = self.search([('codigoCaeb', '=', activity.codigoCaeb)], limit=1)
            if activity_exist:
                activity_exist.write(
                    {
                        'tipoActividad' : activity.tipoActividad,
                        'descripcion' : activity.descripcion
                    }
                )
            else:
                self.create(
                    {
                        'codigoCaeb' : activity.codigoCaeb,
                        'descripcion' : activity.descripcion,
                        'tipoActividad' : activity.tipoActividad
                    }
                )


class L10nBoDatetime(models.Model):
    _name = 'l10n.bo.datetime'
    _description = 'L10nBo Datetime'
    _order = 'id desc'
    name = fields.Datetime('Fecha y hora')
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    def create_records(self, res):
        self.create(
            {
                'name': datetime.strptime(res.fechaHora, '%Y-%m-%dT%H:%M:%S.%f')
            }
        )



class L10nBoActivityDocumentSector(models.Model):
    _name = 'l10n.bo.activity.document.sector'
    _description = 'L10nBo Activity Document Sector'
    _order = 'codigoDocumentoSector ASC'
    codigoActividad = fields.Char('Codigo de actividad')
    codigoDocumentoSector = fields.Integer('Codigo documento sector')
    tipoDocumentoSector = fields.Char('Tipo documento sector')
    company_id = fields.Many2one(string='Compañia', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)
    name = fields.Char('Nombre', store=True, compute='_compute_name')
    
    @api.depends('codigoActividad', 'codigoDocumentoSector', 'tipoDocumentoSector')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s - %s' % (
            leg.codigoActividad or '', leg.codigoDocumentoSector or '', leg.tipoDocumentoSector or '')

    def getCodigoDocumentoSector(self):
        if not self.codigoDocumentoSector:
            raise UserError('Defina el codigo de documentoSector')
        return self.codigoDocumentoSector

    def create_records(self, res):
        for activity in res.listaActividadesDocumentoSector:
            activity_exist = self.search([('codigoDocumentoSector', '=', activity.codigoDocumentoSector)], limit=1)
            if activity_exist:
                
                activity_exist.write(
                    {
                        'codigoActividad' : activity.codigoActividad,
                        'tipoDocumentoSector' : activity.tipoDocumentoSector
                    }
                )
            else:
                self.create(
                    {
                        'codigoActividad': activity.codigoActividad,
                        'codigoDocumentoSector': activity.codigoDocumentoSector,
                        'tipoDocumentoSector': activity.tipoDocumentoSector
                    }
                )

class LegendCodesInvoices(models.Model):
    _name = 'l10n.bo.legend.code'
    _description = 'L10nBo Legend Code'
    _order = 'codigoActividad ASC'
    codigoActividad = fields.Char('Codigo de actividad')
    descripcionLeyenda = fields.Text('Leyenda')
    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    
    name = fields.Char('Nombre', store=True, compute='_compute_name')
    @api.depends('codigoActividad', 'descripcionLeyenda')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoActividad or '', leg.descripcionLeyenda or '')

    def create_records(self, res):
        for activity in res.listaLeyendas:
            activity_exist = self.search(['&',('codigoActividad','=',activity.codigoActividad), ('descripcionLeyenda', '=', activity.descripcionLeyenda) ], limit=1)
            if not activity_exist:
                self.create(
                    {
                        'codigoActividad': activity.codigoActividad,
                        'descripcionLeyenda': activity.descripcionLeyenda,
                    }
                )



class MessageService(models.Model):
    _name = 'l10n.bo.message.service'
    _description = 'L10nBo Message service'
    _order = 'codigoClasificador ASC'
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    
    codigoClasificador = fields.Integer('Codigo')
    descripcion = fields.Text('Descripción')
    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )



class ProductService(models.Model):
    _name = 'l10n.bo.product.service'
    _description = 'L10nBo Product Service'
    _order = 'codigoProducto ASC'
    codigoActividad = fields.Char('Codigo de actividad')
    codigoProducto = fields.Integer('Codigo de producto')
    descripcionProducto = fields.Text('Descripcion')    
    company_id = fields.Many2one(string='Compañia', comodel_name='res.company', required=True, default=lambda self: self.env.user.company_id)
    manytowmany_nandina_ids = fields.Many2many('l10n.bo.product.service.nandina',string="Codigos nandina",readonly=True)
    name = fields.Char('Nombre', store=True, compute='_compute_name')

    def getAe(self):
        return self.codigoActividad
    
    def getCode(self):
        return self.codigoProducto

    @api.depends('codigoActividad', 'codigoProducto', 'descripcionProducto')
    def _compute_name(self):
        for record in self:
            record.name = '%s - %s - %s' % (
            record.codigoActividad or '', record.codigoProducto or '', record.descripcionProducto or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search(['&',('codigoActividad','=',activity.codigoActividad), ('codigoProducto','=',activity.codigoProducto)], limit=1)
            if not record_exist:
                record_exist = self.create(
                    {
                        'codigoActividad': activity.codigoActividad,
                        'codigoProducto': activity.codigoProducto,
                        'descripcionProducto' : activity.descripcionProducto
                    }
                )
            if activity.nandina:
                for nandina in activity.nandina:
                    nandina_id = self.env['l10n.bo.product.service.nandina'].search([('name','=',nandina)])
                    if not nandina_id:
                        nandina_ids = [registro_id.id for registro_id in record_exist.manytowmany_nandina_ids]
                        nandina_ids.append(self.env['l10n.bo.product.service.nandina'].create({'name': nandina,'l10n_bo_product_service_id':record_exist.id}).id)
                        record_exist.write({'manytowmany_nandina_ids': [(6,0,nandina_ids)]})
                        
class ProductServiceNandina(models.Model):
    _name = 'l10n.bo.product.service.nandina'
    _description = 'L10nBo Product Service Nandina'
    name = fields.Char('Nandina')
    
    l10n_bo_product_service_id = fields.Many2one(
        string='Producto servicio',
        comodel_name='l10n.bo.product.service',
        ondelete='restrict',
    )
    

class SignificantEvent(models.Model):
    _name = 'l10n.bo.significant.event'
    _description = 'L10nBo significant event'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer('Codigo')
    descripcion = fields.Text('Descripcion')
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    name = fields.Char('Name', store=True, compute='_compute_name')

    def getCode(self):
        return self.codigoClasificador

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class CancellationReason(models.Model):
    _name = 'l10n.bo.cancellation.reason'
    _description = 'L10nBo Cancellation Reason'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer('Codigo')
    descripcion = fields.Text('Descripcion')
    name = fields.Char('Nombre', store=True, compute='_compute_name')
    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    def getCode(self):
        return self.codigoClasificador
    
    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class OriginCountry(models.Model):
    _name = 'l10n.bo.origin.country'
    _description = 'L10nBo Origin Country'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer('Codigo')
    descripcion = fields.Text('Descripcion')
    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypeDocumentIdentity(models.Model):
    _name = 'l10n.bo.type.document.identity'
    _description = 'L10nBo Type Document Identity'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer('Codigo')
    descripcion = fields.Text('Descripcion')
    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    def getCode(self):
        return self.codigoClasificador
    
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Name', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )

xsd_names = {
    '1-1': 'facturaElectronicaCompraVenta.xsd',
    '1-24': ''
}


class L10nLatamDocumentType(models.Model):
    _name = 'l10n.bo.document.type'
    _description = 'Sector document type'
    _order = 'codigoClasificador ASC'
    name = fields.Char(string='Nombre',compute='_compute_name')
    codigoClasificador = fields.Integer(string='Código',)
    descripcion = fields.Text(string='Descripción',)
    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    def getCode(self):
        return self.codigoClasificador
    
    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )

class TypeEmision(models.Model):
    _name = 'l10n.bo.type.emision'
    _description = 'L10nBo Type Emision'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer(string='Codigo',required=True)
    descripcion = fields.Text('Descripcion')
    legend = fields.Char(string='Leyenda')
    
    

    def getCode(self):
        return self.codigoClasificador

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    name = fields.Char(
        string='Nombre', 
        store=True, 
        compute='_compute_name'
    )

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypeRoom(models.Model):
    _name = 'l10n.bo.type.room'
    _description = 'L10nBo Type Room'

    codigoClasificador = fields.Integer('Codigo',required=True)
    descripcion = fields.Text('Descripcion')

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypePayment(models.Model):
    _name = 'l10n.bo.type.payment'
    _description = 'Tipo de pago SIAT'
    _order = 'codigoClasificador ASC'
    codigoClasificador = fields.Integer('Codigo',required=True)
    descripcion = fields.Text('Descripcion')

    def getCode(self):
        return self.codigoClasificador

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )



class TypeCurrency(models.Model):
    _name = 'l10n.bo.type.currency'
    _description = 'L10nBo Type Currency'

    codigoClasificador = fields.Integer('Codigo',required=True)
    descripcion = fields.Text('Descripcion')

    def getCode(self):
        return self.codigoClasificador

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypePos(models.Model):
    _name = 'l10n.bo.type.point.sale'
    _description = 'L10nBo Type Point Sale'

    codigoClasificador = fields.Integer('Codigo',required=True)
    descripcion = fields.Text('Descripcion')

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypeInvoice(models.Model):
    _name = 'l10n.bo.type.invoice'
    _description = 'L10nBo Type Invoice'

    codigoClasificador = fields.Integer('Codigo',required=True)     
    descripcion = fields.Text('Descripcion')
    
    nameInReport = fields.Char(string='Nombre en reporte',)
    

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    def getCode(self):
        return self.codigoClasificador

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )


class TypeUnitMeasurement(models.Model):
    _name = 'l10n.bo.type.unit.measurement'
    _description = 'L10nBo Unit Measurement'
    codigoClasificador = fields.Integer('Codigo',required=True)
    descripcion = fields.Text('Descripcion')

    def complete_name(self):
        for leg in self.search([]):
            leg._compute_name()

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )

    name = fields.Char('Nombre', store=True, compute='_compute_name')

    @api.depends('codigoClasificador', 'descripcion')
    def _compute_name(self):
        for leg in self:
            leg.name = '%s - %s' % (leg.codigoClasificador or '', leg.descripcion or '')
    
    def getCode(self):
        return self.codigoClasificador

    def create_records(self, res):
        for activity in res.listaCodigos:
            record_exist = self.search([('codigoClasificador','=',activity.codigoClasificador)], limit=1)
            if record_exist:
                record_exist.write({'descripcion' : activity.descripcion})
            else:
                self.create(
                    {
                        'codigoClasificador': activity.codigoClasificador,
                        'descripcion': activity.descripcion,
                    }
                )
