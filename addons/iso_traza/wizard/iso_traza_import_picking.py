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

from osv import osv,fields
import os
import base64
import tempfile
from xml.etree import ElementTree
import datetime

class iso_traza_import_picking(osv.osv_memory):
    _name = 'iso.traza.import.picking'
    _description = 'Importar entrada de productos'
    _columns={
        'file': fields.binary('Albaran a Importar'),
    }
    
    _defaults = {
    }
    
    def import_picking(self, cr, uid, ids, context=None):
        if not context: context = {}
        
        datetime_now = datetime.datetime.today()
        content = self.browse(cr,uid,ids)[0].file
        
        file_path = tempfile.gettempdir()+'/file.xml'
        f = open(file_path,'wb')
        f.write(content.decode('base64'))
        f.close()  

        f = open(file_path,'r')
        tree = ElementTree.parse(f)
                
        for node in tree.iter('SummaryItem'):
            
            sid = node.attrib.get('SID')
            psn = node.attrib.get('PSN')
            
            for i in range(len(node)):
                if node[i].tag == "ProducerProductCode":
                    ProducerProductCode = node[i].text
                elif node[i].tag == "ProducerProductName":
                    ProducerProductName = node[i].text
                elif node[i].tag == "ItemQuantity":
                    ItemQuantity = node[i].text
                elif node[i].tag == "CountOfTradeUnits":
                    CountOfTradeUnits = node[i].text
                elif node[i].tag == "PackagingLevel":
                    PackagingLevel = node[i].text
                elif node[i].tag == "ProductionDate":
                    ProductionDate = node[i].text
                elif node[i].tag == "Length":
                    Length = node[i].text
                elif node[i].tag == "UnitOfMeasure":
                    UnitOfMeasure = node[i].text
                    if UnitOfMeasure == 'KGM':
                        uom = 2
                    elif UnitOfMeasure == 'MTR':
                        uom = 7
                    else:
                        uom = 1
                elif node[i].tag == "NEW":
                    NEW = node[i].text
                    
            if sid[0]=="I":
                product_ids = self.pool.get('product.product').search(cr, uid, [('name_template', '=', ProducerProductName)], context=context)
                if len(product_ids) > 0 :
                    sid_existente = self.pool.get('product.product').browse(cr, uid, product_ids[0], context=context).default_code
<<<<<<< HEAD
                    if sid not in sid_existente.split():
                        self.pool.get('product.product').write(cr, uid, product_ids[0], {'default_code': sid_existente+" "+sid})
=======
                    self.pool.get('product.product').write(cr, uid, product_ids[0], {'default_code': sid_existente+" "+sid})
>>>>>>> branch 'master' of https://github.com/daviddiz/graniteiros.git
                else:        
                    p_template_vals = {
                        'supply_method': 'buy',
                        'standard_price': 1.00,
                        'mes_type': 'fixed',
                        'uom_id': uom,
                        'uom_po_id': uom,
                        'name': ProducerProductName,
                        'description': ProducerProductName,
                        'description_purchase': ProducerProductName,
                        'description_sale': ProducerProductName,
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
                        'default_code': sid,
                        'valuation': 'manual_periodic',
                        'lot_split_type': 'single',
                        'price_extra': 0.00,
                        'name_template': ProducerProductName,
                        'active': True,
                        'price_margin': 1.00,
                        'track_production': False,
                        'track_outgoing': False,
                        'track_incoming': True,
                    }
                    
                    product_product_id = self.pool.get('product.product').create(cr, uid, p_product_vals)
            
        f.close()
        
        f = open(file_path,'r')
        tree = ElementTree.parse(f)
         
        picking_vals = {
                'type': 'in',
                'move_type': 'direct',
                'company_id': 1,
                'invoice_state': 'none',
                'auto_picking': False,
                'location_id': 8,
                'location_dest_id': 12,
                'state': 'draft',
                'date': datetime_now,
                }
        picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals)
        
        print "alta de albaran"
         
        i = 0
        for node in tree.iter('Item'):
            print i
            i+=1
             
            uid_source = node.attrib.get('UID')
            sid = node.attrib.get('SID')
            psn = node.attrib.get('PSN')
            
            product_ids = self.pool.get('product.product').search(cr, uid, [], context=context)
            for product_id in product_ids:
                sid_varios = self.pool.get('product.product').browse(cr, uid, product_id, context=context).default_code.split()
                if sid in sid_varios:
                    p_id = product_id
                    break
<<<<<<< HEAD
            
            tracking_vals = {
                     'active': True,
                     'serial': uid_source,
                     'date': datetime_now,
                     'name': uid_source,
                     }    
            tracking_id = self.pool.get('stock.tracking').create(cr, uid, tracking_vals)     
 
            move_vals = {
                     'location_id': 8,
                     'location_dest_id': 12,
                     'product_id': p_id,
                     'picking_id': picking_id,
                     'product_uom': 1,
                     'product_uos_qty': 1,
                     'product_qty': 1,
                     'name': uid_source,
                     'tracking_id': tracking_id,
=======
                
 
            move_vals = {
                     'location_id': 8,
                     'location_dest_id': 12,
                     'product_id': p_id,
                     'picking_id': picking_id,
                     'product_uom': 1,
                     'product_uos_qty': 1,
                     'product_qty': 1,
                     'name': uid_source,
>>>>>>> branch 'master' of https://github.com/daviddiz/graniteiros.git
                     }    
            move_id = self.pool.get('stock.move').create(cr, uid, move_vals)  
             
        f.close()
<<<<<<< HEAD
        
#         view_ids = self.pool.get('ir.ui.view').search(cr, uid, [('name', '=', 'view.picking.in.tree.traza')], context=context)
=======
         
#         os.remove(f)
>>>>>>> branch 'master' of https://github.com/daviddiz/graniteiros.git
        
        cr.execute(
                            "select id,name from ir_ui_view \
                            where model= 'stock.picking' \
                            and name = 'view.picking.in.form_traza'"
                        )
        view_res = cr.fetchone()
         
#         os.remove(f)
         
        return {
                'domain': "[('id','=',%s)]" % (picking_id),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'view_id': view_res,
                'type': 'ir.actions.act_window',
                'res_id': picking_id
        }

iso_traza_import_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
