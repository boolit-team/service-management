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
from openerp.exceptions import Warning
from openerp.tools.translate import _

WEEK_DAYS = [
    (5, 'Saturday'),
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
]

class recurrent_rule_change_time(models.TransientModel):
    _name = 'recurrent.rule.change.time'
    _description = 'Recurrent Rule Change Time'

    calendar_id = fields.Many2one('calendar.service.calendar', 'Cleaning Time')
    action = fields.Selection([('delete', 'Delete'), ('update', 'Update')], 'Action', required=True)
    day = fields.Selection(WEEK_DAYS, 'Week Day')
    time_from = fields.Float('Change From')
    time_to = fields.Float('Change To')
    change_id = fields.Many2one('recurrent.rule.change', 'Rule Change')    

class recurrent_rule_change(models.TransientModel):
    _name = 'recurrent.rule.change'
    _description = 'Recurrent Rule Change Wizard'
    date_from = fields.Datetime('Change From', required=True)
    date_to = fields.Datetime('Change to')
    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar')
    rule_id = fields.Many2one('calendar.service.recurrent.rule', 'Rule')
    change_time_ids = fields.One2many('recurrent.rule.change.time', 'change_id', 'Change Times')
    change_type = fields.Selection([('permanent', 'Permanent'), ('once', 'One Time')], 'Change Type', required=True)

    @api.one
    def change_rule(self):
        """
        Changes already generated calendar service records
        and if change_type == 'permanent' changes rules 
        according to specific change_rule
        """
        if self.date_from and self.rule_id:
            service_domain = []
            if self.date_to:
                date_from = datetime.strptime(self.date_from, '%Y-%m-%d %H:%M:%S')
                date_to = datetime.strptime(self.date_to, '%Y-%m-%d %H:%M:%S')
                if date_to < date_from:
                    raise Warning(_('Date To can\'t be lower than Date From!'))
                service_domain.append(('date_to', '<=', self.date_to))
            partner = self.rule_id.partner_id
            for change_time in self.change_time_ids:
                if change_time.calendar_id.rule_id.id != self.rule_id.id:
                    raise Warning(_('Calendar item does not match Rule!'))
                service_domain.extend((('start_time', '>=', self.date_from), 
                    ('rule_calendar_id', '=', change_time.calendar_id.id), ('state', '=', 'open')))
                service = self.env['calendar.service'].search(service_domain)
                if service:
                    if change_time.action == 'delete':
                        service.unlink()
                    elif change_time.action == 'update':
                        cal_serv_cal = self.env['calendar.service.calendar']
                        start_time = cal_serv_cal.relative_date(
                            datetime.strptime(service.start_time, "%Y-%m-%d %H:%M:%S"), change_time.day, change_time.time_from)
                        end_time = cal_serv_cal.relative_date(
                            datetime.strptime(service.end_time, "%Y-%m-%d %H:%M:%S"), change_time.day, change_time.time_to)
                        service.write({'start_time': start_time, 'end_time': end_time})
                        for work in service.work_ids:
                            work.write({'start_time': start_time, 'end_time': end_time})
                else:
                    raise Warning(_('No Services were Found!'))

    #TODO - Might need to rewrite it
    '''
    def onchange_rule_id(self, cr, uid, rule_id, context=None):
        res = {}
        if rule_id:
            domain = {}
            rule = self.pool.get('calendar.service.recurrent.rule').browse(cr, uid, rule_id, context=context)
            domain['change_time_ids.calendar_id']
        return {'domain': domain}
    '''