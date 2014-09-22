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

class res_partner_address_archive(models.Model):
    _name = 'res.partner.address_archive'
    _description = 'Partner Addresses Archive'
    #fields
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State')
    city = fields.Char('City')
    name = fields.Char('Post Code', size=24)
    eyre = fields.Char('Eyre')
    apartment_complex = fields.Char('Apart. Complex')
    house_name = fields.Char('House Name')
    street = fields.Char('Street')
    street2 = fields.Char('Ent. Street')
    house_no = fields.Char('House No.', size=64)
    apartment_no = fields.Char('Apartment No.', size=64)
    current = fields.Boolean('Current')
    address_description = fields.Char('Address Description')
    partner_id = fields.Many2one('res.partner', 'Partner')

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
            if address.state_id:
                name.append(address.state_id.name)
            if address.country_id:
                name.append(address.country_id.name)
            res.append((address.id, ", ".join(name)))
        return res    

    @api.model
    def create(self, vals):
        if vals.get('partner_id') and vals.get('current'):
            addresses = self.search([('partner_id', '=', vals['partner_id'])])
            for address in addresses:
                if address.current:
                    address.write({'current': False})
        return super(res_partner_address_archive, self).create(vals)    

    @api.multi
    def write(self, vals):
        for rec in self:
            if self.partner_id and vals.get('current'):                
                archive_addresses = self.env['res.partner.address_archive'].search(
                    [('id', '!=', self.id), ('partner_id', '=', self.partner_id.id)])
                for other_address in archive_addresses:                  
                    if other_address.current:
                        other_address.write({'current': False})
        return super(res_partner_address_archive, self).write(vals)
    
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    #fields
    nationality_id = fields.Many2one('res.country', 'Nationality')
    attention = fields.Text('Attention')
    eyre = fields.Char('Eyre')
    apartment_complex = fields.Char('Apartment Complex')
    house_name = fields.Char('House Name')
    address_description = fields.Char('Description')
    address_archive_ids = fields.One2many('res.partner.address_archive', 'partner_id', 'Addresses Archive')

    #methods
    @api.one
    def init_archive(self):
        """
        Creates address to archive from address
        in res.partner
        """
        vals = {
            'country_id': self.country_id and self.country_id.id or False,
            'state_id': self.state_id and self.state_id.id or False,            
            'city': self.city or None, 
            'name': self.zip or None, 
            'eyre': self.eyre or None,  
            'apartment_complex': self.apartment_complex or None, 
            'house_name': self.house_name or None, 
            'street': self.street or None, 
            'street2': self.street2 or None, 
            'house_no': self.house_no or None,
            'apartment_no': self.apartment_no or None,
            'address_description': self.address_description or None,         
        }        
        if not self.address_archive_ids:
            arch_addr_model = self.env['res.partner.address_archive']
            vals['current'] = True
            vals['partner_id'] = self.id
            arch_addr_model.create(vals)
        else:
            for address in self.address_archive_ids:
                if address.current:
                    address.write(vals)

    @api.one
    def update_address(self, context=None):
        """
        Updates res.partner address from current address
        from archive.
        """
        address = self.env['res.partner.address_archive'].search(
            [('partner_id', '=', self.id), ('current', '=', True)])
        if address:
            vals = {
                'country_id': address.country_id and address.country_id.id or False,
                'state_id': address.state_id and address.state_id.id or False,            
                'city': address.city or None, 
                'zip': address.name or None, 
                'eyre': address.eyre or None,  
                'apartment_complex': address.apartment_complex or None, 
                'house_name': address.house_name or None, 
                'street': address.street or None, 
                'street2': address.street2 or None, 
                'house_no': address.house_no or None,
                'apartment_no': address.apartment_no or None,
                'address_description': address.address_description or None,        
            }
            self.write(vals)