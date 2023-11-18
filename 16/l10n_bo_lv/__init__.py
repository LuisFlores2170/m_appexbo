#-*- coding:utf-8 -*-

from . import models

# AL INSTALAR
def post_install_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    
    #------------------------------------------------------------
    # res.partner
        
    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env['res.company'].sudo().browse(SUPERUSER_ID)
    company.partner_id.write({'tz': 'America/La_Paz'})