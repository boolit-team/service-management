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
WORK_TYPE = [('recurrent', 'Recurrent'), ('one', 'One Time'), ('wait', 'Waiting')]
STATE = [('open', 'Open'), ('done', 'Done'), ('cancel', 'Canceled')]
ONE_TIME = [('out', 'Move Out'), ('in', 'Move In'), ('built', 'After Building'),
    ('spring', 'Spring Cleaning'), ('alternate', 'Alternates Cleaners')]

CANCEL_REASON = [('no_reason', 'Last min. Without Reason'), ('reason', 'Last min. Without Reason'), 
    ('prior_notify', 'Prior Notification'), ('no_notify', 'Did not Notify'), 
    ('holiday', 'Holiday'), ('change_time', 'Change Cleaning Time')]
REASON = [('illness', 'Illness'), ('unexpect', 'Unexpected Problems'), ('else', 'Else')]
PRIOR_NOTIFY = ([('repair', 'Repair'), ('vacation', 'Vacation'), ('illness', 'Illness'), ('else', 'Else')])
NO_NOTIFY = [('nobody_home', 'Nobody was at Home'), ('cant_enter', 'Couldn\'t Enter'), ('else', 'Else')]

def get_weekday(nmb):
    weekdays = {
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
        3: 'Wednesday', 4: 'Friday', 5: 'Saturday',
        6: 'Sunday'
    }
    return weekdays[nmb]
def relative_date(reference, weekday, timevalue):
    hour, minute = divmod(timevalue, 1)
    minute *= 60
    days = reference.weekday() - weekday
    return (reference - timedelta(days=days)).replace(
        hour=int(hour), minute=int(minute), second=0, microsecond=0)

class calendar_service_work(models.Model):
    _name = 'calendar.service.work'
    _description = 'Services Work Management Through Calendar'

    name = fields.Char('Subject', size=128)
    note = fields.Text('Note')
    employee_id = fields.Many2one('hr.employee', 'Responsible', required=True)
    start_time = fields.Datetime('Starting at', required=True)
    end_time = fields.Datetime('Ending at', required=True)
    description = fields.Text('Description')
    attention = fields.Text('Attention!')
    duration = fields.Float('Duration')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)])
    address_archive_id = fields.Many2one('res.partner.address_archive', 'Current Address')
    service_id = fields.Many2one('calendar.service', 'Service', ondelete='cascade')
    work_type = fields.Selection(WORK_TYPE, 'Type', required=True)
    state = fields.Selection(STATE, 'State', readonly=True, default='open', track_visibility='onchange')

    @api.one
    def close_state(self):
        self.state = 'done'

    @api.one
    def cancel_state(self):
        self.state = 'cancel'    

    @api.onchange('partner_id')
    def onhange_partner_id(self):
        if self.partner_id:
            for address in self.partner_id.address_archive_ids:
                if address.current:
                    self.address_archive_id = address.id
            self.note = self.partner_id.comment
            self.attention = self.partner_id.attention

    @api.onchange('service_id')
    def onchange_service_id(self):
        if self.service_id:
            self.start_time = self.service_id.start_time
            self.end_time = self.service_id.end_time
            self.work_type = self.service_id.work_type
            self.partner_id = self.service_id.partner_id and self.service_id.partner_id.id or False

class calendar_service(models.Model):
    _name = 'calendar.service'
    _description = 'Calendar Service'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Service No.', default='/', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)])
    start_time = fields.Datetime('Starting at', required=True)
    end_time = fields.Datetime('Ending at', required=True)
    work_type = fields.Selection(WORK_TYPE, 'Type', required=True)
    one_time = fields.Selection(ONE_TIME, 'One Time Type')
    work_ids = fields.One2many('calendar.service.work', 'service_id', 'Works')
    state = fields.Selection(STATE, 'State', readonly=True, default='open', track_visibility='onchange')
    cancel_reason = fields.Selection(CANCEL_REASON, 'Cancel Reason')
    no_reason_specify = fields.Char('Specify')
    reason = fields.Selection(REASON, 'Reason')
    reason_unexpected_specify = fields.Char('Specify')
    reason_specify = fields.Char('Specify')
    prior_notify = fields.Selection(PRIOR_NOTIFY, 'Notification')
    prior_notify_specify = fields.Char('Specify')
    no_notify = fields.Selection(NO_NOTIFY, 'No Notification')
    no_notify_speficy = fields.Char('Specify')
    cleaning_calendar_ids = fields.One2many('crm.lead.cleaning_calendar', 'service_id', 'Cleaning Time')
    canceled_until = fields.Date('Canceled Until')
    opportunity_id = fields.Many2one('crm.lead', 'Related Opportunity', domain=[('type', '=', 'opportunity')])
    user_id = fields.Many2one('res.users', 'Salesman')

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].get('calendar.service') or '/'
        return super(calendar_service, self).create(vals)

    @api.one
    def close_state(self):
        self.state = 'done'
        for work in self.work_ids:
            work.state = 'done'

    @api.one
    def cancel_state(self):
        self.state = 'cancel'
        for work in self.work_ids:
            work.state = 'cancel'

class calendar_service_calendar(models.Model):
    _name = 'calendar.service.calendar'
    _description = 'Calendar Service Working Time'

    name = fields.Char('Calendar', size=64)
    cleaning_day = fields.Selection(WEEK_DAYS, 'Week Day', required=True)
    clean_time_from = fields.Float('From', required=True)
    clean_time_to = fields.Float('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_calendar_rel', 'calendar_id', 'employee_id', 'Employees')
    rule_id = fields.Many2one('calendar.service.recurrent.rule', 'Rule')

    @api.multi
    def name_get(self):
        result = []
        name = self._rec_name
        if name in self._fields:
            for record in self:
                rec_name = []
                if record.name:
                    rec_name.append(record.name)
                rec_name.append(get_weekday(record.cleaning_day))
                rec_name.append("%s - %s" % (record.clean_time_from, record.clean_time_to))
                if record.rule_id.partner_id:
                    rec_name.append("/ %s" % (record.rule_id.partner_id.name))
                result.append((record.id, ", ".join(rec_name)))    
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))
        return result

class calendar_service_recurrent(models.Model):
    _name = 'calendar.service.recurrent'
    _description = 'Recurrent Calendar Services'

    name = fields.Char('Name', size=64)
    active = fields.Boolean('Active', default=True)
    rule_ids = fields.One2many('calendar.service.recurrent.rule', 'recurrent_id', 'Rules')

    @api.one
    def generate_recurrent(self): #TODO - Finish It!
        if self.active:
            ref_time = datetime.today()
            service_obj = self.env['calendar.service']
            for rule in self.rule_ids:
                current_address = self.env['res.partner.address_archive'].search(
                    [('partner_id', '=', rule.partner_id.id), ('current', '=', True)])
                for cal_rec in rule.calendar_ids:
                    start_time = relative_date(ref_time, cal_rec.cleaning_day, cal_rec.clean_time_from)
                    end_time = relative_date(ref_time, cal_rec.cleaning_day, cal_rec.clean_time_to)
                    service = service_obj.create({
                        'start_time': start_time, 'end_time': end_time,
                        'user_id': rule.user_id.id, 'work_type': 'recurrent',
                        'partner_id': rule.partner_id.id,
                    })
                    service_work_obj = self.env['calendar.service.work']
                    for empl in cal_rec.employee_ids:
                        service_work_obj.create({
                            'start_time': start_time, 'end_time': end_time,
                            'employee_id': empl.id, 'work_type': 'recurrent',
                            'address_archive_id': current_address.id,
                            'partner_id': rule.partner_id.id, 'note': rule.partner_id.comment, 
                            'attention': rule.partner_id.attention, 'service_id': service.id,                                
                        })

class calendar_service_recurrent_rule(models.Model):
    _name = 'calendar.service.recurrent.rule'
    _description = 'Recurrent Calendar Services Rules'
    user_id = fields.Many2one('res.users', 'Salesman')
    name = fields.Char('Rule Name')
    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)])
    calendar_ids = fields.One2many('calendar.service.calendar', 'rule_id', 'Cleaning Time')

    @api.multi
    def name_get(self):
        result = []
        name = self._rec_name
        if name in self._fields:
            for record in self:
                rec_name = []
                if record.name:
                    rec_name.append(record.name)
                if record.partner_id:
                    rec_name.append(record.partner_id.name)
                result.append((record.id, ", ".join(rec_name)))    
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))
        return result    
