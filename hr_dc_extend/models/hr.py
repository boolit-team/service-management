from openerp import models, fields

class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    #fields
    address_lt_id = fields.Many2one('res.better.zip',string="Home Address in LT")
    phone_lt = fields.Char(string='Phone number in LT')
    address_uk_id = fields.Many2one('res.better.zip',string="Home Address in UK")
    #id_copy_fname = fields.Char('ID Copy Fname', readonly=True) - Temp. disabled
    id_copy = fields.Binary('ID Copy')
    sort_code = fields.Char('Sort Code', size=8)
    nin = fields.Char('NIN', size=9)
    driving_licence = fields.Binary('Driving Licence')
    relatives = fields.Char('Relatives')
    relative_name = fields.Char('Relative Name')
    contact_info = fields.Text('Contact Info')

