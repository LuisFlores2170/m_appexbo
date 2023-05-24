# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class product_reference(models.Model):
    _name = 'client.reference'
    _description = 'product reference with clients'

    
    name = fields.Char(
        string='Nombre',
        required=True
    )

    
