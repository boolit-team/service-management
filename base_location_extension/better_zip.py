# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi. Copyright Camptocamp SA
#    Contributor: Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>
#                 Ignacio Ibeas <ignacio@acysos.com>
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
#from openerp.osv import orm, fields
from openerp import fields, models

class BetterZip(models.Model):

    _inherit = 'res.better.zip'

    city_id = fields.Many2one('res.country.state.city', 'City')
    street_id = fields.Many2one('res.country.state.city.street', 'Street')
    city = fields.Char('City', required=False, deprecated=True)
    code = fields.Char('City Code', related='city_id.code', size=64, help="The official code for the city")
    house_no = fields.Char('House No.', size=32)
    apartment_no = fields.Char('Appartment No.', size=32)
       
    #_order = 'name asc'
    def name_get(self, cursor, uid, ids, context=None):
        res = []
        for bzip in self.browse(cursor, uid, ids):
            name = [bzip.name]
            #Updating with street and city tables
            if bzip.street_id:
                name.append(bzip.street_id.name)
            if bzip.city_id:
                name.append(bzip.city_id.name)
            if bzip.state_id:
                name.append(bzip.state_id.name)
            if bzip.country_id:
                name.append(bzip.country_id.name)
            res.append((bzip.id, ", ".join(name)))
        return res

    def onchange_city_id(self, cr, uid, ids, city_id=False, context=None):

        if city_id:
            city = self.pool['res.country.state.city'].browse(cr, uid, city_id, context=context)
            return {'value': {'state_id': city.state_id.id if city.state_id else False,
                          'code': city.code,
                          }
                 }
        else:
            return {}

    def onchange_street_id(self, cr, uid, ids, street_id=False, context=None):

        if street_id:
            street = self.pool['res.country.state.city.street'].browse(cr, uid, street_id, context=context)
            return {'value': {'city_id': street.city_id.id if street.city_id else False,
                          'code': street.city_id.code,
                          }
                 }
        else:
            return {}

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=5):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('city_id', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('street_id', operator, name)] + args, limit=limit)       
        return self.name_get(cr, uid, ids, context=context)                                          
            
       
