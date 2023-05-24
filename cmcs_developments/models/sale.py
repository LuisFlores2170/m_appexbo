# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class formsale(models.Model):
    _inherit = 'sale.order'

    
    client_code = fields.Char(
        string='Codigo de cliente',
    )

    
    customer_reference_ids = fields.Many2many(
        string='Referencia del cliente',
        comodel_name='client.reference'
    )

    def updatedomain(self):
        self.updateReference()



    @api.onchange('customer_reference_ids')
    def updateReference(self):
        self._cr.execute("UPDATE product_template SET venta=True")
        for record in self:
            if record.customer_reference_ids:
                self._cr.execute("UPDATE product_template SET venta=False WHERE referencia_de_cliente_id is not null")
                    
                for reference in record.customer_reference_ids:
                    
                    id_client = str(reference.id)[6:] if str(reference.id)[6:] != '' else reference.id

                    self._cr.execute("UPDATE product_template SET venta=True WHERE referencia_de_cliente_id = " + str(id_client))
            
    
    

class DomainOrderLine(models.Model):
    _inherit = ['sale.order.line']

    @api.onchange('product_id')
    def domain_line3(self):
        for record in self:
            return {
                'domain': {
                    "product_id": [
                        ('venta','=', True)
                    ]
                }
            }
