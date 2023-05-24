# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class workOrder(models.Model):
    _name = 'work.order'
    _description = 'Register work orders'

    #-------------------------------------------------------------------------
    
    name = fields.Char(
        string='Nombre',
        default='ORDEN DE TRABAJO',
        readonly=True 
    )

    
    #-------------------------------------------------------------------------
    
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today,
    )

    #-------------------------------------------------------------------------

    user_id = fields.Many2one(
        string='Aprobado por',
        comodel_name='res.users',
        ondelete='restrict',
    )

    #-------------------------------------------------------------------------
    
    requested_by = fields.Char(
        string='Solicitante',
    )
    
    
    #-------------------------------------------------------------------------

    
    apartment = fields.Selection(
        string='Dpto/Area',
        selection=[('imp', 'IMPRESIÓN'), ('est', 'EXTRUSIÓN'), ('sop', 'SOPLADO'), ('iny', 'INYECCIÓN')]
    )

    #-------------------------------------------------------------------------
    
    client_id = fields.Many2one(
        string='Cliente',
        comodel_name='res.partner',
        ondelete='restrict',
    )

    #-------------------------------------------------------------------------
    
    product_id = fields.Many2one(
        string='Producto',
        comodel_name='product.product',
        ondelete='restrict',
    )

    
    product_code_id = fields.Char(
        string='Codigo',
        readonly=True 
    )
    
    
    
    #-------------------------------------------------------------------------
    
    material = fields.Char(
        string='Material',
        default='PVC'
    )

    #-------------------------------------------------------------------------
    
    
    art_name = fields.Char(
        string='Nombre del arte',
    )
    
    #-------------------------------------------------------------------------

    
    amount = fields.Char(
        string='Cantidad',
    )
    
    #-------------------------------------------------------------------------

    
    approximate_weight = fields.Char(
        string='Peso aproximado',
    )
    
    #-------------------------------------------------------------------------
    
    colors = fields.Char(
        string='Colores',
    )
    
    #-------------------------------------------------------------------------

    
    type_of_cut = fields.Char(
        string='Tipo de corte',
    )
    
    #-------------------------------------------------------------------------
    
    
    pecked = fields.Char(
        string='Picoteado',
    )
    
    #-------------------------------------------------------------------------
    
    logo = fields.Char(
        string='Tiene logotipo',
    )
    
    #-------------------------------------------------------------------------

    
    thickness = fields.Char(
        string='Espesor',
    )
    
    #-------------------------------------------------------------------------
    
    
    sealed = fields.Char(
        string='Sellado',
    )

    #-------------------------------------------------------------------------

    
    printing_colors = fields.Char(
        string='Colores de impresion',
    )
    
    #-------------------------------------------------------------------------

    
    width = fields.Char(
        string='Ancho',
    )

    #-------------------------------------------------------------------------

    
    height = fields.Char(
        string='Largo',
    )
    
    
    #-------------------------------------------------------------------------
    
    
    plate_thickness = fields.Char(
        string='Espesor de la plancha',
    )
    
    #-------------------------------------------------------------------------

    reduction = fields.Char(
        string='Reduccion',
    )
    
    #-------------------------------------------------------------------------
    
    cylinder_roller = fields.Char(
        string='Rodillo / Cilindro',
    )

    #-------------------------------------------------------------------------

    lines_print_repetitions = fields.Char(
        string='Lineas / repeticiones impresion',
    )
    
    #-------------------------------------------------------------------------

    
    printing_system = fields.Char(
        string='Sistema de impresion',
    )
    
    
    #-------------------------------------------------------------------------
    
    
    number_of_labels = fields.Char(
        string='Cantidad de etiquetas',
    )
    
    #-------------------------------------------------------------------------
    
    waste = fields.Char(
        string='Desperdicio',
    )
    
    #-------------------------------------------------------------------------
    
    
    development = fields.Char(
        string='Desarrollo',
    )
    
    
    #-------------------------------------------------------------------------

    
    coil_dimension_sense = fields.Char(
        string='Sentido / Dimencion.',
    )
    
    #-------------------------------------------------------------------------

    
    description = fields.Html(
        string='Descripciones',
    )

    
    description_bool = fields.Boolean(
        string='description_bool',
    )

    
    company_id = fields.Many2one(
        string='compañia',
        comodel_name='res.company',
        ondelete='restrict',
        default=lambda self: self.env.user.company_id
    )
    
    

    #-------------------------------------------------------------------------

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_code_id = self.product_id.default_code

    #-------------------------------------------------------------------------

    @api.constrains("product_id")
    def _constrains_product_id(self):
        self.product_code_id = self.product_id.default_code
    
    #-------------------------------------------------------------------------
    
    # [AL CREAR]
    @api.constrains("create_date")
    def _constrains_name(self):
        prefix = '00000'
        self.name = "ORDEN DE TRABAJO NRO "+prefix[:len(prefix)-len(str(self.id))]+str(self.id)

    #-------------------------------------------------------------------------
    
    # [AL GUARDAR]
    @api.constrains("description")
    def _constrains_description(self):
        if self.description in ["""<p placeholder="Obserbaciones..." class="oe-hint oe-command-temporary-hint"><br></p>""","<p><br></p>"]:
            self.description_bool = False
        else:
            self.description_bool = True