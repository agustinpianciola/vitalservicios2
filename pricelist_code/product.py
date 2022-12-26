class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"
    
    #ZVT
    
    descuento_1 = fields.Float('Descuento 1')
    descuento_2 = fields.Float('Descuento 2')
    descuento_3 = fields.Float('Descuento 3')
    descuento_4 = fields.Float('Descuento 4')
    descuento_5 = fields.Float('Descuento 5')
    
    gastos_1 = fields.Float('Gastos 1%')
    gastos_2 = fields.Float('Gastos 2%')
    gastos_3 = fields.Float('Gastos $')
    
    costo_neto = fields.Float('Costo neto producto', compute='_compute_costo_final')
    
    #ZVT
    
    @api.depends('costo_neto','price','descuento_1','descuento_2', 'descuento_3', 'descuento_4','descuento_5', 'gastos_1', 'gastos_2','gastos_3')
    def _compute_costo_final(self):
        for record in self:
            record.costo_neto = record.price * (1-record.descuento_1) * (1-record.descuento_2)* (1-record.descuento_3)* (1-record.descuento_4)* (1-record.descuento_5)*(1+record.gastos_1)*(1+record.gastos_2) + record.gastos_3
            record.product_tmpl_id.standard_price=record.costo_neto
