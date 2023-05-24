# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    
    
    default_code = fields.Char(
        string='Codigo',
        default='',
        
    )
    

