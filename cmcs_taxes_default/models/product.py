from odoo import models, fields
import re

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_default_taxes(self):
        sale_tax = False
        company_tax = self.env.company.account_sale_tax_id
        sale_tax_ids = self.env['ir.config_parameter'].sudo().get_param('product_taxs.sale_tax_ids')
        if sale_tax_ids:
            string_to_convert = re.sub("account.tax|\(|\)", "", sale_tax_ids)
            sale_tax = tuple(map(int, string_to_convert.split(', ')))
        # if not sale_tax:
        #     return company_tax
        # else:
        #     sale_tax.append(self.env.company.account_sale_tax_id)

        return sale_tax

    taxes_id = fields.Many2many('account.tax',
                                'product_taxes_rel',
                                'prod_id', 'tax_id',
                                help="Default taxes used when selling the product.",
                                string='Customer Taxes',
                                domain=[('type_tax_use', '=', 'sale')],
                                default=get_default_taxes)