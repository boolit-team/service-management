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

# Import logger
import logging
# Get the logger
_logger = logging.getLogger(__name__)


class BetterZip(models.Model):
    _inherit = 'res.better.zip'

    city_id = fields.Many2one('res.country.state.city', 'City')
    street_id = fields.Many2one('res.country.state.city.street', 'Street')
    city = fields.Char('City', required=False, deprecated=True)
    code = fields.Char('City Code', related='city_id.code', size=64, help="The official code for the city")
    house_no = fields.Char('House No.', size=32)
    apartment_no = fields.Char('Appartment No.', size=32)

    # _order = 'name asc'
    # def name_get(self, cursor, uid, ids, context=None):
    #     res = []
    #     for bzip in self.browse(cursor, uid, ids):
    #         name = [bzip.name]
    #         # Updating with street and city tables
    #         if bzip.street_id:
    #             name.append(bzip.street_id.name)
    #         if bzip.city_id:
    #             name.append(bzip.city_id.name)
    #         if bzip.state_id:
    #             name.append(bzip.state_id.name)
    #         if bzip.country_id:
    #             name.append(bzip.country_id.name)
    #         res.append((bzip.id, ", ".join(name)))
    #     return res

    # @api.one
    # @api.depends(
    #     'name',
    #     'street_id',
    #     'city_id',
    #     'state_id',
    #     'country_id',
    # )
    # def _get_display_name(self):
    #     if self.name:
    #         name = [self.name, self.city_id]
    #     else:
    #         name = [self.city_id]
    #     if self.street_id:
    #         name.append(self.city_id)
    #     if self.city_id:
    #         name.append(self.city_id)
    #     if self.state_id:
    #         name.append(self.state_id)
    #     if self.country_id:
    #         name.append(self.country_id)
    #     self.display_name = ", ".join(name)

    @api.onchange('city_id')
    # def onchange_city_id(self, cr, uid, ids, city_id=False, context=None):
    def onchange_city_id(self):
        # _logger.warning(self)
        if self.city_id:
            # _logger.critical(str(self.city_id))
            # _logger.critical(str(self.city_id.id))
            # _logger.critical(str(self.city_id.name))
            # self.city = self.env['res.country.state.city'].browse(self.city_id.id)
            # _logger.warning(str(self.city))
            # _logger.critical(str(self.city_id.state_id.id))
            # _logger.critical(str(self.city_id.state_id.name))

            self.state_id = self.city_id.state_id.id if self.city_id.state_id else False
            self.code = self.city_id.code
            # return {'value': {'state_id': self.city.state_id.id if self.city.state_id else False,
            #                   'code': self.city.code,
            #                   }
            #         }

    @api.onchange('street_id')
    # def onchange_street_id(self, cr, uid, ids, street_id=False, context=None):
    def onchange_street_id(self):

        if self.street_id:
            # _logger.critical("this is SPARTAAA!!!" + str(self.street_id))
            # self.street = self.env['res.country.state.city.street'].browse(self.street_id).id
            self.city_id = self.street_id.city_id.id if self.street_id.city_id else False
            self.code = self.street_id.city_id.code
            # return {'value': {'city_id': street.city_id.id if street.city_id else False,
            #                   'code': street.city_id.code,
            #                   }
            #         }

    # def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=5):
    #     if args is None:
    #         args = []
    #     if context is None:
    #         context = {}
    #     ids = []
    #     if name:
    #         ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit)
    #     if not ids:
    #         ids = self.search(cr, uid, [('city_id', operator, name)] + args, limit=limit)
    #     if not ids:
    #         ids = self.search(cr, uid, [('street_id', operator, name)] + args, limit=limit)
    #     return self.name_get(cr, uid, ids, context=context)
