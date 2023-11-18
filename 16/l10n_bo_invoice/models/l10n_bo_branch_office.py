# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo.exceptions import UserError
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