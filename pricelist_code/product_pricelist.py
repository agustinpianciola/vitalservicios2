
from itertools import chain

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime
from odoo.tools.misc import formatLang, get_lang


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
      
    #ZVT
    
    
    margen_1 = fields.Float('Margen 1')
    margen_2 = fields.Float('Margen 2')
    margen_3 = fields.Float('Margen 3')
    
    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        """Compute the unit price of a product in the context of a pricelist application.
           The unused parameters are there to make the full context available for overrides.
        """
        self.ensure_one()
        date = self.env.context.get('date') or fields.Date.today()
        convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))
        if self.compute_price == 'fixed':
            price = convert_to_price_uom(self.fixed_price)
        elif self.compute_price == 'percentage':
            price = (price - (price * (self.percent_price / 100))) * ((1+self.margen_1) * (1+self.margen_2)* (1+self.margen_3)) or 0.0
        else:
            # complete formula
            price_limit = price
            price = (price - (price * (self.price_discount / 100))) * ((1+self.margen_1) * (1+self.margen_2)* (1+self.margen_3))  or 0.0
            if self.base == 'standard_price':
                price_currency = product.cost_currency_id
            elif self.base == 'pricelist':
                price_currency = self.currency_id  # Already converted before to the pricelist currency
            else:
                price_currency = product.currency_id
            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            def convert_to_base_price_currency(amount):
                return self.currency_id._convert(amount, price_currency, self.env.company, date, round=False)

            if self.price_surcharge:
                price_surcharge = convert_to_base_price_currency(self.price_surcharge)
                price_surcharge = convert_to_price_uom(price_surcharge)
                price += price_surcharge

            if self.price_min_margin:
                price_min_margin = convert_to_base_price_currency(self.price_min_margin)
                price_min_margin = convert_to_price_uom(price_min_margin)
                price = max(price, price_limit + price_min_margin)

            if self.price_max_margin:
                price_max_margin = convert_to_base_price_currency(self.price_max_margin)
                price_max_margin = convert_to_price_uom(price_max_margin)
                price = min(price, price_limit + price_max_margin)
        return price
