# -*- coding: utf-8 -*-

from odoo import models, api, fields

class color(models.Model):
    _name = "color"
    _description = "Colors of references"

    
    name = fields.Char(
        string='name',
    )
    