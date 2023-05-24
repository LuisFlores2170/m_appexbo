# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'


    
    
    analytic_account_id = fields.Many2one(
        string='analytic account',
        comodel_name='account.analytic.account',
        ondelete='restrict',
        help='This is a reference to account analytic ',
        
        
        
    )

    
    account_analytic_ids = fields.Many2many(
        string='account_analytic',
        comodel_name='account.analytic.account'
    )

    
    code_name = fields.Char(
        string='code',
        default='New',
        
        readonly=True, 
        
    )
    



    @api.model
    def create(self, vals):
        
        if vals.get('code_name'):
            
            if vals['code_name'] == 'New':
                vals['code_name'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        
        result = super(ResPartner, self).create(vals)
        return result

    

    
    
    


    