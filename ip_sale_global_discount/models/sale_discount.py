# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrdeDiscount(models.Model):
    _inherit = 'sale.order'

    @api.depends('discount_value', 'discount_type', 'discount_total', 'order_line.price_total')
    def _amount_all(self):
        super()._amount_all()
        for order in self:
            discount = 0.0
            if order.discount_type == 'per':
                discount = order.amount_untaxed * order.discount_value / 100
            if order.discount_type == 'fix':
                discount = order.discount_value

            order.update({
                'discount_total': discount,
                'amount_total': order.amount_total - discount
            })

    discount_type = fields.Selection([('per', 'Percentage'), ('fix', 'Fix Rate')], string='Discount Type')
    discount_value = fields.Float(string="Discount Value")
    discount_total = fields.Monetary(string="Discount", store=True, readonly=True, compute='_amount_all')

    @api.onchange('discount_type', 'discount_value')
    def onchange_discount_type(self):
        if self.discount_type == 'per':
                if self.discount_value < 0 or self.discount_value > 100:
                    raise UserError(_('You Can Not add Value Less Than 0 and Greater Than 100'))
        if self.discount_type == 'fix':
                if self.discount_value > self.amount_untaxed:
                    raise UserError(_('You Can Not add More than Amount In Fix Rate'))

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrdeDiscount, self)._prepare_invoice()
        invoice_vals['discount_type'] = self.discount_type
        discount_value = self.discount_value
        if self.discount_type == 'fix' and self.invoice_ids:
            discount_applied = sum(self.invoice_ids.filtered(
                lambda x: x.state in ['draft', 'posted'] and x.discount_type == 'fix').mapped(
                'discount_value'))
            discount_value -= discount_applied
        invoice_vals['discount_value'] = discount_value if discount_value > 0 else 0
        return invoice_vals
