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

from openerp.osv import fields, orm

def location_name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('code', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
       
        return self.name_get(cr, uid, ids, context=context)                 
    
class BaseLocalization(orm.Model):
    _name = 'base.localization'
    _description = 'Base class for localization classes'
    _columns = {
        'name': fields.char('Name', size=256, required=True),

    }
    _order = 'name'
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
    
class City(orm.Model):
    _name = 'res.country.state.city'
    _description = 'City'
    _inherit = 'base.localization'
    _columns = {
        'code': fields.char('Code', size=64, help="The official code for the city"),
        'state_id': fields.many2one('res.country.state', 'State', required=True),
    }
    
    def create(self, cursor, user, vals, context=None):
        #Make code value with capital letters
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(City, self).create(cursor, user, vals,
                context=context)

    def write(self, cursor, user, ids, vals, context=None):
        if 'code' in vals and vals['code'] != False:
            vals['code'] = vals['code'].upper()
        return super(City, self).write(cursor, user, ids, vals,
                context=context)
    
    name_search = location_name_search   
    

