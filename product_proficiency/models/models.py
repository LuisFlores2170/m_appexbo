from odoo import models, api, fields, _
import logging

_logger = logging.getLogger('MENSAJE DE LOG: ')
    

class ProductProduct(models.Model):
    _inherit = ['product.product']
    
    
    location_ids = fields.One2many(
        string='Almacénes',
        comodel_name='product.product.proficiency',
        inverse_name='product_id',
    )
    


class productProductProficiency(models.Model):
    _name = 'product.product.proficiency'
    _description = 'product proficiency'

    
    name = fields.Char(
        string='name',        
        default='Registro'
    )

    
    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.product',
        ondelete='restrict',
    )

    
    location_id = fields.Many2one(
        string='Ubicacion',
        comodel_name='stock.location',
    )


    


    
    
class stockQuant(models.Model):
    _inherit = ['stock.quant']
    
    @api.model
    def create(self, vals):
        stock_quant_id = super(stockQuant, self).create(vals)

        if stock_quant_id.location_id:
            stock_quant_id.add_location()

        return stock_quant_id
    
    def add_location(self):
        if self.location_id.id not in [ location_id.id for location_id in self.product_id.location_ids]:
            self.product_id.location_ids.create(
                {
                    'location_id' : self.location_id.id ,
                    'product_id' : self.product_id.id
                }
            )
            
    def unlink(self):
        for record in self:
            if record.location_id:
                for line in record.product_id.location_ids:
                    if line.location_id.id == record.location_id.id:
                        line.unlink()
        return super(stockQuant, self).unlink()
    

class SaleOrder(models.Model):
    _inherit = ['sale.order.line']

    @api.onchange('product_id')
    def domain_line_product_id(self):
        for record in self:
            return {
                'domain': {
                    "product_id": [
                        ('location_ids.location_id.id','=', record.warehouse_id.lot_stock_id.id)
                    ]
                }
            }
    