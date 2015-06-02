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
import netsvc

class stock_location(osv.osv):
    _inherit = 'stock.location'

    _columns = {
        'obra': fields.boolean('Obra'),
        'polvorin': fields.boolean('Polvorin'),
        }

stock_location()

class iso_traza_artillero(osv.osv):
        
    _name='iso.traza.artillero'
    _description='Artillero'
    _columns={
        'name': fields.char("Nombre", size=145, required=True), 
        'dni': fields.char("DNI", size=32),
        'cartilla': fields.char("Cartilla de Artillero", size=32),
        'username': fields.char('Login', size = 64, required = True),
        'password': fields.char('Password', size = 64, required = True),
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
        'name': fields.char("Nombre", size=65, select=True),
        'num_acta': fields.char("Número de Acta", size=65, select=True),
        'date': fields.date('Fecha', required=True, select=True),
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', help='Responsable de utilización - Artillero'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
        #'obra': fields.char("Derecho Minero/Obra", size=265),
        'obra_id': fields.many2one('stock.location', 'Obra', domain = [('obra','=',True)]),
        'moves_ids': fields.one2many('stock.move', 'acta_id', "Movimientos"),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'iso.traza.acta'),
    }
    
    def alta_mov_out_sinproducto(self, cr, uid, serial, qty, acta_id, polvorin, context=None):
        acta_data = self.browse(cr, uid, acta_id, context=context)
        move_obj = self.pool.get('stock.move')
        if qty:
            qty= float(qty)
        else:
            qty = 1.0
            
        #alta de producto no existente        
        p_template_vals = {
            'supply_method': 'buy',
            'standard_price': 1.00,
            'mes_type': 'fixed',
            'uom_id': 1,
            'uom_po_id': 1,
            'name': "producto no existente",
            'description': "producto no existente",
            'description_purchase': "producto no existente",
            'description_sale': "producto no existente",
            'type': 'consu',
            'procure_method': 'make_to_stock',
            'categ_id': 1,
            'cost_method': 'standard',
            'warranty': 0,
            'purchase_ok': True,
            'company_id': 1,
            'rental': False,
            'sale_ok': True,
            'sale_delay': 7,
            'produce_delay': 1,
        }
        
        product_template_id = self.pool.get('product.template').create(cr, uid, p_template_vals)
         
        p_product_vals = {
            'product_tmpl_id': product_template_id,
            'default_code': serial,
            'valuation': 'manual_periodic',
            'lot_split_type': 'single',
            'price_extra': 0.00,
            'name_template': "producto no existente",
            'active': True,
            'price_margin': 1.00,
            'track_production': False,
            'track_outgoing': False,
            'track_incoming': True,
        }
                
        product_id = self.pool.get('product.product').create(cr, uid, p_product_vals)
        
        new_move_out_id = move_obj.create(cr, uid, vals = {
            'acta_id': acta_id,
            'serial': serial,                                               
            'location_id': polvorin,
            'location_dest_id': acta_data.obra_id.id,
            'product_id': product_id,
            'product_uom': 1,
            'product_uos_qty': qty,
            'product_qty': qty,
            'name': serial}, context = context)
        return new_move_out_id
    
    def alta_mov_out(self, cr, uid, move_in_id, qty, acta_id, polvorin, context=None):        
        acta_data = self.browse(cr, uid, acta_id, context=context)
        move_obj = self.pool.get('stock.move')
        move_in_obj = move_obj.browse(cr, uid, move_in_id, context=context)
        if qty:
            qty= float(qty)
        else:
            qty = move_in_obj.product_qty
        new_move_out_id = move_obj.create(cr, uid, vals = {
            'acta_id': acta_id,
            'serial': move_in_obj.serial,                                               
            'location_id': polvorin,
            'location_dest_id': acta_data.obra_id.id,
            'product_id': move_in_obj.product_id.id,
            'product_uom': move_in_obj.product_uom.id,
            'product_uos_qty': qty or 1.0,
            'product_qty': qty or 1.0,
            'name': move_in_obj.serial,
            'tracking_id': move_in_obj.tracking_id.id}, context = context)
        return new_move_out_id
    
    def add_moves(self, cr, uid, acta_id, moves, polvorin, context=None):
        new_moves_out = []
        move_obj = self.pool.get('stock.move')
        tracking_obj = self.pool.get('stock.tracking')
        for move_code in moves:
            m = move_obj.search(cr, uid, [('serial', '=', move_code[0])])
            t = tracking_obj.search(cr, uid, [('serial', '=', move_code[0])])
            if m:
                #alta de un solo movimiento de salida
                new_move_out = self.alta_mov_out(cr, uid, m[0], move_code[1], acta_id, polvorin, context)
                new_moves_out.append(new_move_out)
            elif t:
                #alta de todos los movimientos del paquete
                moves_from_tracking = move_obj.search(cr, uid, [('tracking_id', '=', t[-1])], context=context)
                if moves_from_tracking:
                    for move_from_tracking in moves_from_tracking:
                        #alta de cada movimiento del paquete
                        new_move_out = self.alta_mov_out(cr, uid, move_from_tracking, None, acta_id, polvorin, context)
                        new_moves_out.append(new_move_out)
                else:
                    paquete_hijo_id = tracking_obj.search(cr, uid, [('parent_id', '=', t[-1])], context=context)
                    moves_from_tracking_hijo = move_obj.search(cr, uid, [('tracking_id', '=', paquete_hijo_id[-1])], context=context)
                    if moves_from_tracking_hijo:
                        for move_from_tracking_hijo in moves_from_tracking_hijo:
                            #alta de cada movimiento del paquete
                            new_move_out = self.alta_mov_out(cr, uid, move_from_tracking_hijo, None, acta_id, polvorin, context)
                            new_moves_out.append(new_move_out)
                    else:
                        new_move_out = self.alta_mov_out_sinproducto(cr, uid, move_code[0], move_code[1], acta_id, polvorin, context)
                        new_moves_out.append(new_move_out)
            else:
                new_move_out = self.alta_mov_out_sinproducto(cr, uid, move_code[0], move_code[1], acta_id, polvorin, context)
                new_moves_out.append(new_move_out)

        if new_moves_out:
            return True
        else:
            return False
        
    def regenerar_acta(self, cr, uid, id, context=None):
        obra = self.browse(cr, uid, id[0], context=context).obra_id.id
        move_obj = self.pool.get('stock.move')
        acta_moves = move_obj.search(cr, uid, [('acta_id', '=', id[0])], context=context)
        # recorro los movimientos del acta
        for acta_move in acta_moves:
            move_data = move_obj.browse(cr, uid, acta_move, context=context)
            product_id = move_data.product_id.id
            product_name = self.pool.get('product.product').browse(cr, uid, product_id, context=context).name
            # miro si el movimiento es de los de producto no existente
            if product_name == "producto no existente":
                # el serial del movimiento tiene 3 posibilidades:
                # 1 que pertenezca a un paquete que sería el caso normal a tratar
                # 2 que pertenezca a un movimiento existente (no debería ser así)
                # 3 que no exista ese serial en el programa (no debería ser así)
                # trataré solamente el primer caso
                # busco el serial entre los paquetes y creo un movimiento por cada elemento del paquete
                # posteriormente elimino el movimiento de salida con producto no existente
                serial_paquete = move_data.serial
                paquetes_id = self.pool.get('stock.tracking').search(cr, uid, [('serial', '=', serial_paquete)], context=context)
                if not paquetes_id:
                    #busco el paquete hijo y sus movimientos
                    paquetes_hijos_id = self.pool.get('stock.tracking').search(cr, uid, [('parent_id', '=', paquetes_id[0])], context=context)
                    if not paquetes_hijos_id:
                        # no hay nada que hacer o en todo caso ver si entra dentro de los casos 2 o 3
                        continue
                    else:
                        se_hizo = 0
                        for paquete_hijo_id in paquetes_hijos_id:
                            moves_del_paquete_hijo = move_obj.search(cr, uid, [('tracking_id', '=', paquete_hijo_id)], context=context)
                            if moves_del_paquete_hijo:
                                se_hizo = 1
                                for move_del_paquete_hijo in moves_del_paquete_hijo:
                                    # crear un movimiento de salida
                                    move_del_paquete_hijo_data = move_obj.browse(cr, uid, move_del_paquete_hijo, context=context)
                                    move_obj.create(cr, uid, vals = {
                                        'acta_id': id[0],
                                        'serial': move_del_paquete_hijo_data.serial,                                               
                                        'location_id': move_data.location_id.id,
                                        'location_dest_id': obra,
                                        'product_id': move_del_paquete_hijo_data.product_id.id,
                                        'product_uom': move_del_paquete_hijo_data.product_uom.id,
                                        'product_uos_qty': move_del_paquete_hijo_data.product_uos_qty,
                                        'product_qty': move_del_paquete_hijo_data.product_qty,
                                        'name': move_del_paquete_hijo_data.serial,
                                        'tracking_id': move_del_paquete_hijo_data.tracking_id.id}, context = context)
                            if se_hizo:
                                # borrar el movimiento sin producto
                                move_obj.unlink(cr, uid, acta_move, context=None)
                            else:
                                continue
                else:
                    moves_del_paquete = move_obj.search(cr, uid, [('tracking_id', '=', paquetes_id[0])], context=context)
                    for move_del_paquete in moves_del_paquete:
                        # crear un movimiento de salida
                        move_del_paquete_data = move_obj.browse(cr, uid, move_del_paquete, context=context)
                        move_obj.create(cr, uid, vals = {
                            'acta_id': id[0],
                            'serial': move_del_paquete_data.serial,                                               
                            'location_id': move_data.location_id.id,
                            'location_dest_id': obra,
                            'product_id': move_del_paquete_data.product_id.id,
                            'product_uom': move_del_paquete_data.product_uom.id,
                            'product_uos_qty': move_del_paquete_data.product_uos_qty,
                            'product_qty': move_del_paquete_data.product_qty,
                            'name': move_del_paquete_data.serial,
                            'tracking_id': move_del_paquete_data.tracking_id.id}, context = context)
                    #borrar el movimiento sin producto
                    move_obj.unlink(cr, uid,[acta_move], context=None)
        return True
    
    def date_to_moves(self, cr, uid, ids, context=None):
        """ Changes move date
        """
        move_obj = self.pool.get('stock.move')
        date = self.browse(cr, uid, ids[0], context=context).date
        moves = self.browse(cr, uid, ids[0], context=context).moves_ids
        for move in moves:
            move_obj.write(cr, uid, move.id, {'date':date, 'create_date':date, 'date_expected':date}, context=context)
        return True
    
    def obra_to_moves(self, cr, uid, ids, context=None):
        """ Changes location_dest_id
        """
        move_obj = self.pool.get('stock.move')
        obra_id = self.browse(cr, uid, ids[0], context=context).obra_id
        moves = self.browse(cr, uid, ids[0], context=context).moves_ids
        for move in moves:
            move_obj.write(cr, uid, move.id, {'location_dest_id':obra_id.id}, context=context)
        return True
    
    def action_done_moves(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        for acta in self.browse(cr, uid, ids, context=context):
            ml_ids = []
            for ml in acta.moves_ids:
                ml_ids.append(ml.id)
            move_obj.write(cr, uid, ml_ids, {'state': 'done'})
        return True
    
#     def action_reopen(self, cr, uid, ids, context=None):
#         move_obj = self.pool.get('stock.move')
#         for acta in self.browse(cr, uid, ids):
#             ml_ids = []
#             for ml in acta.moves_ids:
#                 ml_ids.append(ml.id)
#             move_obj.write(cr, uid, ml_ids, {'state':'draft'})
#         return True
    
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
        'obra_id': fields.many2one('stock.location', 'Obra', domain = [('obra','=',True)]),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'iso.traza.libro'),
    }
    
iso_traza_libro()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _order = 'date desc, id'
     
    _columns = {
        'num_guia': fields.char('Número de Guía', size=25),
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', ondelete='cascade', help='Responsable de utilización - Artillero'),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', ondelete='cascade', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'num_catalog': fields.char('Número de catalogación', size=25),                
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
                }
    
    def date_to_moves(self, cr, uid, ids, context=None):
        """ Changes move date
        """
        move_obj = self.pool.get('stock.move')
        date = self.browse(cr, uid, ids[0], context=context).date
        moves = self.browse(cr, uid, ids[0], context=context).move_lines
        for move in moves:
            move_obj.write(cr, uid, move.id, {'date':date, 'create_date':date, 'date_expected':date}, context=context)
        return True
    
    def polvorin_to_moves(self, cr, uid, ids, context=None):
        """ Changes location_dest_id
        """
        move_obj = self.pool.get('stock.move')
        location_dest_id = self.browse(cr, uid, ids[0], context=context).location_dest_id
        moves = self.browse(cr, uid, ids[0], context=context).move_lines
        for move in moves:
            move_obj.write(cr, uid, move.id, {'location_dest_id':location_dest_id.id}, context=context)
        return True
    
    def action_reopen(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids):
            ml_ids = []
            for ml in pick.move_lines:
                ml_ids.append(ml.id)
            move_line_obj.write(cr, uid, ml_ids, {'state':'draft'})

            self.write(cr, uid, pick.id, {'state':'draft'})
            wf_service = netsvc.LocalService("workflow")

            wf_service.trg_delete(uid, 'stock.picking', pick.id, cr)
            wf_service.trg_create(uid, 'stock.picking', pick.id, cr)

            self.log_picking(cr, uid, ids, context=context)  
            
        return True
    
#     def create(self, cr, uid, vals, context={}):
#         vals.update({'type': 'in'})
#         return super(stock_picking, self).create(cr, uid, vals, context)
    
stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _order = 'date desc, picking_id desc'
    
    def _check_tracking(self, cr, uid, ids, context=None):
        return True

    def _check_product_lot(self, cr, uid, ids, context=None):
        return True

    _columns = {
        'artillero_id': fields.many2one('iso.traza.artillero', 'Artillero', ondelete='cascade', help='Responsable de utilización - Artillero'),
        'dir_facul_id': fields.many2one('iso.traza.dirfacul', 'Director facultativo', ondelete='cascade', help='Director facultativo'),
        'resp_explot_id': fields.many2one('iso.traza.respexplot', 'Responsable explotación', ondelete='cascade', help='Responsable explotación, encargado del libro de registro y usuario del programa'),
        'num_catalog': fields.char('Número de catalogación', size=25),
        'serial': fields.char('Número de dentificación', required=True ,size=25, help='Número de dentificación único del producto'),
        'consum_hab_id' : fields.many2one('res.partner', 'Consumidor habitual de explosivos', ondelete='cascade', help="Consumidor habitual de explosivos"),
        'libro_id' : fields.many2one('iso.traza.libro', 'Libro de Registro'),
        'acta_id' : fields.many2one('iso.traza.acta', 'Acta de Consumo'),
    }
    _constraints = [
        (_check_tracking,
            'You must assign a production lot for this product',
            ['prodlot_id']),
        (_check_product_lot,
            'You try to assign a lot which is not from the same product',
            ['prodlot_id'])]
    
    
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

class stock_tracking(osv.osv):
    _inherit = 'stock.tracking'
    
    _columns = {
        'parent_id': fields.many2one('stock.tracking', 'Paquete Padre', ondelete='cascade'),
        'nivel': fields.char('Nivel', size=16),
    }
    _constraints = [
        (osv.osv._check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]
    
stock_tracking()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
