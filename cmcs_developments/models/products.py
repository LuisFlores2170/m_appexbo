# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class product_template(models.Model):
    
    _inherit = ['product.template']

    
    referencia_de_cliente_id = fields.Many2one(
        string='Referencias de cliente',
        comodel_name='client.reference',
        ondelete='restrict',
    )
    

    
    venta = fields.Boolean(
        string='venta',
    )
    
    # AUTOMATIZACIONES

    # [AL CREAR]
    @api.constrains("create_date")
    def _constrains_default_code(self):
        for record in self:

            if record.categ_id.id != 1:
                
                # variables
                correlacion = record.categ_id.correlacion if record.categ_id.correlacion != False else record.categ_id.parent_id.correlacion
                correlacion_maxima = record.categ_id.correlacion_maxima if record.categ_id.correlacion_maxima != False else record.categ_id.parent_id.correlacion_maxima

                
                # verificar que se le esta poniendo un codigo manualmente
                if record.default_code != False: 

                    # verifica que el codigo manual este dentro del rango maximo
                    if int(record.default_code) > int(correlacion_maxima): 
                        raise UserError(('SE HA LLEGADO AL LIMITE DE CORRELACIONES DE ESTA CATEGORIA: '+record.categ_id.display_name))
                
                # de lo contrario establece un codigo automatico
                else: 
                    if int(correlacion) > int(correlacion_maxima): # verifica si la correlacion esta fuera del limite
                        raise UserError(('SE HA LLEGADO AL LIMITE DE CORRELACIONES DE ESTA CATEGORIA: '+record.categ_id.display_name)) # se muestra un mensaje de error y cancela todo proceso
                
                    self.increase_correlation()
                    
    # [CAMBIAR - CATEG]
    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        for record in self:
            if record.categ_id.parent_id.id == False: # cuando la categoria no tiene padre
                record['default_code'] = record.categ_id.correlacion
            else:
                record['default_code'] = record.categ_id.parent_id.correlacion

    # [AL GUARDAR - CATEG]
    @api.constrains("categ_id")
    def _constrains_product_id(self):
        for record in self:
            #-------------------------------------------------------------------------------

            if record.categ_id.id != 1:
                
                #----------------------------------------------------------------------------------------------
                # variables
                correlacion = record.categ_id.correlacion if record.categ_id.correlacion != False else record.categ_id.parent_id.correlacion
                correlacion_maxima = record.categ_id.correlacion_maxima if record.categ_id.correlacion_maxima != False else record.categ_id.parent_id.correlacion_maxima

                #-------------------------------------------------------------------------------

                record.default_code = correlacion

                if int(record.default_code) > int(correlacion_maxima):
                    raise UserError(('SE HA LLEGADO AL LIMITE DE CORRELACIONES DE ESTA CATEGORIA : '+record.categ_id.display_name))

                self.increase_correlation()
                

    def increase_correlation(self):
        for record in self:
            # CONTINUAR CORRELACION
            if record.categ_id.correlacion != False:
                record.categ_id.correlacion = str( int(record.categ_id.correlacion) + 1 )

            elif record.categ_id.parent_id.correlacion != False:
                record.categ_id.parent_id.correlacion = str( int(record.categ_id.parent_id.correlacion) + 1 )

    
class product_produc(models.Model):
    
    _inherit = ['product.product']

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        for record in self:
            if record.categ_id.parent_id.id == False: # cuando la categoria no tiene padre
                record['default_code'] = record.categ_id.correlacion
            else:
                record['default_code'] = record.categ_id.parent_id.correlacion
