from . import models

from odoo import api, SUPERUSER_ID

# AL INSTALAR
def post_install_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    
    #------------------------------------------------------------
    # res.partner
        
    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env['res.company'].sudo().browse(SUPERUSER_ID)
    company.partner_id.write({'tz': 'America/La_Paz'})

    #------------------------------------------------------------
    # account.edi.format
    '''
    edi_format = env['account.edi.format'].create({'name':'Factura (BO)', 'code':'bo_siat'})
    journal_ids = env['account.journal'].search([('type','=','sale')])
    for jounal_id in journal_ids:
        jounal_id.write({'edi_format_ids': [(6,0,[edi_format.id])]})
    '''