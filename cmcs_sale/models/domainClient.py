# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------------

from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------

class DomainOrderLine(models.Model):
    _inherit = ['sale.order.line']

    @api.onchange('product_id')
    def domain_line3(self):
        for record in self:
            return {
                'domain': {
                    "product_id": [
                        ('x_studio_venta','=', True)
                    ]
                }
            }

#------------------------------------------------------------------------------------

class FormSale(models.Model):
    
    _inherit = ['sale.order']

    #-------------------------------------------------------------------------------------------------------
    
    @api.onchange('x_studio_many2many_referencia_de_clientes', 'x_studio_actualizar')
    def updateReference(self):
        try:
            self._cr.execute("UPDATE product_template SET x_studio_venta=True")
            for record in self:
                if record.x_studio_many2many_referencia_de_clientes:
                    try:
                        self._cr.execute("UPDATE product_template SET x_studio_venta=False WHERE x_studio_many2one_referencia_de_clientes is not null")
                    except:
                        raise UserError(_('NO SE PUDO DISPONER DE TODOS LOS PRODUCTOS SIN REFERENCIA'))

                    for reference in record.x_studio_many2many_referencia_de_clientes:
                        try:
                            self._cr.execute("UPDATE product_template SET x_studio_venta=True WHERE x_studio_many2one_referencia_de_clientes = " + str(reference.id)[6:])
                        except:
                            raise UserError(_('NO SE PUDO ACTUALIZAR EL DOMINIO DE LOS PRODUCTOS'))
                record.x_studio_actualizar = True
        except:
            raise UserError(_('NO SE PUDO DISPONER DE TODOS LOS PRODUCTOS'))
    
    
    #-------------------------------------------------------------------------------------------------------
    
    # [VENTA - GUARDAR]
    @api.constrains('order_line','warehouse_id')
    def _check_order_line(self):
        for record in self:
            for line in record.order_line:
                if line.product_id.categ_id.id ==1:
                    if line.product_id.qty_available <= 0:
                        raise UserError(_("AL AGREGAR. NO EXISTE STOCK DEL PRODUCTO: "+line.name))
    
    #-------------------------------------------------------------------------------------------------------
    
    # [VENTA - CONFIRMAR]
    @api.constrains('state')
    def _check_state(self):
        for record in self:
            if record.state == "sale":
                for line in record.order_line:
                    
                    # [CONTROL DE SOLO COTIZACION]
                    if line.product_id.categ_id.id ==1:
                        raise UserError("AL CONFIRMAR. EL PRODUCTO: "+line.name+". SOLO ESTA DISPONIBLE PARA COTIZAR")
                    
                    # [CONTROL DE VENTA DE STOCK]
                    if line.product_id.detailed_type != "service":
                        if line.product_id.qty_available<=0 or line.product_uom_qty > line.product_id.qty_available:
                            raise UserError("AL CONFIRMAR. EL PRODUCTO: "+line.name+". NO TIENE STOCK.")
