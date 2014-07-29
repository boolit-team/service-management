from openerp import models, fields

class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    #fields
    address_lt_id = fields.Many2one('res.better.zip',string="Home Address in LT")
    address_uk_id = fields.Many2one('res.better.zip',string="Home Address in UK")