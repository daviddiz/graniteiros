# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields, osv
from tools.translate import _

class iso_traza_libro_report(osv.osv_memory):
    _name = 'iso.traza.libro.report'
    _description = 'Imprimir Libro de Registro'
    _columns = {
        'obra_id': fields.many2one('stock.location', 'Explotacion - Obra', domain = [('obra','=',True)], required=True),
        'date_from': fields.date("Fecha Inicial"),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['obra_id',  'date_from'])[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'libro',
            'datas': data,
            }

iso_traza_libro_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: