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
    action = fields.Selection([('delete', 'Delete'), ('update', 'Update'), ('add', 'Add')], 'Action', required=True)
    day = fields.Selection(WEEK_DAYS, 'Week Day')
    time_from = fields.Float('Change From')
    time_to = fields.Float('Change To')
    change_id = fields.Many2one('recurrent.rule.change', 'Rule Change')
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_change_time_rel', 'change_time_id', 'employee_id', 'Employees')
    weeks = fields.Integer('Weeks', help="How many weeks to generate."
        "\n0 means generate only this week starting from now + 1 hour", default=0)   

class recurrent_rule_change(models.TransientModel):
    _name = 'recurrent.rule.change'
    _description = 'Recurrent Rule Change Wizard'
    date_from = fields.Datetime('Change From', required=True, default=datetime.now())
    date_to = fields.Datetime('Change to')
    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar')
    rule_id = fields.Many2one('calendar.service.recurrent.rule', 'Rule', required=True)
    change_time_ids = fields.One2many('recurrent.rule.change.time', 'change_id', 'Change Times')
    change_type = fields.Selection([('permanent', 'Permanent'), ('once', 'One Time')], 
        'Change Type', required=True, help="Choosing 'One Time', it only modifies calendar.\nChoosing 'Permanent', it also updates rules")

    @api.one
    def _add_rule_item(self, change_time):
        """
        Adds rule item in specified rule if type is 'permanent'. 
        Also generates services from specified rule item
        """
        if change_time.weeks < 0:
            raise Warning(_("Weeks can't be negative!"))
        calendar_item = self.env['calendar.service.calendar']
        if self.change_type == 'permanent':
            employee_ids = []
            for empl in change_time.employee_ids:
                employee_ids.append(empl.id)            
            calendar_item.create({
                'cleaning_day': change_time.day, 
                'clean_time_from': change_time.time_from, 
                'clean_time_to': change_time.time_to, 
                'employee_ids': [(6, 0, employee_ids)],
                'rule_id': self.rule_id.id,
            })
        current_address = self.env['res.partner.address_archive'].search(
            [('partner_id', '=', self.rule_id.partner_id.id), ('current', '=', True)])            
        now1 = calendar_item.set_utc(datetime.today() + timedelta(hours=1), check_tz=False) #Setting UTC to now1 and date_from to be able to compare.
        date_from = calendar_item.set_utc(datetime.strptime(self.date_from, "%Y-%m-%d %H:%M:%S"), check_tz=False)
        for week in range(change_time.weeks+1): 
            ref_time = datetime.today() + timedelta(weeks=week) 
            start_time = change_time.calendar_id.relative_date(
                ref_time, change_time.day, change_time.time_from)
            end_time = change_time.calendar_id.relative_date(
                ref_time, change_time.day, change_time.time_to)
            if (start_time > now1) and (start_time >= date_from):
                serv_vals = {
                    'start_time': start_time, 'end_time': end_time,
                    'user_id': self.rule_id.user_id.id, 'work_type': 'recurrent',
                    'rule_calendar_id': calendar_item.id,'partner_id': self.rule_id.partner_id.id,
                }
                service = self.env['calendar.service'].create(serv_vals)
                service_work = self.env['calendar.service.work']
                for empl in change_time.employee_ids:                    
                    service_work.create({
                    'start_time': start_time, 'end_time': end_time,
                    'employee_id': empl.id, 'work_type': 'recurrent',
                    'address_archive_id': current_address.id,
                    'partner_id': self.rule_id.partner_id.id, 'note': self.rule_id.partner_id.comment, 
                    'attention': self.rule_id.partner_id.attention, 'service_id': service.id,})


    @api.one
    def change_rule(self):
        """
        Changes already generated calendar service records
        and if change_type == 'permanent' changes rules 
        according to specific change_rule. Skips updates
        for records that would otherwise be changed into past time.
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
            if not self.change_time_ids:
                raise Warning(_('You must enter at least one change time!'))
            cal_serv_cal = self.env['calendar.service.calendar']
            rule_changes = []
            now1 = cal_serv_cal.set_utc(datetime.today() + timedelta(hours=1), check_tz=False)
            for change_time in self.change_time_ids:
                if change_time.action == 'add':  #skips rest of the iteration, because using add, it is not relevant to continue.
                    self._add_rule_item(change_time)
                    continue
                if change_time.calendar_id.rule_id.id != self.rule_id.id:
                    raise Warning(_('Calendar item does not match Rule!'))
                service_domain.extend((('start_time', '>=', self.date_from), 
                    ('rule_calendar_id', '=', change_time.calendar_id.id), ('state', '=', 'open')))
                services = self.env['calendar.service'].search(service_domain)
                if not services:
                    raise Warning(_('No Services were Found!'))
                for service in services: #using for, because there might be generated records for more then present week (for future weeks too!)
                    if change_time.action == 'delete':
                        service.unlink()
                    elif change_time.action == 'update':
                        start_time = cal_serv_cal.relative_date(
                            datetime.strptime(service.start_time, "%Y-%m-%d %H:%M:%S"), change_time.day, change_time.time_from)
                        end_time = cal_serv_cal.relative_date(
                            datetime.strptime(service.end_time, "%Y-%m-%d %H:%M:%S"), change_time.day, change_time.time_to)
                        if start_time > now1:
                            service.write({'start_time': start_time, 'end_time': end_time})
                            for work in service.work_ids:
                                work.write({'start_time': start_time, 'end_time': end_time})
                if self.change_type == 'permanent': #checking for action second time, because herer it is needed only once (to not repeat more).
                    if change_time.action == 'delete':
                        change_time.calendar_id.unlink()
                    elif change_time.action == 'update':
                        rule_changes.append({'id': change_time.calendar_id.id,'cleaning_day': change_time.day, 
                            'clean_time_from': change_time.time_from, 'clean_time_to': change_time.time_to})
            for change in rule_changes: #Applying write at the end of the method to bypass null constraint violation
                item = cal_serv_cal.search([('id', '=', change['id'])])
                if item:
                    item.write({'cleaning_day': change['cleaning_day'], 
                        'clean_time_from': change['clean_time_from'], 'clean_time_to': change['clean_time_to']})
                    

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