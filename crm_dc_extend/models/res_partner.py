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

class res_partner_address_archive(models.Model):
    _name = 'res.partner.address_archive'
    _description = 'Partner Addresses Archive'
    #fields
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State')
    city = fields.Char('City')
    name = fields.Char('Post Code', size=24)
    street = fields.Char('Street')
    current = fields.Boolean('Current')
    partner_id = fields.Many2one('res.partner', 'Partner')

    _sql_constraints = [('unique_current', 'unique(current)', 'Only One Address can be Current!')]

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    #fields
    nationality_id = fields.Many2one('res.country', 'Nationality')
    attention = fields.Text('Attention')
    address_archive_ids = fields.One2many('res.partner.address_archive', 'partner_id', 'Addresses Archive')