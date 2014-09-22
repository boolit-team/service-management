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
from openerp import models, api

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def getDuration(self, payslip):
        duration = 0.0
        tsheet_obj = self.env['hr.analytic.timesheet']
        timesheets = tsheet_obj.search([('employee_id', '=', self.id), 
            ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('officer', '=', True)])
        if self.user_id: #also add timesheets if only user is selected 
            tsheet_add = tsheet_obj.search([('user_id', '=', self.user_id.id), 
            ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('officer', '=', False)])
            timesheets += tsheet_add
        for tsheet in timesheets: #counting duration from timesheets
            duration += tsheet.unit_amount   
        return duration
