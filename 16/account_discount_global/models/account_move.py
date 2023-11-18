from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # @api.model
    # def create(self, vals):
    #     if 'product_id' in vals or 'price_unit' in vals:
    #         product = self.env['product.product'].browse(int(vals['product_id']))
    #         if product.global_discount:
    #             vals['price_unit'] = -abs(vals['price_unit'])
    #     return super(AccountMoveLine, self).create(vals)
    #
    # def write(self, vals):
    #     if 'product_id' in vals or 'price_unit' in vals:
    #         _product_id = self.product_id.id
    #         if 'product_id' in vals:
    #             _product_id = vals['product_id']
    #         product = self.env['product.product'].browse(_product_id)
    #         if product.global_discount:
    #             vals['price_unit'] = -abs(vals['price_unit'])
    #     _logger.info("def write(self, vals)")
    #     _logger.info(vals)
    #     rslt = super(AccountMoveLine, self).write(vals)
    #     return rslt


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_discount_global = fields.Float('Global Discount Amount', copy=False)
    percentage_discount_global = fields.Float('Porcentaje de descuento', copy=False)

    discount_percent_global = fields.Float(
        string='Descuento Global',
        compute='_compute_amount',
        store=True
    )
    discount_gift_card = fields.Float(
        string='Descuento Gift Card',
        compute='_compute_amount',
        store=True
    )

    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        self._compute_discount_percent_global()
        self._compute_discount_gift_card()

    def _compute_discount_percent_global(self):
        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if line.product_id.global_discount: # not line.exclude_from_invoice_tab and  V15
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += abs(line.price_unit * line.quantity)
            discount_percent_global = abs(total_untaxed_currency if len(currencies) == 1 else abs(total_untaxed))
            value = move.amount_untaxed + discount_percent_global
            move.discount_percent_global = discount_percent_global
            # move.discount_percent_global = (discount_percent_global / value) * 100 if value != 0 else 0

            # if subtotal advance != 0
            number_invoice_lines = 0
            for line in move.invoice_line_ids:
                number_invoice_lines += 1
                if number_invoice_lines == 1 and line.product_id.global_discount:
                    move.discount_percent_global = 0.00

    def _compute_discount_gift_card(self):
        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if line.product_id.gift_card: # not line.exclude_from_invoice_tab and  V15
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
            discount_percent_global = abs(total_untaxed_currency if len(currencies) == 1 else abs(total_untaxed))
            value = move.amount_untaxed + discount_percent_global
            move.discount_gift_card = discount_percent_global
            # move.discount_percent_global = (discount_percent_global / value) * 100 if value != 0 else 0

            # if subtotal advance != 0
            number_invoice_lines = 0
            for line in move.invoice_line_ids:
                number_invoice_lines += 1
                if number_invoice_lines == 1 and line.product_id.gift_card:
                    move.discount_gift_card = 0.00


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    global_discount = fields.Boolean(string='¿Es descuento global?')
    gift_card = fields.Boolean(string='Descuento Gift Card')
