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
from openerp.api import onchange

class crm_lead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'
    #fields
    zip_id = fields.Many2one('res.better.zip', 'Address Completion')
    house_no = fields.Char('House No.', size=64, help="House No.")
    apartment_no = fields.Char('Apartment No.', size=64, help="Apartment No.")

    #methods
    @onchange('zip_id')
    def onchange_zip_id(self):
        if self.zip_id:
            self.street = self.zip_id.street_id and self.zip_id.street_id.name or False
            self.city = self.zip_id.city or False
            self.country_id = self.zip_id.country_id and self.zip_id.country_id.id or False
            self.state_id = self.zip_id.state_id and self.zip_id.state_id.id or False
            self.house_no = self.zip_id.house_no or False
            self.apartment_no = self.zip_id.apartment_no or False
           