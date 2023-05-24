# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class categoryCode(models.Model):
    
    _inherit = ['product.category']

    ''' 
        MAQUINARIA          : 10000 - 19999
        INSUMOS             : 20000 - 29999
        PRODUCTO TERMINADO  : 30000 - 39999
        MATERIA PRIMA       : 40000 - 49999
    '''

    correlacion = fields.Char(
        string='correlacion',
    )


    
    correlacion_maxima = fields.Char(
        string='correlacion maxima',
    )
    
    
    