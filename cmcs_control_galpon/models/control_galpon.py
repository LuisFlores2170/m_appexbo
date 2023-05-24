# -*- coding: utf-8 -*-

from odoo import models, api, fields

class controlGalpon(models.Model):
    _name = "control.galpon"
    _description = "Control de galpones"

    
    state = fields.Selection(
        string='state',
        selection=[('draft', 'Borrador'), ('done', 'Realizado'), ('cancel', 'Cancelado')],
        default='draft'
    
    )
    
    

    
    kardex = fields.Selection(
        string='kardex',
        selection=[('PT', 'PRODUCTO TERMINADO'), ('MP', 'MATERIA PRIMA')]
    )
    
    
    galpon_id = fields.Many2one(
        string='galpon',
        comodel_name='stock.location',
        ondelete='restrict',
    )

    
    description = fields.Char(
        string='description',
    )

    
    material_id = fields.Many2one(
        string='material',
        comodel_name='product.product',
    )

    
    periodo = fields.Date(
        string='periodo',
        default=fields.Date.context_today,
    )

    
    user_id = fields.Many2one(
        string='user',
        comodel_name='res.users',
        ondelete='restrict',
    )

    
    consume_lines_ids = fields.One2many(
        string='consume_lines',
        comodel_name='control.galpon.line',
        inverse_name='galpon_id',
    )


    def action_done(self):
        self.state = 'done'
        
    
    def action_cancel(self):
        self.state = 'cancel'
    
    def action_draft(self):
        self.state = 'draft'
    
    

#---------------------------------------------------------------------------------------------

class controlGalponLine(models.Model):
    _name = "control.galpon.line"
    _description = "Control de lineas de consumo"

    
    galpon_id = fields.Many2one(
        string='galpon',
        comodel_name='control.galpon',
        ondelete='restrict',
    )
    
    
    date = fields.Datetime(
        string='date',
        default=fields.Datetime.now,
    )

    
    internal_document = fields.Char(
        string='internal_document',
    )
    
    
    details = fields.Char(
        string='details',
    )

    
    type_of_material = fields.Selection(
        string='type_of_material',
        selection=[('PE', 'PE'), ('PP', 'PP'),('PVC', 'PVC'), ('RECICLADO', 'RECICLADO'),('PIGMENTOS', 'PIGMENTOS')]
    )

    
    udm_id = fields.Many2one(
        string='udm',
        comodel_name='uom.uom',
        ondelete='restrict',
    )

    
    qty_unidades = fields.Float(
        string='qty_unidades',
    )
    
    
    
    
    imput_in_kilogram = fields.Float(
        string='input in kilogram',
    )

    output_in_kilogram = fields.Float(
        string='output in kilogram',
    )

    
    output_central = fields.Float(
        string='output_central',
    )

    
    saldo = fields.Float(
        string='saldo',
    )
    
    
    
    
    
    
    
    
