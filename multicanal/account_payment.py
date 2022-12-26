    
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models, fields
from odoo.exceptions import UserError, Warning
    
class AccountPayment(models.Model):
    _inherit = "account.payment"
 
    es_canal_2 = fields.Boolean(string="Es canal 2", compute='_compute_canal_2', read_only=False, store=True)
    

    @api.depends("date")
    def _compute_canal_2(self):
        for rec in self:
            rec.es_canal_2 = rec.payment_group_id.es_canal_2
            
         #   company_id = rec.company_id.id or self.env.company.id
         #   domain = [('company_id', '=', company_id),('es_canal_2', '=', rec.es_canal_2), ('type', 'in', ('bank', 'cash'))]
         #   rec.journal_id = self.env['account.journal'].search(domain, limit=1)
         #   return {'domain':{'journal_id':domain}}
        
        

    @api.onchange("es_canal_2")
    def _compute_diario_2(self):
        for m in self:       
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id),('es_canal_2', '=', m.es_canal_2), ('type', 'in', ('bank', 'cash'))]
            m.journal_id = self.env['account.journal'].search(domain, limit=1)
            return {'domain':{'journal_id':domain}}
      
