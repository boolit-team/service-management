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

class recurrent_rule_change_time(models.TransientModel):
    _inherit = 'recurrent.rule.change.time'

    account_id = fields.Many2one('account.analytic.account', 'Timesheet Account', domain=[('type', '=', 'normal'), 
        ('use_timesheets', '=', True)]) 

class recurrent_rule_change(models.TransientModel):
    _inherit = 'recurrent.rule.change'

    @api.model
    def _add_rule_item(self, change_time):
        cal_rec = super(recurrent_rule_change, self)._add_rule_item(change_time)
        if self.change_type == 'permanent' and cal_rec:
            cal_rec.account_id = change_time.account_id.id
