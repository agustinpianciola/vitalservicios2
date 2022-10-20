# -*- coding: utf-8 -*-
from odoo import api, models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        res = super(AccountPaymentRegister,
                    self)._get_wizard_values_from_batch(batch_result)
        if res.get('partner_type') == 'customer':
            move_id = self.env['account.move'].browse(
                self._context.get('active_id'))
            if res.get('source_amount') < 0:
                res['source_amount'] += move_id.discount_total
                res['source_amount_currency'] += move_id.discount_total
            else:
                res['source_amount'] -= move_id.discount_total
                res['source_amount_currency'] -= move_id.discount_total
        return res
