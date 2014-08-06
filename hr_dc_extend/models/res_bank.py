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

class res_bank(models.Model):
    _inherit = 'res.bank'

    sort_code = fields.Char('Sort Code', size=8)

class res_bank_partner(models.Model):
    _inherit = 'res.partner.bank'

    sort_code = fields.Char('Sort Code', size=8)

    def onchange_bank_id(self, cr, uid, ids, bank_id, context=None):
        vals = super(res_bank_partner, self).onchange_bank_id(cr, uid, ids, bank_id, context=None)
        bank = self.pool.get('res.bank').browse(cr, uid, bank_id, context=context)
        vals['value']['sort_code'] = bank.sort_code
        return vals  
