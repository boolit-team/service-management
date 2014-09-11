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
        """
        When closing service, it also creates/updates Sale Order
        if product_id is set on service. Also creates timesheet 
        activity if analytic account is set.
        """
        if self.product_id:
            cal_serv_cal = self.env['calendar.service.calendar']
            order_obj = self.env['sale.order']                      
            vals = {'partner_id': self.partner_id.id, 'date_order': self.end_time,
                'pricelist_id': self.partner_id.property_product_pricelist.id,
                'user_id': self.user_id.id, 'calendar_service_id': self.id,
            }  
            start_time = cal_serv_cal.str_to_dt(self.start_time)
            end_time = cal_serv_cal.str_to_dt(self.end_time)
            qty = round(cal_serv_cal.get_duration(start_time, end_time), 3) #converting duration as qty in hours              
            line_vals = {'product_id': self.product_id.id, 'product_uom_qty': qty,}                      
            if not self.order_id or (self.order_id and self.order_id.state == 'cancel'):
                order = order_obj.create(vals)
                self.order_id = order.id
                line_vals['order_id'] = order.id
                self.env['sale.order.line'].create(line_vals)
            elif self.order_id.state == 'draft':
                order = self.order_id.write(vals)
                for line in self.order_id.order_line:
                    line.write(line_vals)
        self.state = 'done'
        for work in self.work_ids:
            work.set_timesheet_activity()
            work.state = 'done'    

