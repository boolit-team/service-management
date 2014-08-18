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
from openerp.exceptions import Warning
from openerp.tools.translate import _
class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    track_calendar = fields.Boolean('Track in Calendar')

    @api.one
    @api.constrains('track_calendar', 'employee_id')
    def _unique_tracking(self):
        if self.track_calendar:
            contracts = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('track_calendar', '=', True), ('id', '!=', self.id)])
            if contracts:
                raise Warning(_('Contract per employee must be Unique for calendar Tracking'))