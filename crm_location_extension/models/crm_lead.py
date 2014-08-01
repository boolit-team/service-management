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
from openerp.api import onchange, one
from openerp import tools

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

    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        """
        Extends original method to also add house_no and apartment_no fields data
        """
        partner = self.pool.get('res.partner')
        vals = {'name': name,
            'user_id': lead.user_id.id,
            'comment': lead.description,
            'section_id': lead.section_id.id or False,
            'parent_id': parent_id,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
            'fax': lead.fax,
            'title': lead.title and lead.title.id or False,
            'function': lead.function,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id and lead.country_id.id or False,
            'state_id': lead.state_id and lead.state_id.id or False,
            'is_company': is_company,
            'type': 'contact',
            'house_no': lead.house_no,
            'apartment_no': lead.apartment_no,
        }
        partner = partner.create(cr, uid, vals, context=context)
        return partner    
           