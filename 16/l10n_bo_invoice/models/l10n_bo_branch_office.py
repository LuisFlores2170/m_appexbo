# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import UserError
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class L10nBoBranchOffice(models.Model):
    _name = 'l10n.bo.branch.office'
    _description = 'CUIS Request'

    
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
        copy=False
    )
    address = fields.Text(string='Dirección',)
    l10n_bo_pos_ids = fields.One2many(string='Puntos de venta',comodel_name='l10n.bo.pos',inverse_name='branch_office_id')
    
    def getCode(self):
        return self.code