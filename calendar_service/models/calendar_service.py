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

class calendar_service_desired_time(models.Model):
    _name = 'calendar.service.desired.time'
    _description = 'Service Desired Time'

    day = fields.Selection(WEEK_DAYS, 'Week Day', required=True)
    time_from = fields.Float('From', required=True)
    time_to = fields.Float('To', required=True)
    service_id = fields.Many2one('calendar.service', 'Calendar Service')    

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
    work_type = fields.Selection(WORK_TYPE, 'Type')
    state = fields.Selection(STATE, 'State', readonly=True, default='open', track_visibility='onchange')
    ign_rule_chk = fields.Boolean('Ignore Rule Check')
    details = fields.Char('Details', compute='_compute_details')

    @api.one
    def close_state(self):
        self.state = 'done'

    @api.one
    def cancel_state(self):
        self.state = 'cancel'    

    @api.one
    @api.depends('description', 'attention')
    def _compute_details(self):
        """
        Checks if description and/or attention fields are filled,
        when in tree view
        """
        self.details = ''
        if self.description:
            self.details = 'Description'
        if self.attention:
            self.details = "%s%s" % ("Description + " if self.details else '', 'Attention')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
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
            if self.partner_id:
                for address in self.partner_id.address_archive_ids:
                    if address.current:
                        self.address_archive_id = address.id
                self.note = self.partner_id.comment
                self.attention = self.partner_id.attention            

    @api.model
    def _get_week_dur(self, employee_id, week_nmb=0, recurrent=False):
        """
        Returns planned duration in hours for chosen week
        """
        cal_serv_cal = self.env['calendar.service.calendar']
        duration = 0.0
        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=week_nmb)
        week_start = dt - timedelta(days=dt.weekday())
        week_end = week_start + timedelta(days=6)
        week_start = week_start.strftime("%Y-%m-%d %H:%M:%S")
        week_end = week_end.strftime("%Y-%m-%d %H:%M:%S")
        work_filter = [('employee_id', '=', employee_id), ('start_time', '>=', week_start), 
            ('end_time', '<=', week_end)]
        if recurrent:
            work_filter.append(('work_type', '=', 'recurrent'))
        works = self.search(work_filter)
        for work in works:
            start_time = cal_serv_cal.str_to_dt(work.start_time)
            end_time = cal_serv_cal.str_to_dt(work.end_time)
            hours = cal_serv_cal.get_duration(start_time, end_time)
            duration += hours
        return duration        

    @api.one
    @api.constrains('start_time', 'end_time', 'service_id')
    def _check_time(self):
        """
        Lets to set works time only in service time constraints
        """
        cal_serv_cal = self.env['calendar.service.calendar']
        start_time = cal_serv_cal.str_to_dt(self.start_time)
        end_time = cal_serv_cal.str_to_dt(self.end_time)
        serv_start_time = cal_serv_cal.str_to_dt(self.service_id.start_time)
        serv_end_time = cal_serv_cal.str_to_dt(self.service_id.end_time)
        if start_time < serv_start_time or end_time > serv_end_time:
            raise Warning(_("Work start/end time can't go out of service time constraints!")) 

    @api.one
    @api.constrains('start_time', 'end_time', 'employee_id', 'state', 'work_type')
    def _check_resource(self):
        """
        Does double resource checking to see if resource (employee)
        is already taken for specific time. First check is to see between
        already created records. Second check is to see if recurrent rule
        is set for that time, the record is being created for.
        """
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
            if recurrent and not recurrent.next_gen_time:
                raise Warning(_("You need to Initially generate Recurrent Calendar\n"
                    "before creating any services or works!"))
            next_gen_time = cal_serv_cal.set_tz(cal_serv_cal.str_to_dt(recurrent.next_gen_time))
            cal_recs = cal_serv_cal.search([('employee_ids', 'in', [self.employee_id.id]), 
                ('rule_id.recurrent_id', '=', recurrent.id), ('weekday', '=', weekday), 
                ('time_from', '<', time_to), ('time_to', '>', time_from)])
            for cal_rec in cal_recs:
                if cal_rec.second_week and start_time >= next_gen_time:
                    next_gen_time_m = next_gen_time - timedelta(days=next_gen_time.weekday())
                    start_time_m = start_time - timedelta(days=start_time.weekday())
                    week_diff = (start_time_m - next_gen_time_m).days / 7 #get difference in weeks
                    #check if week is reserved or not
                    if (week_diff % 2 == 0 and cal_rec.last_week_gen) or (week_diff % 2 != 0 and not cal_rec.last_week_gen):
                        continue
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
    work_ids = fields.One2many('calendar.service.work', 'service_id', 'Works')
    state = fields.Selection(STATE, 'State', readonly=True, default='open', track_visibility='onchange')
    user_id = fields.Many2one('res.users', 'Salesman')
    rule_calendar_id = fields.Many2one('calendar.service.calendar', 'Rule Calendar Item')
    product_id = fields.Many2one('product.product', 'Product Service', domain=[('type', '=', 'service')])
    order_id = fields.Many2one('sale.order', 'Sale Order')
    desired_time_ids = fields.One2many('calendar.service.desired.time', 'service_id', 'Service Time')
    canceled_until = fields.Date('Canceled Until')

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
        """
        When closing service, it also creates/updates Sale Order
        if product_id is set on service.
        """
        if self.work_type == 'wait':
            raise Warning(_("Service with Waiting type can't be closed!"))
        if self.product_id:
            cal_serv_cal = self.env['calendar.service.calendar']   
            # avoid forcing default_state values when creating sale orders
            order_obj = self.env['sale.order'].with_context({
                key: val
                for key, val in self.env.context.iteritems()
                if not (isinstance(key, basestring) and key == 'default_state')
            })
            line_obj = self.env['sale.order.line'].with_context({
                key: val
                for key, val in self.env.context.iteritems()
                if not (isinstance(key, basestring) and key == 'default_state')                
            })
            vals = {'partner_id': self.partner_id.id, 'date_order': self.end_time,
                'pricelist_id': self.partner_id.property_product_pricelist.id,
                'user_id': self.user_id.id, 'calendar_service_id': self.id,
            }
            qty = 0.0
            for work in self.work_ids:  
                start_time = cal_serv_cal.str_to_dt(work.start_time)
                end_time = cal_serv_cal.str_to_dt(work.end_time)
                qty += round(cal_serv_cal.get_duration(start_time, end_time), 3) #converting duration as qty in hours              
            line_vals = {'product_id': self.product_id.id, 'product_uom_qty': qty, 'state': 'draft',}                      
            if not self.order_id or (self.order_id and self.order_id.state == 'cancel'):
                order = order_obj.create(vals)
                self.order_id = order.id
                line_vals['order_id'] = order.id
                line_obj.create(line_vals)
            elif self.order_id.state == 'draft':
                order = self.order_id.write(vals)
                for line in self.order_id.order_line:
                    line.write(line_vals)
        self.state = 'done'
        for work in self.work_ids:
            work.state = 'done'

    @api.cr_uid
    def _auto_close_state(self, cr, uid, context=None):
        """
        Used only for cron job. Automatically checks and closes passed services
        that were still open and not in Waiting type.
        """
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_start = today_start.strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        service_ids = self.search(cr, uid, [('state', '=', 'open'), ('work_type', '!=', 'wait'),
            ('start_time', '>=', today_start), ('end_time', '<=', now)], context=context)
        for service in self.browse(cr, uid, service_ids, context=context):
            self.close_state(cr, uid, service.id, context=context)

    @api.one
    def cancel_state(self):
        if not self.state == 'open':
            raise Warning(_("You can't cancel Service that is not in 'open' state!"))
        self.state = 'cancel'
        for work in self.work_ids:
            work.state = 'cancel'

    @api.one
    def open_state(self):
        if self.order_id and self.order_id.state not in ('draft', 'cancel'):
            raise Warning(_("Can't open Service, because \nSale Order is not in Draft or Cancelled state!"))
        self.state = 'open'
        for work in self.work_ids:
            work.state = 'open'
        
    @api.one
    @api.constrains('work_ids')
    def _check_works(self):
        if not self.work_ids:
            raise Warning(_("Works can't be Empty!"))

    @api.one
    @api.constrains('start_time', 'end_time')
    def _check_time(self):
        start_time = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")
        if end_time < start_time:
            raise Warning(_("End Time can't be lower than Start Time!"))
        if end_time == start_time:
            raise Warning(_("End Time and Start Time can't be the same!"))

class calendar_service_calendar(models.Model):
    _name = 'calendar.service.calendar'
    _description = 'Calendar Service Working Time'

    name = fields.Char('Calendar', size=64)
    weekday = fields.Selection(WEEK_DAYS, 'Week Day', required=True)
    time_from = fields.Float('From', required=True)
    time_to = fields.Float('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_calendar_rel', 'calendar_id', 'employee_id', 'Employees')
    rule_id = fields.Many2one('calendar.service.recurrent.rule', 'Rule', ondelete='cascade')
    second_week = fields.Boolean('Every Second Week')
    last_week_gen = fields.Boolean('Last Week Generated')
    product_id = fields.Many2one('product.product', 'Product Service', domain=[('type', '=', 'service')])

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
    def _resolve_week_skip(self, weeks, init_skip):
        """
        Looks first or second week should be skipped
        """
        if weeks % 2 == 0:
            return init_skip
        else:
            return not init_skip

    @api.model
    def relative_date(self, reference, weekday, timevalue):
        """
        Constructs datetime from weekday, time in
        float format and reference datetime. Reference
        datetime means datetime for specific week. It
        can be any datetime in wanted week interval.
        Also sets utc timezone for datetime for 
        comparing purposes.
        """
        hour, minute = divmod(timevalue, 1)
        minute *= 60
        days = reference.weekday() - weekday
        dt = (reference - timedelta(days=days)).replace(
            hour=int(hour), minute=int(minute), second=0, microsecond=0)
        dt = self.set_utc(dt)
        return dt

    @api.model
    def get_weekday(self, key, name=True):
        """
        Returns weekday name from weekday keyword
        or its value.
        """
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
    def str_to_dt(self, string):
        """
        Converts String to Datetime
        """        
        dt = datetime.strptime(string, self.get_dt_fmt())
        return dt

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

    @api.model
    def get_duration(self, start_dt, end_dt):
        """
        Returns duration in hours between two dates. 
        """
        if end_dt < start_dt:
            raise Warning(_("end_dt can't be lower than start_dt!"))
        diff = end_dt - start_dt
        dur = diff.total_seconds() / 3600
        return dur  


    @api.one
    @api.constrains('time_to', 'time_from')
    def _check_calendar(self):
        if self.time_to < self.time_from:
            raise Warning(_("End time can\'t be lower than Start!"))

    @api.one
    @api.constrains('weekday', 'time_from', 'time_to', 'employee_ids', 'second_week', 
        'last_week_gen')
    def _check_resource(self):
        for empl in self.employee_ids:
            items = self.search(
                [('id', '!=', self.id), ('employee_ids', 'in', [empl.id]), 
                ('weekday', '=', self.weekday), ('time_from', '<', self.time_to), 
                ('time_to', '>', self.time_from)])
            for item in items:
                if self.second_week and item.second_week and (self.last_week_gen != item.last_week_gen) or \
                    self.rule_id.recurrent_id.ign_second_week:
                    continue               
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
    ign_second_week = fields.Boolean('Ignore Second Week Check') #used to second week constrain when generating calendar

    @api.model
    def create(self, vals):
        recurrents = self.search([])
        if recurrents:
            raise Warning(_("Only one Recurrent Calendar Configuration\ncan be active at a time!"))
        return super(calendar_service_recurrent, self).create(vals)

    @api.model
    def _get_week_range(self):
        if self.init:
            return self.init_weeks + 1 #to run at least once           
        else:
            return self.weeks

    @api.one
    def set_next_gen_time(self):
        """
        Sets datetime for next recurrent calendar 
        generation time 'constraint'. If it is initial generation,
        then datetime will be next weeks monday from last generated
        week. If non initial, then it extends the number of weeks
        it was specified to extend generation (usually 1 week)
        """
        cal_serv_cal = self.env['calendar.service.calendar']
        if self.init:
            weeks = self.init_weeks + 1 # we need to jump to the next week after the last one generated (+1).
            next_gen_time = datetime.today() + timedelta(weeks=weeks)
            next_gen_time = next_gen_time - timedelta(days=next_gen_time.weekday()) #Set it to monday
            next_gen_time = next_gen_time.replace(hour=0, minute=0, second=0, microsecond=0)
            next_gen_time = cal_serv_cal.set_utc(next_gen_time) #set time back to UTC
        else:
            next_gen_time = cal_serv_cal.str_to_dt(self.next_gen_time) + timedelta(weeks=self.weeks, days=1) #+1 day to be sure to jump to another week
            next_gen_time = next_gen_time - timedelta(days=next_gen_time.weekday())
            next_gen_time = cal_serv_cal.set_utc(next_gen_time.replace(hour=0, minute=0, second=0, microsecond=0))
        self.next_gen_time = next_gen_time     

    @api.one
    def create_service(self,service_obj, service_work_obj, start_time, end_time, 
        cal_rec, rule, current_address, change_time=None):
        """
        Helper method for creating services and its works 
        for generation methods.
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
                'address_archive_id': current_address.id,
                'partner_id': rule.partner_id.id, 'note': rule.partner_id.comment, 
                'attention': rule.partner_id.attention, 'service_id': service.id,
                'ign_rule_chk': True, #ign_rule_chk lets prevent istelf constraining.                                
            })          

    @api.one
    def generate_recurrent(self):
        """
        Generates recurrent services from specified 
        recurrent calendar rules. Can generate weekly,
        or every second week repeating calendar services
        with their works. 
        """
        if self.active:
            cal_serv_cal = self.env['calendar.service.calendar']
            now1 = cal_serv_cal.set_utc(datetime.today() + timedelta(hours=1), check_tz=False)
            service_obj = self.env['calendar.service']
            service_work_obj = self.env['calendar.service.work']
            self.ign_second_week = True #to let interchanging last_week_gen value
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
                            if cal_rec.second_week: #checking if need to generate every or second week
                                if not cal_rec.last_week_gen:
                                    self.create_service(service_obj, service_work_obj, start_time, end_time, 
                                        cal_rec, rule, current_address)
                                cal_rec.last_week_gen = not cal_rec.last_week_gen    
                            else:
                                self.create_service(service_obj, service_work_obj, start_time, end_time, 
                                    cal_rec, rule, current_address)                                
            # Set next generate time
            self.set_next_gen_time()
            if self.init:
                self.init = False
            self.ign_second_week = False #Stop ignoring second_week

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
    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True)], required=True)
    calendar_ids = fields.One2many('calendar.service.calendar', 'rule_id', 'Service Time')

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

    '''
    @api.one
    @api.constrains('calendar_ids')
    def _check_calendar_ids(self):
        if not self.calendar_ids:
            raise Warning(_("You should enter at least one Calendar Item!"))
    '''

