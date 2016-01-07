# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp import api, fields, models


class BaseLocalization(models.Model):
    _name = 'base.localization'
    _description = 'Base class for localization classes'
    _order = 'name'

    name = fields.Char(size=256, required=True)

    """
    def create(self, cursor, user, vals, context=None):
        if vals.get('name'):
            vals['name'] = vals['name'].capitalize()
        return super(BaseLocalization, self).create(cursor, user, vals,
                context=context)

    def write(self, cursor, user, ids, vals, context=None):
        if 'name' in vals and vals['name'] != False:
            vals['name'] = vals['name'].capitalize()
        return super(BaseLocalization, self).write(cursor, user, ids, vals,
                context=context)
    """


class City(models.Model):
    _name = 'res.country.state.city'
    _description = 'City'
    _inherit = 'base.localization'

    code = fields.Char(size=64, help="The official code for the city")
    state_id = fields.Many2one('res.country.state', 'State', required=True)

    @api.model
    def create(self, vals):
        # Make code value with capital letters
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(City, self).create(vals)

    @api.model
    def write(self, vals):
        if 'code' in vals and vals['code'] != False:
            vals['code'] = vals['code'].upper()
        return super(City, self).write(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Search for code and name, instead of just name, when entering city in"""
        if args is None:
            args = []
        ids = []
        if name:
            ids = self.search([('code', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search([('name', operator, name)] + args, limit=limit)

        return ids.name_get()
