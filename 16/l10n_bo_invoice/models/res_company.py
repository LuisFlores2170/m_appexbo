# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import logging

from copy import deepcopy
from lxml import etree
from pytz import timezone
from datetime import datetime
from odoo.exceptions import ValidationError
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from signxml import XMLSigner
from base64 import b64decode, b64encode


_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    
    l10n_bo_code_environment = fields.Selection(string='Tipo de entorno',selection=[('1', 'Producción'), ('2', 'Prueba')],default='2'    )
    l10n_bo_code_modality = fields.Selection(selection=[('1', 'Electronica en linea'), ('2', 'Computarizada en linea')],string='Tipo de modalidad',default='1')
    l10n_bo_code_system = fields.Char(string='Codigo de sistema',)
    l10n_bo_delegate_token = fields.Char(string='Token delegado',)
    
    
    endpoint_2_invoice_codes = fields.Char(string='Codigos de prueba',default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionCodigos?wsdl')
    endpoint_1_invoice_codes = fields.Char(string='Codigos de produccion',default='https://siatrest.impuestos.gob.bo/v2/FacturacionCodigos?wsdl')
    
    endpoint_2_invoice_binding = fields.Char(string='Servicio de prueba',default='https://pilotosiatservicios.impuestos.gob.bo/v2/ServicioFacturacionCompraVenta?wsdl')
    endpoint_1_invoice_binding = fields.Char(string='Servicio de produccion',default='https://siatrest.impuestos.gob.bo/v2/FacturacionCodigos?wsdl')
    
    endpoint_2_wsdl_qr = fields.Char(string='Servicio de prueba',default='https://pilotosiat.impuestos.gob.bo/consulta/QR')
    endpoint_1_wsdl_qr = fields.Char(string='Servicio de produccion',default='https://siat.impuestos.gob.bo/consulta/QR')
    
    
    l10n_bo_catalog_sync_ids = fields.Many2many('l10n.bo.catalog', string='Catalogos para sincronizar')
    l10n_bo_edi_certificate_id = fields.Many2one(comodel_name='l10n.bo.edi.certificate', string="Certificado (BO)")
    cafc = fields.Char(string='Cafc',)

    def get_wsdl_qr(self):
        _wsdl = getattr(self, f'endpoint_{self.l10n_bo_code_environment}_wsdl_qr')
        return _wsdl.strip()

    def getCafc(self):
        if self.cafc:
            return self.cafc
        else:
            raise UserError('La compañia no tiene un codigo Cafc')
    
    # GETTERS
    def getL10nBoCodeEnvironment(self):
        if not self.l10n_bo_code_environment:
            raise UserError('Defina el tipo de entorno')
        return self.l10n_bo_code_environment
    
    def getL10nBoCodeSystem(self):
        if not self.l10n_bo_code_system:
            raise UserError('Defina el codigo de sistema')
        return self.l10n_bo_code_system
    
    def getNit(self):
        if not self.vat:
            raise UserError('Defina el nit de la compañia')
        return self.vat
    
    def getL10nBoCodeModality(self):
        if not self.l10n_bo_code_modality:
            raise UserError('Defina el tipo de modalidad')
        return self.l10n_bo_code_modality

    
    @api.model
    def validate_wsdl(self, _wsdl, _token):
        if _wsdl in [None, False, '']:
            raise UserError(_('SIAT wsdl no configurado'))
        if not _token:
            raise UserError(_('SIAT Token delegado no configurado'))
    

    def get_wsdl_obtaining_codes(self):
        _wsdl = getattr(self, f'endpoint_{self.l10n_bo_code_environment}_invoice_codes')
        self.validate_wsdl(_wsdl, self.l10n_bo_delegate_token)
        return _wsdl, self.l10n_bo_delegate_token
    
    def get_wsdl_invoicing_binding(self):
        _wsdl = getattr(self, f'endpoint_{self.l10n_bo_code_environment}_invoice_binding')
        self.validate_wsdl(_wsdl, self.l10n_bo_delegate_token)
        return _wsdl, self.l10n_bo_delegate_token

    endpoint_2_synchronization = fields.Char(
        string='Sincronización de prueba',
        default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl'
    )

    endpoint_1_synchronization = fields.Char(
        string='Sincronización de producción',
        default='https://siatrest.impuestos.gob.bo/v2/FacturacionSincronizacion?wsdl'
    )
    
    def get_wsdl_data_synchronization(self):
        _wsdl = getattr(self, f'endpoint_{self.l10n_bo_code_environment}_synchronization')
        self.validate_wsdl(_wsdl, self.l10n_bo_delegate_token)
        return _wsdl, self.l10n_bo_delegate_token
    

    
    endpoint_2_operations = fields.Char(
        string='Operaciones de prueba',
        default='https://pilotosiatservicios.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl'
    )
    
    endpoint_1_operations = fields.Char(
        string='Operaciones de produccion',
        default='https://siatrest.impuestos.gob.bo/v2/FacturacionOperaciones?wsdl'
    )

    def get_wsdl_operations(self):
        _wsdl = getattr(self, f'endpoint_{self.l10n_bo_code_environment}_operations')
        self.validate_wsdl(_wsdl, self.l10n_bo_delegate_token)
        return _wsdl, self.l10n_bo_delegate_token


from copy import deepcopy
from lxml import etree
from pytz import timezone
from datetime import datetime
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from signxml import XMLSigner
from base64 import b64decode, b64encode



class Certificate(models.Model):
    _name = 'l10n.bo.edi.certificate'
    _description = 'SIAT Digital Certificate'
    _order = 'date_start desc, id desc'
    _rec_name = 'serial_number'

    content = fields.Binary(string="Certificado", required=True, help="PFX Certificate")
    password = fields.Char( string="Contraseña", help="Passphrase for the PFX certificate")
    serial_number = fields.Char(readonly=True, index=True, help="The serial number to add to electronic documents")
    date_start = fields.Datetime(string="Fecha de inicio",  readonly=True, help="The date on which the certificate starts to be valid")
    date_end = fields.Datetime(string="Fecha de expiracion", readonly=True, help="The date on which the certificate expires")
    company_id = fields.Many2one( string="Compañia", comodel_name='res.company', required=True, default=lambda self: self.env.company)

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    @api.model
    def _get_pe_current_datetime(self):
        bolivian_tz = timezone('America/Lima')
        return datetime.now(bolivian_tz)

    @tools.ormcache('self.content', 'self.password')
    def _decode_certificate(self):
        "Return: _private_key, _cert"
        self.ensure_one()
        cert = pkcs12.load_key_and_certificates(b64decode(self.content), self.password.encode(), default_backend())
        return cert[0], cert[1]

    # -------------------------------------------------------------------------
    # LOW-LEVEL METHODS
    # -------------------------------------------------------------------------

    @api.model
    def create(self, vals):
        record = super(Certificate, self).create(vals)
        if not self.env.company.partner_id.tz:
            raise ValidationError(_('Time Zone no configured in company'))
        bolivian_tz = timezone(self.env.company.partner_id.tz)
        bolivian_dt = self._get_pe_current_datetime()
        try:
            dummy, certificate = record._decode_certificate()
            serial_number = certificate.serial_number
            cert_date_start = bolivian_tz.localize(certificate.not_valid_before)
            cert_date_end = bolivian_tz.localize(certificate.not_valid_after)
        except:
            raise ValidationError(_('There has been a problem with the certificate, some usual problems can be:\n'
                                    '- The password given or the certificate are not valid.\n'
                                    '- The certificate content is invalid.'))
        # Assign extracted values from the certificate
        record.write({
            'serial_number': ('%x' % serial_number)[1::2],
            'date_start': fields.Datetime.to_string(cert_date_start),
            'date_end': fields.Datetime.to_string(cert_date_end),
        })
        if bolivian_dt > cert_date_end:
            raise ValidationError(_('The certificate is expired since %s') % record.date_end)
        return record

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------

    def _sign(self, edi_tree):
        self.ensure_one()
        _private_key, _cert = self._decode_certificate()
        edi_tree_copy = deepcopy(edi_tree)
        etree.SubElement(edi_tree_copy, '{http://www.w3.org/2000/09/xmldsig#}Signature', Id='placeholder',
                         nsmap={None: 'http://www.w3.org/2000/09/xmldsig#'})
        signed_edi_tree = XMLSigner(c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
                                    signature_algorithm=u'rsa-sha256',
                                    digest_algorithm=u'sha256').sign(edi_tree_copy, key=_private_key, cert=[_cert])
        signed_edi_tree = etree.tostring(signed_edi_tree).replace(b'\n', b'')
        return signed_edi_tree
    




#-----------------------------------------------------------------------------------------------------------------------------




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    '''
    def send_invoices_online(self):
        self.company_id.send_invoices_online()

    l10n_bo_type_emision = fields.Many2one(
        related='company_id.l10n_bo_type_emision', 
        readonly=False
    )

    l10n_bo_legend_codes = fields.Many2many(
        related='company_id.l10n_bo_legend_codes', 
        readonly=False
    )

    l10n_bo_support_email = fields.Char(
        related='company_id.l10n_bo_support_email',
        string='Support Email', 
        required=True, 
        readonly=False
    )
    '''

    l10n_bo_edi_certificate_id = fields.Many2one(
        comodel_name='l10n.bo.edi.certificate',
        string="Certificado (BO)",
        related="company_id.l10n_bo_edi_certificate_id",
        readonly=False,
        domain="[('company_id', '=', company_id)]"
    )
    
    l10n_bo_catalog_sync_ids = fields.Many2many(
        related='company_id.l10n_bo_catalog_sync_ids',
        string='Catalogos para sincronizar', 
        readonly=False
    )
    
    

    l10n_bo_code_environment = fields.Selection(
        related='company_id.l10n_bo_code_environment',
        string='Code Environment',
        readonly=False,
        help='Describes the type of environment used, the allowed '
    )

    
    l10n_bo_code_modality = fields.Selection(
        related='company_id.l10n_bo_code_modality', 
        string='Code Modality',
        readonly=False,
        help='Modality used by the Billing Computer System for the')
    
    l10n_bo_code_system = fields.Char(
        related='company_id.l10n_bo_code_system', 
        string='System Code', 
        readonly=False,
        help='System Code that was assigned at the time of making the authorization.')

    l10n_bo_delegate_token = fields.Char(
        related='company_id.l10n_bo_delegate_token', 
        string='Delegate Token',
        readonly=False, 
        help='Request through your SIAT portal, necessary for all SIAT'
    )
    
    endpoint_2_invoice_codes = fields.Char(
        related='company_id.endpoint_2_invoice_codes', 
        string='Codigos de prueba',
        readonly=False 
    )

    endpoint_1_invoice_codes = fields.Char(
        related='company_id.endpoint_1_invoice_codes', 
        string='Codigos de produccion',
        readonly=False 
    )

    
    cafc = fields.Char(
        string='Cafc',    
        related='company_id.cafc',
        readonly=False
    )
        
    