# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMoveAddDiscount(models.Model):
    _inherit = 'account.move'

    discount_type = fields.Selection([('per', 'Percentage'), ('fix', '  Fix Rate')], string='Discount Type', readonly=True)
    discount_value = fields.Float(string='Discount Value', readonly=True)
    discount_total = fields.Monetary(
        string='Discount', store=True, readonly=True,
        compute="_compute_amount")

    @api.onchange('discount_type', 'discount_value')
    def onchange_discount(self):
        if self.discount_type == 'per':
            if 0 > self.discount_value or self.discount_value > 100:
                raise ValidationError("Please Set Discount (%) Properly betweek 1 to 100 only.")
        if self.discount_type == 'fix':
            if self.amount_total and self.discount_value > self.amount_total:
                raise ValidationError("Please Check Discount value, it should be less then the order value.")

    @api.depends('discount_total', 'amount_total', 'discount_type', 'discount_value')
    def _compute_amount(self):
        super()._compute_amount()
        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            if move.discount_type == 'per':
                move.discount_total = move.amount_untaxed * move.discount_value / 100
            if move.discount_type == 'fix':
                move.discount_total = move.discount_value

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            move.amount_total -= move.discount_total
            move.amount_residual -= move.discount_total
            move.amount_residual_signed -= move.discount_total
            move.amount_total_signed -= move.discount_total
            move.amount_total_in_currency_signed = abs(move.amount_total - move.discount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
            # Compute 'payment_state'.
            total_to_pay = 0.0
            total_residual = 0.0
            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    if line.account_id.user_type_id.type in ('receivable', 'payable'):
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
            currencies = move._get_lines_onchange_currency().currency_id
            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state
