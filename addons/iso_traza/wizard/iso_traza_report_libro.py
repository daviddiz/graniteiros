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
        'date_to': fields.date("Fecha Final"),
        'delegacion_id': fields.many2one('iso.traza.delegacion', "Delegación"),
        'subdelegacion_id': fields.many2one('iso.traza.subdelegacion', "Subdelegación"),
        'area_id': fields.many2one('iso.traza.area', "Área Funcional"),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', help='Responsable de la explotación'),
    }
    _defaults = {
        'obra_id': lambda self, cr, uid, c: self.pool.get('stock.location').search(cr, uid, [('obra', '=', True)])[0],
        'dir_facul_id': lambda self, cr, uid, c: self.pool.get('iso.traza.dirfacul').search(cr, uid, [])[0],
        'resp_explot_id': lambda self, cr, uid, c: self.pool.get('iso.traza.respexplot').search(cr, uid, [])[0],
        'delegacion_id': lambda self, cr, uid, c: self.pool.get('iso.traza.delegacion').search(cr, uid, [])[0] if (self.pool.get('iso.traza.delegacion').search(cr, uid, [])) else None,
        'subdelegacion_id': lambda self, cr, uid, c: self.pool.get('iso.traza.subdelegacion').search(cr, uid, [])[0] if (self.pool.get('iso.traza.subdelegacion').search(cr, uid, [])) else None,
        'area_id': lambda self, cr, uid, c: self.pool.get('iso.traza.area').search(cr, uid, [])[0] if (self.pool.get('iso.traza.area').search(cr, uid, [])) else None,
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['obra_id',  'date_from', 'date_to', 'delegacion', 'subdelegacion', 'area', 'dir_facul_id', 'resp_explot_id'])[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'libro',
            'datas': data,
            }

iso_traza_libro_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: