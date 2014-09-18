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
from analytic import DANGER_REASON, COMMUNICATION_REASON, SCHEDULE_REASON
CLAIM = [('quality', 'Cleaning Quality'), ('danger', 'Danger'), ('damage', 'Damage to Property'),
    ('commun', 'Communication Problems with HM'), ('cheating', 'Housemaid Cheating'),
    ('schedule', 'Failed to comply with Schedule'), ('resp', 'Lack of Responsibility'),
    ('colleaugue', 'Communication with Colleague'), ('head', 'Commuication with the Head'),
    ('assessment', 'Overall Negative Assessment')
]
RESP_CLAIM = [('sick', 'Frequently Sick'), ('late', 'Late for Work'),
    ('alcohol', 'Alcohol Abuse'), ('smoke', 'Smoke near the Customer\'s Home'),
    ('untidy_car', 'Using Untidy Car'), ('else', 'Else')
]
COLLEAGUE_CLAIM = [('conflict', 'Conflicting'), ('not_equal', 'Don\'t share work Equally'),
    ('else', 'Else')
]
HEAD_CLAIM = [('instructions', 'Failse to Comply with Instructions'), ('impolite', 'Impolite'),
('phone', 'Can\'t be Reached by Phone'), ('else', 'Else')
]

ASSESSMENT_CLAIM = [('slow', 'Too Slow'), ('liar', 'Liar'), ('lazy', 'Lazy'),
    ('steal', 'Tried to steal Customer'), ('else', 'Else')
]
class crm_claim(models.Model):
    _inherit = 'crm.claim'

    employee_id = fields.Many2one('hr.employee', 'Blamed Employee')
    cleaning_claim = fields.Selection(CLAIM, 'Cleaning Claim')
    quality_specify = fields.Char('Specify')
    danger_claim = fields.Selection(DANGER_REASON, 'Dangerous Situations')
    danger_specify = fields.Char('Specify')
    commun_claim = fields.Selection(COMMUNICATION_REASON, 'Communiation Problems with HM') 
    commun_specify = fields.Char('Specify')
    cheating_specify = fields.Char('Specify')
    schedule_claim = fields.Selection(SCHEDULE_REASON, 'Fail to comply with Schedule')
    shcedule_specify = fields.Char('Specify')
    resp_claim = fields.Selection(RESP_CLAIM, 'Lack of Responsibility')
    resp_specify = fields.Char('Specify')
    colleaugue_claim = fields.Selection(COLLEAGUE_CLAIM, 'Commun. With Colleague')
    colleaugue_specify = fields.Char('Specify')
    head_claim = fields.Selection(HEAD_CLAIM, 'Commun. with the Head')
    head_specify = fields.Char('Specify')
    assessment_claim = fields.Selection(ASSESSMENT_CLAIM, 'Overall Negative Assessment')
    assessment_specify = fields.Char('Specify')
    damage_amount = fields.Float('Damage amount, %')

