# -*- coding: utf-8 -*-

from odoo import models, api, fields


class report(models.Model):

    _name = 'report.control'
    _description = 'warehouse control'


    type_kardex = fields.Char(
        string='Kardex',
    )

    
    material_name_id = fields.Many2one(
        string='material_name',
        comodel_name='product.template',
        ondelete='restrict',
    )
    
    
    
    #_inherit = 'x_control_de_almacen'
    '''
    def get_values(self):
        values = +{
            'registro' : self.x_name
        }

        return values

    def _l10n_bo_edi_get_edi_values(self, invoice):
        self.ensure_one()
        values = invoice.l10n_bo_edi_values()
        _l10n_bo_date_emision = fields.Datetime.context_timestamp(invoice.company_id,
                                                                  invoice.l10n_bo_date_emision or datetime.now())
        _document_number = ''
        if invoice.l10n_latam_document_number:
            _document_number = invoice.l10n_latam_document_number.split('-')[2]
        if invoice.l10n_latam_document_type_id_code in ['24']:
            _document_number = invoice.nc_nd_number.split('-')[2]
        _nc_nd_date_emision = False
        if invoice.nc_nd_date_emision:
            _nc_nd_date_emision = fields.Datetime.context_timestamp(invoice.company_id, invoice.nc_nd_date_emision)
        invoice.l10n_bo_v_cuf = invoice._generate_cuf()
        _nc_nd_cash_amount_credit = float(values.get('amount_total', 0.00)) * 0.13
        _cufd = invoice.l10n_bo_pos_id.cufd
        if invoice.l10n_bo_massive_cufd:
            _cufd = invoice.l10n_bo_massive_cufd
        values.update({
            'cafc': invoice.l10n_bo_significant_event_code,
            'modality': invoice.company_id.l10n_bo_code_modality,
            'invoice': invoice,
            'document_number': _document_number,
            'date_emision': _l10n_bo_date_emision.strftime(
                "%Y-%m-%dT%H:%M:%S.000") if invoice.l10n_bo_date_emision else '',
            'issuer': invoice.company_id,
            'cuf': invoice.l10n_bo_v_cuf,
            'cufd': _cufd,
            'customer': invoice.partner_id,
            'uri': '#',
            'nc_nd_original_cuf': invoice.nc_nd_cuf,
            'nc_nd_date_emision': _nc_nd_date_emision.strftime(
                "%Y-%m-%dT%H:%M:%S.000") if invoice.nc_nd_date_emision else '',
            'nc_nd_original_amount_total': invoice.nc_nd_amount_total,
            'nc_nd_amount_returned': values.get('amount_total', 0.00),
            'nc_nd_cash_amount_credit': '%.2f' % _nc_nd_cash_amount_credit
        })

        return values

    def l10n_bo_edi_values(self):
        bob_currency = self.env.ref('base.BOB')
        _vals_amount = self.tax_totals_json or "{}"
        tax_totals_json = json.loads(_vals_amount)
        _detail_amount = 0.00
        _detail_amount_credit = 0.00
        _amount_on_iva = 0.00
        _amount_total = 0.00
        _amount_on_currency = 0.00
        _gift_card_discount = self.amount_gift_card
        _amount_discount = self.discount_percent_global
        _amount_total_iva = 0.00
        _nc_nd_original_amount_total = self.nc_nd_amount_total
        _credit_fiscal = 0.00
        _debit_fiscal = 0.00
        _amount_subtotal = 0.00
        _amount_total = tax_totals_json.get('amount_total', 0.00)
        _amount_on_currency = tax_totals_json.get('amount_total', 0.00)
        _vals_taxes = tax_totals_json.get('groups_by_subtotal', {})
        for tag_key, tax_tuple in _vals_taxes.items():
            for tax_line in tax_tuple:
                tax_group = self.env['account.tax.group'].browse(int(tax_line.get('tax_group_id', False)))
                if tax_group.id:
                    if tax_group.l10n_bo_code == 'IVA':
                        _amount_total_iva += tax_line.get('tax_group_amount', 0.00)
        invoice_line_vals_list = []
        invoice_line_origin_vals_list = []
        _amount_on_iva = tax_totals_json.get('amount_total', 0.00)
        product_default = self.env.ref('l10n_bo_edi.l10n_bo_default_product')
        if self.nc_nd_move_id.id and self.l10n_latam_document_type_id_code in ['29']:
            move_related = self.nc_nd_move_id
            for rec_line in move_related.invoice_line_ids.filtered(
                    lambda line: not line.product_id.global_discount):
                _price_unit = rec_line.price_unit
                _line_discount = rec_line.discount_fixed_total
                _price_subtotal = rec_line.price_subtotal
                product_id = rec_line.product_id if rec_line.product_id.id else product_default
                if self.currency_id.id != bob_currency.id:
                    _price_unit = self.currency_id._convert(_price_unit,
                                                            bob_currency,
                                                            self.company_id,
                                                            self.l10n_bo_date_emision,
                                                            round=True)
                    _line_discount = self.currency_id._convert(_line_discount,
                                                               bob_currency,
                                                               self.company_id,
                                                               self.l10n_bo_date_emision,
                                                               round=True)
                    _price_subtotal = self.currency_id._convert(_price_subtotal,
                                                                bob_currency,
                                                                self.company_id,
                                                                self.l10n_bo_date_emision,
                                                                round=True)
                _detail_amount += _price_subtotal
                _detail_amount_credit += _price_subtotal
                invoice_line_origin_vals_list.append({
                    'nandina': product_id.l10n_bo_nandina_code or '',
                    'product_id': product_id,
                    'default_code': product_id.default_code or '',
                    'line': rec_line,
                    'name': rec_line.name,
                    'quantity': rec_line.quantity,
                    'uom': '%s-%s' % (rec_line.product_uom_id.l10n_bo_catalog_id.sorter_code,
                                      rec_line.product_uom_id.l10n_bo_catalog_id.description),
                    'price_unit': abs(_price_unit),
                    'is_amount_discount': True if _line_discount > 0 else False,
                    'amount_discount': abs(_line_discount),
                    'amount_subtotal': abs(_price_subtotal),
                    'nc_nd_same_transaction': rec_line.nc_nd_same_transaction
                })
        if self.move_type in ['out_refund', 'in_refund', 'out_invoice'] and self.nc_nd_move_id.id and \
                self.l10n_latam_document_type_id_code in ['24']:
            move_related = self.nc_nd_move_id
            for rec_line in move_related.invoice_line_ids.filtered(
                    lambda line: not line.product_id.global_discount):
                _price_unit = rec_line.price_unit
                _line_discount = rec_line.discount_fixed_total
                # if _line_discount > 0:
                #     _price_subtotal = rec_line.price_subtotal
                # else:
                #     _price_subtotal = rec_line.price_total
                _price_subtotal = rec_line.price_total
                product_id = rec_line.product_id if rec_line.product_id.id else product_default
                if self.currency_id.id != bob_currency.id:
                    _price_unit = self.currency_id._convert(_price_unit,
                                                            bob_currency,
                                                            self.company_id,
                                                            self.l10n_bo_date_emision,
                                                            round=True)
                    _line_discount = self.currency_id._convert(_line_discount,
                                                               bob_currency,
                                                               self.company_id,
                                                               self.l10n_bo_date_emision,
                                                               round=True)
                    _price_subtotal = self.currency_id._convert(_price_subtotal,
                                                                bob_currency,
                                                                self.company_id,
                                                                self.l10n_bo_date_emision,
                                                                round=True)
                _detail_amount += _price_subtotal
                _detail_amount_credit += _price_subtotal
                invoice_line_vals_list.append({
                    'product_id': product_id,
                    'default_code': product_id.default_code or '',
                    'line': rec_line,
                    'name': rec_line.name,
                    'quantity': rec_line.quantity,
                    'uom': '%s-%s' % (rec_line.product_uom_id.l10n_bo_catalog_id.sorter_code,
                                      rec_line.product_uom_id.l10n_bo_catalog_id.description),
                    'uom_description': rec_line.product_uom_id.l10n_bo_catalog_id.description,
                    'price_unit': abs(_price_unit),
                    'is_amount_discount': True if _line_discount > 0.00 else False,
                    'amount_discount': abs(_line_discount),
                    'amount_subtotal': abs(_price_subtotal),
                    'nc_nd_same_transaction': rec_line.nc_nd_same_transaction,
                    'is_invoice': False
                })
        for rec_line in self.invoice_line_ids.filtered(
                lambda line: not line.product_id.global_discount):
            _price_unit = rec_line.price_unit
            _line_discount = rec_line.discount_fixed_total
            _line_discount = rec_line.discount_fixed_total
            # if _line_discount > 0:
            #     _price_subtotal = rec_line.price_subtotal
            # else:
            #     _price_subtotal = rec_line.price_total
            _price_subtotal = rec_line.price_total
            _line_original_amount = rec_line.nc_nd_related_move_id.price_total
            product_id = rec_line.product_id if rec_line.product_id.id else product_default
            if self.currency_id.id != bob_currency.id:
                _line_original_amount = self.currency_id._convert(_line_original_amount,
                                                                  bob_currency,
                                                                  self.company_id,
                                                                  self.l10n_bo_date_emision,
                                                                  round=True)
                _price_unit = self.currency_id._convert(_price_unit,
                                                        bob_currency,
                                                        self.company_id,
                                                        self.l10n_bo_date_emision,
                                                        round=True)
                _line_discount = self.currency_id._convert(_line_discount,
                                                           bob_currency,
                                                           self.company_id,
                                                           self.l10n_bo_date_emision,
                                                           round=True)
                _price_subtotal = self.currency_id._convert(_price_subtotal,
                                                            bob_currency,
                                                            self.company_id,
                                                            self.l10n_bo_date_emision,
                                                            round=True)
                _amount_subtotal += _price_subtotal
            _detail_amount += _price_subtotal
            invoice_line_vals_list.append({
                'product_id': product_id,
                'default_code': product_id.default_code or '',
                'line': rec_line,
                'name': rec_line.name,
                'quantity': rec_line.quantity,
                'uom': '%s-%s' % (rec_line.product_uom_id.l10n_bo_catalog_id.sorter_code,
                                  rec_line.product_uom_id.l10n_bo_catalog_id.description),
                'uom_description': rec_line.product_uom_id.l10n_bo_catalog_id.description,
                'price_unit': abs(_price_unit),
                'is_amount_discount': True if _line_discount > 0 else False,
                'amount_discount': abs(_line_discount),
                'amount_subtotal': abs(_price_subtotal),
                'nc_nd_same_transaction': rec_line.nc_nd_same_transaction,
                'original_amount': _line_original_amount,
                'final_amount': _line_original_amount,
                'conciliation_amount': abs(_price_subtotal),
                'is_invoice': True
            })
        if self.nc_nd_move_id.id and self.l10n_latam_document_type_id_code in ['29'] and self.move_type == 'out_refund':
            _credit_fiscal = _amount_total_iva
            _debit_fiscal = 0.00
        else:
            _debit_fiscal = _amount_total_iva
            _credit_fiscal = 0.00

        if self.currency_id.id != bob_currency.id:
            _nc_nd_original_amount_total = self.currency_id._convert(_nc_nd_original_amount_total,
                                                                     bob_currency,
                                                                     self.company_id,
                                                                     self.l10n_bo_date_emision,
                                                                     round=True)
            _credit_fiscal = self.currency_id._convert(_credit_fiscal,
                                                       bob_currency,
                                                       self.company_id,
                                                       self.l10n_bo_date_emision,
                                                       round=True)
            _amount_total_iva = self.currency_id._convert(_amount_total_iva,
                                                          bob_currency,
                                                          self.company_id,
                                                          self.l10n_bo_date_emision,
                                                          round=True)
            _amount_total = self.currency_id._convert(_amount_total,
                                                      bob_currency,
                                                      self.company_id,
                                                      self.l10n_bo_date_emision,
                                                      round=True)
            _amount_on_iva = self.currency_id._convert(_amount_on_iva,
                                                       bob_currency,
                                                       self.company_id,
                                                       self.l10n_bo_date_emision,
                                                       round=True)
            _amount_discount = self.currency_id._convert(_amount_discount,
                                                         bob_currency,
                                                         self.company_id,
                                                         self.l10n_bo_date_emision,
                                                         round=True)
            _gift_card_discount = self.currency_id._convert(_gift_card_discount,
                                                            bob_currency,
                                                            self.company_id,
                                                            self.l10n_bo_date_emision,
                                                            round=True)
        national_spending, _national_fob_amount, list_national_spending = self.get_l10n_bo_national_spending_ids()
        international_expenses, _international_fob_amount, list_international_expenses = self.get_l10n_bo_international_expense_ids()
        _national_fob_amount2 = _national_fob_amount + _detail_amount
        if self.l10n_bo_type_invoice.sorter_code in ['2']:
            _amount_on_iva = 0.00
            # _national_fob_amount = 0.00
            _amount_on_currency = _national_fob_amount2 + _international_fob_amount
            if _amount_on_currency > 0:
                _amount_on_currency = _amount_on_currency - _amount_discount
            if _amount_on_currency > 0:
                _amount_total = _amount_on_currency

        _nc_nd_number = ''
        if self.nc_nd_number:
            _nc_nd_number = self.nc_nd_number.split('-')[2]
        _l10n_latam_document_number = ''
        if self.l10n_latam_document_number:
            _l10n_latam_document_number = self.l10n_latam_document_number.split('-')[2]
        _amount_subtotal =  _detail_amount

        # Monto Gift Card
        _amount_on_iva = _amount_on_iva - _gift_card_discount

        def format_amount_2decimal(amount):
            return '%.2f' % amount

        amounts_json = {
            'format_decimal': format_amount_2decimal,
            'amount_gift_card': '%.2f' % self.amount_gift_card,
            'amount_total': '%.2f' % _amount_total,
            'amount_total_original': '%.2f' % (_amount_total + _amount_discount),
            'amount_on_iva': '%.2f' % _amount_on_iva,
            # 'amount_on_iva': '%.2f' % _amount_total,
            'amount_on_currency': '%.2f' % _amount_on_currency,
            'is_gift_card_discount': True if _gift_card_discount > 0 else False,
            'gift_card_discount': _gift_card_discount,
            'is_amount_discount': True if _amount_discount > 0 else False,
            'amount_discount': '%.2f' % _amount_discount,
            'invoice_line_ids': invoice_line_vals_list,
            'invoice_line_origin_ids': invoice_line_origin_vals_list,
            'force_nit': self.l10n_bo_force_send_vat,
            'qr': self.l10n_bo_v_url_qr,
            'national_spending': national_spending if national_spending else None,
            'list_national_spending': list_national_spending,
            'is_totalGastosNacionalesFob': True if _national_fob_amount2 > 0 else False,
            'amount_national_spending_fob': _national_fob_amount2 if _national_fob_amount2 > 0 else None,
            'list_international_expenses': list_international_expenses,
            'international_expenses': international_expenses if international_expenses else None,
            'amount_international_expenses': _international_fob_amount if _international_fob_amount > 0 else None,
            'detail_amount': '%.2f' % _detail_amount,
            'detail_amount_credit': '%.2f' % _detail_amount_credit,
            'amount_total_iva': '%.2f' % _amount_total_iva,
            'invoice_number': _nc_nd_number,
            'nc_nd_control_code': self.l10n_bo_pos_id.cufd_request_id.control_code,
            'conciliation_amount': _amount_total,
            'original_amount': _nc_nd_original_amount_total,
            'credit_fiscal': '%.2f' % _credit_fiscal,
            'debit_fiscal': '%.2f' % _debit_fiscal,
            'l10n_latam_document_number': _l10n_latam_document_number,
            'amount_subtotal': _amount_subtotal,
            'l10n_bo_card_payment': self.get_l10n_bo_card_payment_obfuscated()
        }
        _logger.info("amounts_json-for-credit")
        _logger.info(amounts_json)
        return amounts_json
    '''