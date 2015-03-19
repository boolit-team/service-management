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

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    #HS Info
    have_key = fields.Boolean('We Have It')
    key_numb = fields.Char('Key ID')
    key_left = fields.Boolean('Is Left')
    where_key = fields.Char('Where?')
    house_alarm_on = fields.Char('House Alarm On')
    house_alarm_off = fields.Char('House Alarm Off')
    gate_alarm_on = fields.Char('Gate Alarm On')
    gate_alarm_off = fields.Char('Gate Alarm Off')


class res_partner_address_archive(models.Model):
    _inherit ='res.partner.address_archive'

    @api.multi
    def name_get(self):
        res = []
        for address in self:
            name = []
            if address.name:
                name.append(address.name)
            if address.street:
                name.append(address.street)
            if address.city:
                name.append(address.city)
            if address.house_no:
                name.append(address.house_no)
            if address.house_name:
                name.append(address.house_name)
            res.append((address.id, ", ".join(name)))
        return res