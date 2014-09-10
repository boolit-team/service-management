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

    @api.one
    def create_timesheet_activity(self):
        #TODO - FINISH IT!
        if self.account_id:
            cal_serv_cal = self.env['calendar.service.calendar']
            start_time = cal_serv_cal.str_to_dt(self.start_time)
            end_time = cal_serv_cal.str_to_dt(self.end_time)
            duration = cal_serv_cal.get_duration(start_time, end_time)
            #vals = {'date': date.today() }
            pass

