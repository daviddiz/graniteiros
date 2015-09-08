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
from decimal_precision import decimal_precision as dp

class iso_traza_moves_changes_unit(osv.osv_memory):
    """
    Cambiar unidades de un movimiento
    """

    _name = "iso.traza.moves.changes.unit"
    _description = "Cambiar unidades de un movimiento"
    _columns = {
        'uom_id': fields.many2one('product.uom', 'Unidad de Medida'),
        }

    def moves_changes_unit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_form = self.read(cr, uid, ids, ['uom_id'])[0]
        uom = data_form['uom_id']
        
        if not uom:
            return False
        
        moves_ids = context['active_ids']
        move_obj = self.pool.get('stock.move')
 
        for move_id in moves_ids:
            move_data = move_obj.browse(cr, uid, move_id, context=context)
            if move_data.state not in ('draft'):
                raise osv.except_osv(_('Warning'), _("No se puede modificar un movimiento que no esté en borrador"))
            #modifico el movimiento
            m = move_obj.write(cr, uid, [move_id], {'product_uom': uom})
            
        return {
            'domain': "[('id','in', %s)]" % (moves_ids),
            'name': 'Movimientos',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'type': 'ir.actions.act_window',
            }

iso_traza_moves_changes_unit()


class iso_traza_moves_changes_qty(osv.osv_memory):
    """
    Cambiar cantidad de un movimiento
    """

    _name = "iso.traza.moves.changes.qty"
    _description = "Cambiar cantidad de un movimiento"
    _columns = {
        'qty':fields.float('Cantidad',  digits_compute=dp.get_precision('Product UoM')),
        }

    def moves_changes_qty(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_form = self.read(cr, uid, ids, ['qty'])[0]
        qty = data_form['qty']
        
        if not qty:
            return False
        
        moves_ids = context['active_ids']
        move_obj = self.pool.get('stock.move')
 
        for move_id in moves_ids:
            move_data = move_obj.browse(cr, uid, move_id, context=context)
            if move_data.state not in ('draft'):
                raise osv.except_osv(_('Warning'), _("No se puede modificar un movimiento que no esté en borrador"))
            #modifico el movimiento
            m = move_obj.write(cr, uid, [move_id], {'product_qty': qty, 'product_uos_qty': qty})
            
        return {
            'domain': "[('id','in', %s)]" % (moves_ids),
            'name': 'Movimientos',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.move',
            'type': 'ir.actions.act_window',
            }

iso_traza_moves_changes_qty()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: