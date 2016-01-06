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
# from openerp.osv import orm, fields
from openerp import api, fields, models


class BetterZip(models.Model):
    _inherit = 'res.better.zip'

    city_id = fields.Many2one('res.country.state.city', 'City')
    street_id = fields.Many2one('res.country.state.city.street', 'Street')
    display_name = fields.Char(compute='_compute_display_name', store=False)
    city = fields.Char('City', required=False, deprecated=True)
    code = fields.Char('City Code', related='city_id.code', size=64, help="The official code for the city")
    house_no = fields.Char('House No.', size=32)
    apartment_no = fields.Char('Apartment No.', size=32)

    @api.multi
    @api.depends(
        'name',
        'street_id',
        'city_id',
        'state_id',
        'country_id',
    )
    def name_get(self):
        res = []
        for bzip in self:
            name = []
            if bzip.name:
                name.append(bzip.name)
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

    @api.onchange('city_id')
    def onchange_city_id(self):
        if self.city_id:
            self.state_id = self.city_id.state_id.id if self.city_id.state_id else False
            self.code = self.city_id.code

    @api.onchange('street_id')
    def onchange_street_id(self):

        if self.street_id:
            self.city_id = self.street_id.city_id.id if self.street_id.city_id else False
            self.code = self.street_id.city_id.code

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=5):
        if args is None:
            args = []
        ids = []
        if name:
            ids = self.search([('name', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search([('city_id.name', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search([('street_id.name', operator, name)] + args, limit=limit)
        return ids.name_get()
