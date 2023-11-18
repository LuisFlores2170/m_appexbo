# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class GlobalDiscountWizard(models.TransientModel):
    _name = 'global.discount.wizard'
    _description = 'Discount Global Wizard'

    name = fields.Monetary('Amount Discount')
    currency_id = fields.Many2one('res.currency', copy=False)
    quantity = fields.Float()
    move_id = fields.Many2one('account.move', string='Move', copy=False)
    type_discount = fields.Selection([('fixed', 'Monto'), ('percentage', 'porcentaje')], string='Tipo', default='fixed')
    percentage_discount_global = fields.Float('porcentaje de descuento')

    @api.onchange('percentage_discount_global')
    def _onchange_percentage_discount_global(self):
        _name = (self.percentage_discount_global * (self.move_id.amount_total_signed + abs(
            self.move_id.discount_percent_global)))

        self.update({'name': _name})

    def create_discount(self):
        self.move_id.write({'percentage_discount_global': self.percentage_discount_global})
        discount_line = self.move_id.invoice_line_ids.filtered(lambda l: l.product_id.global_discount)
        if discount_line.ids:
            discount_line[0].write({'price_unit': -abs(self.name)})
        else:
            product_disc = self.env['product.product'].search([('global_discount', '=', True)], limit=1)
            self.move_id.write({
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_disc.id,
                    'price_unit': -abs(self.name),
                    'quantity': 1
                })]})

    def button_apply(self):
        if self.name >= abs(self.move_id.amount_total_signed) + abs(self.move_id.discount_percent_global):
            raise ValidationError(_('Descuento no puede superar el precio'))
        if self.name <= 0:
            raise ValidationError(_('Descuento tiene que ser mayor a cero'))
        self.create_discount()
