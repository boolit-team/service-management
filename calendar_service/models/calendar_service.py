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

from openerp import models, fields, api, SUPERUSER_ID
from datetime import datetime, timedelta
from openerp.exceptions import Warning
from openerp.tools.translate import _
import pytz

WEEK_DAYS = [
    ('S', 'Saturday'),
    ('M', 'Monday'),
    ('T', 'Tuesday'),
    ('W', 'Wednesday'),
    ('Th', 'Thursday'),
    ('F', 'Friday'),
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
    ign_rule_chk = fields.Boolean('Ignore Rule Check')

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

    @api.one
    @api.constrains('start_time', 'end_time', 'employee_id', 'state', 'work_type')
    def _check_resource(self):
        cal_serv_cal = self.env['calendar.service.calendar']
        recs = self.search([('id', '!=', self.id), 
            ('employee_id', '=', self.employee_id.id), ('state', '=', 'open'), ('work_type', '!=', 'wait'), 
            ('start_time', '<', self.end_time), ('end_time', '>', self.start_time)])
        for rec in recs:
            start_time = cal_serv_cal.set_tz(datetime.strptime(rec.start_time, "%Y-%m-%d %H:%M:%S"))
            end_time = cal_serv_cal.set_tz(datetime.strptime(rec.end_time, "%Y-%m-%d %H:%M:%S"))
            warn_str = "%s Already Assigned from %s to %s in Service %s for %s" % \
                (rec.employee_id.name, start_time, end_time, rec.service_id.name, rec.partner_id.name)
            raise Warning(_(warn_str))
        #Checks Rules if that time is already reserved for any of it
        if self.state == 'open' and self.work_type != 'wait' and not self.ign_rule_chk:
            start_time = cal_serv_cal.set_tz(datetime.strptime(self.start_time, 
                cal_serv_cal.get_dt_fmt()))
            weekday = cal_serv_cal.get_rev_weekday(start_time.weekday()) #get weekday in calendar.service.calendar
            start_h = start_time.hour
            start_min = round(float(start_time.minute) / 60, 2)
            time_from = float(start_h + start_min)
            end_time = cal_serv_cal.set_tz(datetime.strptime(self.end_time, 
                cal_serv_cal.get_dt_fmt()))
            end_h = end_time.hour
            end_min = round(float(end_time.minute) / 60, 2)
            time_to = float(end_h + end_min)
            recurrent = self.env['calendar.service.recurrent'].search([('active', '=', True)])
            cal_recs = cal_serv_cal.search([('employee_ids', 'in', [self.employee_id.id]), 
                ('rule_id.recurrent_id', '=', recurrent.id), ('weekday', '=', weekday), 
                ('time_from', '<', time_to), ('time_to', '>', time_from)])
            for cal_rec in cal_recs:
                raise Warning(_("There is rule already defined for \n"
                    "%s to work at %s from %s to %s !" % (self.employee_id.name, 
                    cal_serv_cal.get_weekday(weekday), cal_rec.time_from, cal_rec.time_to)))
            

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
    cleaning_calendar_ids = fields.One2many('crm.lead.cleaning_calendar', 'service_id', 'Work Time')
    canceled_until = fields.Date('Canceled Until')
    opportunity_id = fields.Many2one('crm.lead', 'Related Opportunity', domain=[('type', '=', 'opportunity')])
    user_id = fields.Many2one('res.users', 'Salesman')
    rule_calendar_id = fields.Many2one('calendar.service.calendar', 'Rule Calendar Item')

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].get('calendar.service') or '/'
        return super(calendar_service, self).create(vals)

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('work_type'):
                for work in rec.work_ids:
                    work.work_type = vals.get('work_type')
        return super(calendar_service, self).write(vals)

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
    weekday = fields.Selection(WEEK_DAYS, 'Week Day', required=True)
    time_from = fields.Float('From', required=True)
    time_to = fields.Float('To', required=True)
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
                rec_name.append(self.get_weekday(record.weekday))
                rec_name.append("%s - %s" % (record.time_from, record.time_to))
                if record.rule_id.partner_id:
                    rec_name.append("/ %s" % (record.rule_id.partner_id.name))
                result.append((record.id, ", ".join(rec_name)))    
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))
        return result

    @api.model
    def relative_date(self, reference, weekday, timevalue):
        hour, minute = divmod(timevalue, 1)
        minute *= 60
        days = reference.weekday() - weekday
        dt = (reference - timedelta(days=days)).replace(
            hour=int(hour), minute=int(minute), second=0, microsecond=0)
        dt = self.set_utc(dt)
        return dt

    @api.model
    def get_weekday(self, key, name=True):
        if name:
            weekdays = {
                'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday',
                'Th': 'Thursday', 'F': 'Friday', 'S': 'Saturday',
                'Sn': 'Sunday',
            }
        else:
            weekdays = {
                'M': 0, 'T': 1, 'W': 2,
                'Th': 3, 'F': 4, 'S': 5,
                'Sn': 6,
            }            
        return weekdays[key]

    @api.model
    def get_rev_weekday(self, key):
        """
        Returns weekday letter from weekday 
        number (reverse of get_weekday())
        """
        weekdays = {
            0: 'M', 1: 'T', 2: 'W',
            3: 'Th', 4: 'F', 5: 'S',
            6: 'Sn',
        }
        return weekdays[key]            

    @api.model
    def get_dt_fmt(self):
        """
        returns standard datetime format
        """
        return "%Y-%m-%d %H:%M:%S"

    @api.model
    def set_utc(self, dt, check_tz=True):
        """
        Sets UTC timezone, so user would see correct time from GUI.
        """
        if check_tz:
            local_tz = pytz.timezone(self.env.user.tz)
            dt = local_tz.localize(dt)
            dt = dt.astimezone(pytz.utc)
        else:
            dt = dt.replace(tzinfo=pytz.utc)
        return dt

    @api.model
    def set_tz(self, dt):
        """
        Sets Timezone that user is living in.
        """
        local_tz = pytz.timezone(self.env.user.tz)
        dt = dt.replace(tzinfo=pytz.utc)
        dt = dt.astimezone(local_tz)
        return dt

    @api.one
    @api.constrains('time_to', 'time_from')
    def _check_calendar(self):
        if self.time_to < self.time_from:
            raise Warning(_("End time can\'t be lower than Start!"))

    @api.one
    @api.constrains('weekday', 'time_from', 'time_to', 'employee_ids')
    def _check_resource(self):
        for empl in self.employee_ids:
            items = self.search(
                [('id', '!=', self.id), ('employee_ids', 'in', [empl.id]), 
                ('weekday', '=', self.weekday), ('time_from', '<', self.time_to), 
                ('time_to', '>', self.time_from)])
            for item in items:
                raise Warning(_("%s is already assigned to work at '%s %s - %s' for %s!\n"
                    "You tried to assign %s to work at '%s %s - %s' for %s'.") % 
                    (empl.name, self.get_weekday(item.weekday), 
                        item.time_from, item.time_to, item.rule_id.partner_id.name,
                        empl.name, self.get_weekday(self.weekday), self.time_from, 
                        self.time_to, self.rule_id.partner_id.name))


class calendar_service_recurrent(models.Model):
    _name = 'calendar.service.recurrent'
    _description = 'Recurrent Calendar Services'

    name = fields.Char('Name', size=64)
    active = fields.Boolean('Active', default=True)
    rule_ids = fields.One2many('calendar.service.recurrent.rule', 'recurrent_id', 'Rules')
    init_weeks = fields.Integer('Initial Weeks', 
        help="How Initially many weeks to generate. \n0 means generate only this week starting from now + 1 hour", default=8)
    weeks = fields.Integer('Weeks', default=1)
    next_gen_time = fields.Datetime('Next Generate Time', readonly=False)
    init = fields.Boolean('Init')

    @api.model
    def _get_week_range(self):
        if self.init:
            return self.init_weeks + 1 #to run at least once           
        else:
            return self.weeks

    @api.one
    def set_next_gen_time(self):
        if self.init:
            cal_serv_cal = self.env['calendar.service.calendar']
            weeks = self.init_weeks + 1 # we need to jump to the next week after the last one generated (+1).
            next_gen_time = datetime.today() + timedelta(weeks=weeks)
            next_gen_time = next_gen_time - timedelta(days=next_gen_time.weekday()) #Set it to monday
            next_gen_time = next_gen_time.replace(hour=0, minute=0, second=0, microsecond=0)
            next_gen_time = cal_serv_cal.set_utc(next_gen_time) #set time back to UTC
        else:
            next_gen_time = datetime.strptime(self.next_gen_time, "%Y-%m-%d %H:%M:%S") + timedelta(weeks=self.weeks)
        self.next_gen_time = next_gen_time        

    @api.one
    def generate_recurrent(self):
        if self.active:
            cal_serv_cal = self.env['calendar.service.calendar']
            now1 = cal_serv_cal.set_utc(datetime.today() + timedelta(hours=1), check_tz=False)
            service_obj = self.env['calendar.service']
            service_work_obj = self.env['calendar.service.work']
            for rule in self.rule_ids:
                current_address = self.env['res.partner.address_archive'].search(
                    [('partner_id', '=', rule.partner_id.id), ('current', '=', True)])
                for cal_rec in rule.calendar_ids:
                    for week in range(self._get_week_range()):
                        if not self.init:
                            ref_time = datetime.strptime(self.next_gen_time, "%Y-%m-%d %H:%M:%S") + timedelta(weeks=week, days=1) #add day to jump to next week
                            now1 = cal_serv_cal.set_utc(datetime.strptime(self.next_gen_time, "%Y-%m-%d %H:%M:%S"), check_tz=False)
                        else:
                            ref_time = datetime.today() + timedelta(weeks=week)                            
                        start_time = cal_rec.relative_date(ref_time, 
                            cal_rec.get_weekday(cal_rec.weekday, name=False), cal_rec.time_from)
                        end_time = cal_rec.relative_date(ref_time, 
                            cal_rec.get_weekday(cal_rec.weekday, name=False), cal_rec.time_to)
                        if start_time >= now1:
                            service = service_obj.create({
                                'start_time': start_time, 'end_time': end_time,
                                'user_id': rule.user_id.id, 'work_type': 'recurrent',
                                'rule_calendar_id': cal_rec.id,'partner_id': rule.partner_id.id,
                            })
                            for empl in cal_rec.employee_ids:
                                service_work_obj.create({
                                    'start_time': start_time, 'end_time': end_time,
                                    'employee_id': empl.id, 'work_type': 'recurrent',
                                    'address_archive_id': current_address.id,
                                    'partner_id': rule.partner_id.id, 'note': rule.partner_id.comment, 
                                    'attention': rule.partner_id.attention, 'service_id': service.id,
                                    'ign_rule_chk': True, #ign_rule_chk lets prevent istelf constraining.                                
                                })                              
            # Set next generate time
            self.set_next_gen_time()
            if self.init:
                self.init = False

        else:
            raise Warning(_("Inactive Recurrent Calendar can\'t be generated!"))

    @api.cr_uid
    def _auto_generate_recurrent(self, cr, uid, context=None):
        """
        Only used for Cron Job. Calls generate_recurrent()
        if conditions are satisfied.
        """
        recurrent_ids = self.search(cr, uid, [('active', '=', True)], context=context)
        if recurrent_ids:
            recurrent = self.browse(cr, uid, recurrent_ids, context=context)[0]
            #if not recurrent.next_gen_time or datetime.today() >= datetime.strptime(recurrent.next_gen_time, "%Y-%m-%d %H:%M:%S"):
            self.generate_recurrent(cr, uid, recurrent.id, context=context) 


    @api.one
    @api.constrains('weeks')
    def _check_weeks(self):
        if self.init_weeks < 0:
            raise Warning(_('Init Weeks can\'t be negative!'))
        if self.weeks < 1:
            raise Warning(_('Weeks can\'t be lower than 1!'))

    @api.one
    @api.constrains('active')
    def _check_active(self):
        if self.active:
            recurrent_recs = self.search([('id', '!=', self.id), ('active', '=', True)])
            if recurrent_recs:
                raise Warning(_("Only one Recurrent Calendar can be active at a Time!"))

    @api.one
    @api.constrains('rule_ids')
    def _check_rules(self):
        if not self.rule_ids:
            raise Warning(_("You should enter at least one Rule!"))


class calendar_service_recurrent_rule(models.Model):
    _name = 'calendar.service.recurrent.rule'
    _description = 'Recurrent Calendar Services Rules'
    user_id = fields.Many2one('res.users', 'Salesman')
    name = fields.Char('Rule Name')
    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], required=True)
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

    @api.one
    @api.constrains('partner_id')
    def _check_partner(self):
        rules = self.search([('id', '!=', self.id), ('recurrent_id', '=', self.recurrent_id.id)])
        for rule in rules:
            if rule.partner_id.id == self.partner_id.id:
                raise Warning(_('Partner per Rule must be Unique!'))

    @api.one
    @api.constrains('calendar_ids')
    def _check_calendar_ids(self):
        if not self.calendar_ids:
            raise Warning(_("You should enter at least one Calendar Item!"))

