# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Operation_Types(models.Model):
    
    _inherit = ['stock.picking.type']

    
    name_in_report = fields.Char(
        string='Nombre en reportes',
    )
    
    