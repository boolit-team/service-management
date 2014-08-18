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
from openerp import models, fields
from openerp import api
from datetime import datetime, timedelta
class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    week_busyness = fields.Float(string='Week Busyness (Hours)', compute="_compute_busyness")

    @api.one
    @api.depends('contract_id')
    def _compute_busyness(self):
        self.week_busyness = 0.0
        if self.contract_id and self.contract_id.track_calendar:
            busyness = 0.0
            dt = datetime.now()
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = dt - timedelta(days=dt.weekday())
            week_end = week_start + timedelta(days=6)
            week_start = week_start.strftime("%Y-%m-%d %H:%M:%S")
            week_end = week_end.strftime("%Y-%m-%d %H:%M:%S")
            works = self.env['calendar.service.work'].search(
                [('employee_id', '=', self.id), ('start_time', '>=', week_start), ('end_time', '<=', week_end)])
            for work in works:
                start_time = datetime.strptime(work.start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(work.end_time, "%Y-%m-%d %H:%M:%S")
                dif = end_time - start_time
                hours = dif.total_seconds() / 3600
                busyness += hours
            self.week_busyness = round(busyness, 2)
             
