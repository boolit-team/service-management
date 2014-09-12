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

TERMINATION_REASON = [
    ('moved', 'Moved'), ('quality', 'Cleaning Quality'),
    ('danger', 'Dangerous Situations'), ('damage', 'Damage to Property'),
    ('communication', 'Communication Problems with Housemaids'),
    ('cheating', 'Housemaid Cheating'),
    ('schedule', 'Fail to Comply with work Schedule'),
    ('internal', 'Company\'s Internal Issues'),
    ('personal', 'Personal Reasons'),
    ('suspicious', 'Customer\'s Suspiciousness'),
    ('other', 'Other Reasons') 
]

MOVED_REASON = [
    ('not_serving', 'Not Serving Area'),
    ('no_address', 'No New Address Left'),
    ('else', 'Else')
]

DANGER_REASON = [
    ('doors', 'Unlocked Doors'),
    ('windows', 'Unlocked Window'),
    ('key', 'Lost Home Key'),
    ('gas', 'Left Open Gas Tap'),
    ('water', 'Left Open Water Tap'),
    ('items', 'Items Disappeared'),
    ('else', 'Else')
]

COMMUNICATION_REASON = [
    ('english', 'Don\'t Talk in English '),
    ('impolite', 'Impolite Behavior'),
    ('else', 'Else')
]

SCHEDULE_REASON = [
    ('late', 'Regulary Late for Work'),
    ('early', 'Comes too Early'),
    ('else', 'Else')
]

INTERNAL_REASON = [
    ('employee_change', 'Frequent Employee Change'),
    ('expensive', 'Too Expensive'),
    ('conflict', 'Conflict With a Manager'),
    ('else', 'Else')
]

PERSONAL_REASON = [
    ('lost_job', 'Lost Job'),
    ('cleans_himself', 'Decided to Clean by Himself'),
    ('no_comments', 'No Comments'),
    ('else', 'Else')
]

SUSPICIOUS_REASON = [
    ('nationality', 'Other Nationality'),
    ('untidy', 'Untidy'),
    ('test', 'It Was Test Cleaning'),
    ('else', 'Else')
]

class account_analytic_termination(models.Model):
    _name = 'account.analytic.cleaning.termination'
    _description = 'Contract Cleaning Termination Reasons'

    term_reason = fields.Selection(TERMINATION_REASON, 'Reason')
    moved = fields.Selection(MOVED_REASON, 'Moved')
    specify_moved = fields.Char('Specify')
    specify_quality = fields.Char('Specify')
    danger = fields.Selection(DANGER_REASON, 'Dangerous Situation')
    specify_danger = fields.Char('Else')
    specify_damage = fields.Char('Specify')
    communication = fields.Selection(COMMUNICATION_REASON, 'Communication Problem')
    specify_comm = fields.Char('Specify')
    specify_cheating = fields.Char('Specify')
    schedule = fields.Selection(SCHEDULE_REASON, 'Work Schedule')
    specify_schedule = fields.Char('Specify')
    internal = fields.Selection(INTERNAL_REASON, 'Internal Issue')
    specify_internal = fields.Char('Specify')
    personal = fields.Selection(PERSONAL_REASON, 'Personal Reason')
    specify_personal = fields.Char('Specify')
    suspicious = fields.Selection(SUSPICIOUS_REASON, 'Suspicious')
    specify_suspicious = fields.Char('Specify')
    specify_other = fields.Char('Specify')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic')

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    termination_ids = fields.One2many('account.analytic.cleaning.termination', 'analytic_id', 'Termination Reasons')





