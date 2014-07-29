from openerp import models, fields

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    #fields
    salary_per_h = fields.Float(string="Salary per Hour")