# -*- coding: utf-8 -*-

from odoo import fields, models, api, _



class stock_quant(models.Model):
    
    _inherit = ['stock.quant']
    
    
    ref_default_code = fields.Char(
        string='Codigo',
        related='product_id.default_code',
        readonly=True
    )

    ref_descripcion = fields.Char(
        string='Descripcion',
        related='product_id.name',
        readonly=True
    )

    
class stock_valuation_layer(models.Model):
    
    _inherit = ['stock.valuation.layer']
    
    
    ref_default_code = fields.Char(
        string='Codigo',
        related='product_id.default_code',
        readonly=True
    )

    ref_descripcion = fields.Char(
        string='Descripcion',
        related='product_id.name',
        readonly=True
    )
    
class stock_move_line(models.Model):
    
    _inherit = ['stock.move.line']
    
    
    ref_default_code = fields.Char(
        string='Codigo',
        related='product_id.default_code',
        readonly=True
    )

    ref_descripcion = fields.Char(
        string='Descripcion',
        related='product_id.name',
        readonly=True
    )
    