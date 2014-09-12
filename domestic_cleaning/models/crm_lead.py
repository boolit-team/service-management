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

class crm_lead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'
    #fields
    nmb_bathrooms = fields.Integer('Number of Bathrooms')
    nmb_bedrooms = fields.Integer('Number of Bedrooms')
    nmb_other_rooms = fields.Integer('Number of Other Rooms')
    nmb_residents = fields.Integer('Number of Residents')
    pets_info = fields.Text('Pets')
    cleaning_note = fields.Text('Notes')    
    desirable_duration = fields.Float('Cleaning Time', help="Desirable Cleaning Time")
 
   