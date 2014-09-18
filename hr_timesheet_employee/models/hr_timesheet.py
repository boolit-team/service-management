# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import Warning, RedirectWarning
from openerp.tools.translate import _

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    officer = fields.Boolean('User is Officer')

class hr_analytic_timesheet(models.Model):
    _inherit = 'hr.analytic.timesheet'

    @api.model
    def _getEmployeeProduct(self):
        if self.env.context is None:
            self.env.context = {}        
        if not self.officer:
            emp_obj = self.env['hr.employee']
            emp = emp_obj.search([('user_id', '=', self.env.context.get('user_id') or self.env.uid)], limit=1)
        else:
            emp = self.employee_id
        if emp:
            if emp.product_id:
                return emp.product_id.id
        return False

    @api.model
    def _getEmployeeUnit(self):
        if self.env.context is None:
            self.env.context = {}        
        if not self.officer:
            emp_obj = self.env['hr.employee']
            emp = emp_obj.search([('user_id', '=', self.env.context.get('user_id') or self.env.uid)], limit=1)
        else:
            emp = self.employee_id
        if emp:
            if emp.product_id:
                return emp.product_id.uom_id.id
        return False

    @api.model
    def _getGeneralAccount(self):
        if self.env.context is None:
            self.env.context = {}        
        if not self.officer:
            emp_obj = self.env['hr.employee']
            emp = emp_obj.search([('user_id', '=', self.env.context.get('user_id') or self.env.uid)], limit=1)
        else:
            emp = self.employee_id
        if emp:
            if bool(emp.product_id):
                a = emp.product_id.property_account_expense.id
                if not a:
                    a = emp.product_id.categ_id.property_account_expense_categ.id
                if a:
                    return a
        return False

    @api.model
    def _getAnalyticJournal(self):
        if self.env.context is None:
            self.env.context = {}
        if not self.officer:
            emp_obj = self.env['hr.employee']
            if self.env.context.get('employee_id'):
                emp = emp_obj.search([('id', '=', context.get('employee_id'))])
            else:
                emp = emp_obj.search([('user_id','=', self.env.context.get('user_id') or self.env.uid)], limit=1)
        else:
            emp = self.employee_id
        if not emp:
            model, action_id = self.env['ir.model.data'].get_object_reference('hr', 'open_view_employee_list_my')
            msg = _("Employee is not created for this user. Please create one from configuration panel.")
            raise RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        if emp.journal_id:
            return emp.journal_id.id
        else :
            raise Warning(_('No analytic journal defined for \'%s\'.\n'
                'You should assign an analytic journal on the employee form.') % (emp.name)) 

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.product_id = self._getEmployeeProduct()
            self.product_uom_id = self._getEmployeeUnit()
            self.general_account_id = self._getGeneralAccount()
            self.journal_id = self._getAnalyticJournal()
            self.account_id = self.employee_id.default_account_id.id 

    @api.model
    def create(self, vals):
        if self.env.context is None:
            self.env.context = {}
        if not vals.get('officer'):
            emp_obj = self.env['hr.employee']        
            emp = emp_obj.search([('user_id', '=', self.env.context.get('user_id') or self.env.uid)], limit=1)
        else:
            emp = self.employee_id
        ename = ''
        if emp:
            ename = emp.name
        if not vals.get('journal_id',False):
           raise Warning(_('No \'Analytic Journal\' is defined for employee %s \n'
            'Define an employee for the selected user and assign an \'Analytic Journal\'!') % (ename))
        if not vals.get('account_id',False):
           raise Warning(_('No analytic account is defined on the project.\n'
            'Please set one or we cannot automatically fill the timesheet.'))
        return super(hr_analytic_timesheet, self).create(vals)         

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    default_account_id = fields.Many2one('account.analytic.account', 'Default Timesheet Account', domain=[('type', '=', 'normal'), 
        ('use_timesheets', '=', True)])   