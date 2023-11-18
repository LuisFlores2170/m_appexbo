# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class messageList(models.Model):
    _name = "message.code"
    _description = "Codigo de mensaje"

    
    
    name = fields.Datetime(
        string='Fecha',
        default=fields.Datetime.now,
    )
    
    
    
    message_code_id = fields.Many2one(
        string='Mensaje',
        comodel_name='l10n.bo.message.service'
    )
    
    
    
    error = fields.Char(
        string='Error',
    )
    
    model = fields.Char(
        string='Modelo',
        
    )
    