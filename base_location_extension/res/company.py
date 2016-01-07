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
from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    better_zip_id = fields.Many2one('res.better.zip', 'Location', select=1,
                                    help=('Use the city name, street or the zip code'
                                          ' to search the location'))

    @api.onchange('better_zip_id')
    def onchange_zip_id(self):
        """Cascade address info into fields when the address completion is filled"""
        self.ensure_one()
        if self.better_zip_id:
            self.zip = self.better_zip_id.name
            self.country_id = self.better_zip_id.country_id
            self.street = self.better_zip_id.street_id.name if self.better_zip_id.street_id else False
            self.city = self.better_zip_id.city_id.name if self.better_zip_id.city_id else False
            self.state_id = self.better_zip_id.state_id if self.better_zip_id.state_id else False
