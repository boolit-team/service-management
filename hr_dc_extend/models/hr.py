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

class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    #fields
    address_lt_id = fields.Many2one('res.better.zip',string="Home Address in LT")
    phone_lt = fields.Char(string='Phone number in LT')
    address_uk_id = fields.Many2one('res.better.zip',string="Home Address in UK")
    id_copy_fname = fields.Char('ID Copy Fname', size=256, readonly=True, default="id_copy.pdf")
    id_copy = fields.Binary('ID Copy', filters="*.pdf", filename=id_copy_fname)
    sort_code = fields.Char('Sort Code', size=8)
    nin = fields.Char('NIN', size=9)
    driving_licence = fields.Binary('Driving Licence', filters="*.pdf")
    relatives = fields.Char('Relatives')
    relative_name = fields.Char('Relative Name')
    contact_info = fields.Text('Contact Info')

    '''
    @api.onchange('bank_account_id')
    def onchange_bank_account_id(self):
        if self.bank_account_id:
            self.sort_code = self.bank_account_id.sort_code
    '''
