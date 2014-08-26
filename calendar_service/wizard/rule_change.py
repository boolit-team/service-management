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
    change_day = fields.Selection(WEEK_DAYS, 'Week Day')
    change_time_from = fields.Float('Change From')
    change_time_to = fields.Float('Change To')
    change_id = fields.Many2one('recurrent.rule.change', 'Rule Change')    

class recurrent_rule_change(models.TransientModel):
    _name = 'recurrent.rule.change'
    _description = 'Recurrent Rule Change Wizard'

    recurrent_id = fields.Many2one('calendar.service.recurrent', 'Recurrent Calendar')
    rule_id = fields.Many2one('calendar.service.recurrent.rule', 'Rule')
    change_time_ids = fields.One2many('recurrent.rule.change.time', 'change_id', 'Change Times')

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