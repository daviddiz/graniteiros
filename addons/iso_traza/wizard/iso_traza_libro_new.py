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
import time
from datetime import datetime

class iso_traza_libro_new(osv.osv_memory):
    _name = 'iso.traza.libro.new'
    _description = 'Nuevo Libro de Registro'
    _columns = {
        'date_from': fields.date("Fecha Inicial"),
        'date_to': fields.date("Fecha Final"),
    }

    def crear_libro(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_form = self.read(cr, uid, ids, ['date_from', 'date_to'])[0]
        
        d_from = data_form['date_from']
        d_to = data_form['date_to']
        
        d_from = d_from + ' 00:00:00'
        d_from = datetime.strptime(d_from, '%Y-%m-%d %H:%M:%S')
        
        d_to = d_to + ' 23:59:59'
        d_to = datetime.strptime(d_to, '%Y-%m-%d %H:%M:%S')
        
        
        obj = self.pool.get('stock.move')
        moves_ids = obj.search(cr, uid, [('date','>=',d_from.strftime('%Y-%m-%d %H:%M:%S')), ('date','<=',d_to.strftime('%Y-%m-%d %H:%M:%S'))])
        
        vals={
            "date": d_from.strftime('%Y-%m-%d'),
            "moves_ids": [(6,0,moves_ids)],
        }
        
        libro_id = self.pool.get('iso.traza.libro').create(cr,uid,vals,context)
        
        return {
            'domain': "[('id','=', %s)]" % (libro_id),
            'name': 'Libro de Registro',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iso.traza.libro',
            'type': 'ir.actions.act_window',
            }

iso_traza_libro_new()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: