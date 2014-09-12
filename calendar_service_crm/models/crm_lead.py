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
from openerp import tools

class calendar_service_desired_time(models.Model):
    _inherit = 'calendar.service.desired.time'

    lead_id = fields.Many2one('crm.lead', 'Lead/Opportunity') 

class crm_lead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    product_id = fields.Many2one('product.product', 'Type of Service', domain=[('type', '=', 'service')])    
    desired_time_ids = fields.One2many('calendar.service.desired.time', 'lead_id', 'Service Time')
    eyre = fields.Char('Eyre')
    apartment_complex = fields.Char('Apart. Complex')
    house_name = fields.Char('House Name')
    address_description = fields.Char('Address Description')
    nationality_id = fields.Many2one('res.country', 'Nationality') 
    
    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        """
        Extends original method to also add:
          house_no, apartment_no, eyre, house_name, apartment_complex, address_description, nationality_id 
          fields data
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
            'eyre': lead.eyre,
            'house_name': lead.house_name,
            'apartment_complex': lead.apartment_complex,
            'address_description': lead.address_description,
            'nationality_id': not is_company and lead.nationality_id and lead.nationality_id.id or False
        }

        partner = partner.create(cr, uid, vals, context=context)
        return partner    