# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from datetime import datetime

class iso_traza_artillero(osv.osv):
        
    _name='iso.traza.artillero'
    _description='Artillero'
    _columns={
        'name': fields.char("Nombre", size=145, required=True), 
        'dni': fields.char("DNI", size=32),
        'cartilla': fields.char("Cartilla de Artillero", size=32),
    }
    
iso_traza_artillero()

class iso_traza_dirfacul(osv.osv):
        
    _name='iso.traza.dirfacul'
    _description='Director facultativo'
    _columns={
        'name': fields.char("Nombre", size=145, required=True),
        'dni': fields.char("DNI", size=32), 
    }
    
iso_traza_dirfacul()

class iso_traza_respexplot(osv.osv):
        
    _name='iso.traza.respexplot'
    _description='Responsable explotación'
    _columns={
        'name': fields.char("Nombre", size=145, required=True),
        'dni': fields.char("DNI", size=32), 
    }
    
iso_traza_respexplot()

class iso_traza_acta(osv.osv):
        
    _name='iso.traza.acta'
    _description='Acta de Consumo'
    _columns={
        'name': fields.char("Nombre", size=65, required=True, readonly=True, select=True),
        'date': fields.date('Fecha', required=True, select=True),
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', help='Responsable de utilización - Artillero'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
        'obra': fields.char("Derecho Minero/Obra", size=265),
        'moves_ids': fields.one2many('stock.move', 'acta_id', "Movimientos"),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'iso.traza.acta'),
    }
    
iso_traza_acta()

class iso_traza_libro(osv.osv):
        
    _name='iso.traza.libro'
    _description='Libro de Registro'
    _columns={
        'name': fields.char("Nombre", size=65, required=True, readonly=True, select=True),
        'date': fields.date('Fecha Inicio Libro', required=True, select=True),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'moves_ids': fields.one2many('stock.move', 'libro_id', "Movimientos"),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'iso.traza.libro'),
    }
    
iso_traza_libro()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _order = 'date desc, id'
     
    _columns = {
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', ondelete='cascade', help='Responsable de utilización - Artillero'),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', ondelete='cascade', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'num_catalog': fields.char('Número de catalogación', size=25),                
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
                }
    
#     def create(self, cr, uid, vals, context={}):
#         vals.update({'type': 'in'})
#         return super(stock_picking, self).create(cr, uid, vals, context)
    
stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _order = 'date desc, picking_id desc'
    
#     def _pending_quantity(self, cr, uid, ids, field_name, arg, context=None):
#         result = {}
#         for move in self.browse(cr, uid, ids, context):
#             result[move.id] = move.product_qty - move.received_quantity
#         return result

    _columns = {
#         'consumed_quantity': fields.float('Cantidad consumida', help='Cantidad consumida'),
#         'pending_quantity': fields.function(_pending_quantity, method=True, type='float', string='Cantidad restante', store=False, help='Cantidad restante'),
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', ondelete='cascade', help='Responsable de utilización - Artillero'),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', ondelete='cascade', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'num_catalog': fields.char('Número de catalogación', size=25),
#         'serial': fields.char('Número de dentificación', required=True ,size=25, help='Número de dentificación único del producto'),
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
        'libro_id' : fields.many2one('iso.traza.libro', 'Libro de Registro'),
        'acta_id' : fields.many2one('iso.traza.acta', 'Acta de Consumo'),
    }
    
#     def create(self, cr, uid, vals, context={}):
#         vals.update({'state': 'done'})
#         return super(stock_move, self).create(cr, uid, vals, context)
    
    def _default_artillero_id(self, cr, uid, context=None):
        pick = context.get('pick', False)
        if pick:
            res = self.pool.get('stock.picking').browse(cr, uid, pick, context=context).artillero_id.id
            return res
        else:
            return False
     
    def _default_dir_facul_id(self, cr, uid, context=None):
        pick = context.get('pick', False)
        if pick:
            res = self.pool.get('stock.picking').browse(cr, uid, pick, context=context).dir_facul_id.id
            return res
        else:
            return False
     
    def _default_resp_explot_id(self, cr, uid, context=None):
        pick = context.get('pick', False)
        if pick:
            res = self.pool.get('stock.picking').browse(cr, uid, pick, context=context).resp_explot_id.id
            return res
        else:
            return False
     
    def _default_consum_hab_id(self, cr, uid, context=None):
        pick = context.get('pick', False)
        if pick:
            res = self.pool.get('stock.picking').browse(cr, uid, pick, context=context).consum_hab_id.id
            return res
        else:
            return False

    def _default_picking_id(self, cr, uid, context=None):
        res = context.get('pick', False)
        return res

    def _default_location(self, cr, uid, context=None):
        t = context.get('type', False)
        if t=='in':
            return 8
        elif t=='out':
            return 12
        else:
            return False

    def _default_location_dest(self, cr, uid, context=None):
        t = context.get('type', False)
        if t=='in':
            return 12
        elif t=='out':
            return 9
        else:
            return False

    _defaults = {
        'location_id': _default_location,
        'location_dest_id': _default_location_dest,
        'artillero_id': _default_artillero_id,
        'dir_facul_id': _default_dir_facul_id,
        'resp_explot_id': _default_resp_explot_id,
        'consum_hab_id': _default_consum_hab_id,
        'picking_id': _default_picking_id,
    }
    
    def add_move_in_from_app(self, cr, uid, data, context=None):
        product_ref = data.split()[1]
        serial = data.split()[0]
        product_obj = self.pool.get('product.product')
        tracking_obj = self.pool.get('stock.tracking')
        move_obj = self.pool.get('stock.move')
        product_ids = product_obj.search(cr, uid, [('default_code', '=', product_ref)])
        product_name = product_obj.browse(cr, uid, product_ids[0], context=context).name_template
               
        datetime_now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        new_tracking_id = tracking_obj.create(cr, uid, vals = {
                    'active': True,
                    'serial': serial,
                    'date': datetime_now,
                    'name': serial}, context = context)
        new_move_id = move_obj.create(cr, uid, vals = {
                    'location_id': 8,
                    'location_dest_id': 12,
                    'product_id': product_ids[0],
                    'product_uom': 1,
                    'product_uos_qty': 1,
                    'product_qty': 1,
                    'name': product_name,
                    'tracking_id': new_tracking_id}, context = context)
        return False
        

stock_move()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
