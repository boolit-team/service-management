from openerp import models, fields

class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    #fields
    salary_per_h = fields.Float(string="Salary per Hour")
    arrive_to_uk = fields.Date('Arrive to UK')
    start_work_uk = fields.Date('Start Work in UK')
    end_work_uk = fields.Date('End Work in UK')
    fixed_salary = fields.Boolean('Fixed Salary?')