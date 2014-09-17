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
    
    week_busyness = fields.Float(string='Planned Week Hrs', compute="_compute_busyness")
    week_work_avg = fields.Float(string="Average Planned Hrs", compute="_compute_busyness", help="Between two weeks (Recurrent)")

    @api.one
    @api.depends('contract_id')
    def _compute_busyness(self):
        self.week_busyness = 0.0
        self.week_work_avg = 0.0
        if self.contract_id and self.contract_id.track_calendar:
            service_work = self.env['calendar.service.work']
            busyness = round(service_work._get_week_dur(self.id), 2)
            busy_week1 = service_work._get_week_dur(self.id, week_nmb=-1, recurrent=True)
            busy_week2 = service_work._get_week_dur(self.id, recurrent=True)
            self.week_busyness = busyness
            self.week_work_avg = round((busy_week1 + busy_week2) / 2, 2)