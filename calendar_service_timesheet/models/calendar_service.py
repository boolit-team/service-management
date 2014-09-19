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
from openerp.exceptions import Warning
from openerp.tools.translate import _
from datetime import date

class calendar_service_work(models.Model):
    _inherit = 'calendar.service.work'

    account_id = fields.Many2one('account.analytic.account', 'Timesheet Account', domain=[('type', '=', 'normal'), 
        ('use_timesheets', '=', True)])
    timesheet_id = fields.Many2one('hr.analytic.timesheet', 'Timesheet Line')

    @api.one
    def set_timesheet_activity(self):
        """
        Creates or updates Timesheet activity using Service Work data
        """
        if self.account_id and self.service_id:
            cal_serv_cal = self.env['calendar.service.calendar']
            start_time = cal_serv_cal.str_to_dt(self.start_time)
            end_time = cal_serv_cal.str_to_dt(self.end_time)
            duration = cal_serv_cal.get_duration(start_time, end_time)
            name = "%s Work for %s" % (self.service_id.name, self.service_id.partner_id.name)
            if self.service_id.user_id:
                user_id = self.service_id.user_id.id
            else:
                user_id = self.env.uid
            vals = {'date': end_time.date(),  'officer': True, 'unit_amount': duration,
                'user_id': user_id, 'employee_id': self.employee_id.id, 
                'account_id': self.account_id.id, 'name': name, 'journal_id': self.employee_id.journal_id.id,
                'product_id': self.employee_id.product_id.id, 'product_uom_id': self.employee_id.product_id.uom_id.id,
                'amount': -(duration * self.employee_id.product_id.standard_price),
            }

            timesheet_obj = self.env['hr.analytic.timesheet']
            if not self.timesheet_id:
                timesheet = timesheet_obj.create(vals)
                self.timesheet_id = timesheet.id
            else:
                timesheet = timesheet_obj.search([('id', '=', self.timesheet_id.id)])
                timesheet.write(vals)

class calendar_service(models.Model):
    _inherit = 'calendar.service'

    @api.one
    def close_state(self):
        super(calendar_service, self).close_state()
        for work in self.work_ids:
            work.set_timesheet_activity()

class calendar_service_calendar(models.Model):
    _inherit = 'calendar.service.calendar'

    account_id = fields.Many2one('account.analytic.account', 'Timesheet Account', domain=[('type', '=', 'normal'), 
        ('use_timesheets', '=', True)])

    @api.onchange('employee_ids')    
    def onchange_employee_ids(self):
        if self.employee_ids:
            self.account_id = self.employee_ids[0].default_account_id.id #defaults to first employee timesheet account

class calendar_service_recurrent(models.Model):
    _inherit = 'calendar.service.recurrent'

    @api.one
    def create_service(self,service_obj, service_work_obj, start_time, end_time, 
        cal_rec, rule, current_address, change_time=None):
        """
        Creates Calendar service and its works. 
        Only use change_time when creating it from rule change wizard!
        """
        service = service_obj.create({
            'start_time': start_time, 'end_time': end_time,
            'user_id': rule.user_id.id, 'work_type': 'recurrent',
            'rule_calendar_id': cal_rec.id, 
            'product_id': change_time.product_id.id if change_time else cal_rec.product_id.id, #exception for early change_time use
            'partner_id': rule.partner_id.id,
        })
        if change_time:
            cal_rec = change_time
        for empl in cal_rec.employee_ids:
            service_work_obj.create({
                'start_time': start_time, 'end_time': end_time,
                'employee_id': empl.id, 'work_type': 'recurrent',
                'address_archive_id': current_address.id, 'account_id': cal_rec.account_id.id,
                'partner_id': rule.partner_id.id, 'note': rule.partner_id.comment, 
                'attention': rule.partner_id.attention, 'service_id': service.id,
                'ign_rule_chk': True, #ign_rule_chk lets prevent istelf constraining.                                
            })    
