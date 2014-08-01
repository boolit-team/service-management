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
from openerp.api import multi, one
WEEK_DAYS = [
    ('saturday', 'Saturday'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
]
class crm_lead_cleaning_calendar(models.Model):
    _name = 'crm.lead.cleaning_calendar'
    _description = 'Lead/Opp. Cleaning Calendar'
    #fields
    cleaning_day = fields.Selection(WEEK_DAYS, 'Week Day', required=True)
    clean_time_from = fields.Float('From', required=True)
    clean_time_to = fields.Float('To', required=True)
    lead_id = fields.Many2one('crm.lead', 'Lead/Opportunity')    


class crm_lead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'
    #fields
    product_id = fields.Many2one('product.product', 'Type of Service', domain=[('type', '=', 'service')])
    cleaning_calendar_ids = fields.One2many('crm.lead.cleaning_calendar', 'lead_id', 'Cleaning Time')
    desirable_duration = fields.Float('Cleaning Time', help="Desirable Cleanng Time")
    eyre = fields.Char('Eyre')
    apartment_complex = fields.Char('Apart. Complex')
    house_name = fields.Char('House Name')
    address_description = fields.Char('Address Description')
    nationality_id = fields.Many2one('res.country', 'Nationality')        