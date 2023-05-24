import re
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Dos campos ->
    sale_tax_ids = fields.Many2many('account.tax', string="Default Sale Tax",readonly=False)

    def set_values(self):
        # Modificas el set_value
        res = super(ResConfigSettings, self).set_values()
        # Modulo + Campo
        self.env['ir.config_parameter'].set_param(
            'product_taxs.sale_tax_ids',self.sale_tax_ids
        )
        return res
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        sale_tax_parameter = self.env['ir.config_parameter'].sudo().get_param('product_taxs.sale_tax_ids') or False

        sale_tax = False

        if sale_tax_parameter:
            string_to_convert = re.sub("account.tax|\(|\)", "", sale_tax_parameter)
            if string_to_convert == '':
                sale_tax = False
            else:
                sale_tax = tuple(map(int, string_to_convert.split(', ')))
        
        res.update(
            sale_tax_ids=sale_tax,
        )

        return res