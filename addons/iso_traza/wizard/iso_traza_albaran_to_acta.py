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
import netsvc
import pooler
import time
from datetime import datetime

class iso_traza_albaran_to_acta(osv.osv_memory):
    """
    Convertir albarán a acta de consumo
    """

    _name = "iso.traza.albaran.to.acta"
    _description = "Convertir albarán a acta de consumo"
    _columns = {
        'date': fields.date("Fecha"),
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', help='Artillero'),
        'obra_id': fields.many2one('stock.location', 'Obra', domain = [('obra','=',True)]),
        }

    def albaran_to_acta(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_form = self.read(cr, uid, ids, ['date','artillero_id','obra_id'])[0]
        d = data_form['date']
        artillero = data_form['artillero_id']
        obra = data_form['obra_id']
        
        if not d or not artillero or not obra:
            return False
        
        d_from = d + ' 00:00:00'
        d_from = datetime.strptime(d_from, '%Y-%m-%d %H:%M:%S')
        
        d_to = d + ' 23:59:59'
        d_to = datetime.strptime(d_to, '%Y-%m-%d %H:%M:%S')
        
        albaranes = context['active_ids']
        albaran_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
 
        for albaran in albaranes:
            albaran_data = albaran_obj.browse(cr, uid, albaran, context=context)
            if albaran_data.state not in ('done'):
                raise osv.except_osv(_('Warning'), _("No se puede crear un acta a partir de un albarán no realizado"))
            #creo el acta
            vals={
                "date": d.strftime('%Y-%m-%d'),
                "artillero_id": artillero,
                "obra_id": obra,
                "consum_hab_id": albaran_data.consum_hab_id,
                "resp_explot_id": albaran_data.resp_explot_id,
                "dir_facul_id": albaran_data.dir_facul_id,
            }
            acta_id = self.pool.get('iso.traza.acta').create(cr,uid,vals,context)
            albaran_moves_ids = move_obj.search(cr, uid, [('picking_id', '=', albaran)])
            for albaran_move_id in albaran_moves_ids:
                albaran_move_data = move_obj.browse(cr, uid, albaran_move_id, context=context)
                vals_move={
                    "date": d.strftime('%Y-%m-%d'),
                    "date_expected": d.strftime('%Y-%m-%d'),
                    "artillero_id": artillero,
                    "obra_id": obra,
                    "consum_hab_id": albaran_data.consum_hab_id,
                    "resp_explot_id": albaran_data.resp_explot_id,
                    "dir_facul_id": albaran_data.dir_facul_id,
                }
            
        return {'type': 'ir.actions.act_window_close'}

iso_traza_albaran_to_acta()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: