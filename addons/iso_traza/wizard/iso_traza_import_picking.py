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
        
        #for node in tree.getiterator('ShipmentNumber'):
#         for node in tree.iter('ShipmentNumber'):
#             ShipmentNumber = node.text
#             break
        
        for node in tree.getiterator('DeliveryNoteNumber'):         
        #for node in tree.iter('DeliveryNoteNumber'):
            DeliveryNoteNumber = node.text
            num_recibo = "Numero de recibo: " + DeliveryNoteNumber
            break
        
        for node in tree.getiterator('Sender'):
        #for node in tree.iter('Sender'):
#             if node.find('Code') is not None:
#                 Code = node.find('Code').text
            if node.find('Name') is not None:
                Name = node.find('Name').text
#             if node.find('Name2') is not None:
#                 Name2 = node.find('Name2').text
#             if node.find('AddressCode') is not None:
#                 AddressCode = node.find('AddressCode').text
            if node.find('Address') is not None:
                Address = node.find('Address').text
#             if node.find('Address2') is not None:
#                 Address2 = node.find('Address2').text
            if node.find('Zipcode') is not None:
                Zipcode = node.find('Zipcode').text
            if node.find('City') is not None:
                City = node.find('City').text
#             if node.find('Country') is not None:
#                 Country = node.find('Country').text
#             if node.find('State') is not None:
#                 State = node.find('State').text
            
            proveedor_ids = self.pool.get('res.partner').search(cr, uid, [('name', '=', Name)])
            if proveedor_ids:
                proveedor_id = proveedor_ids[0]
            else:
                proveedor_vals = {
                    'name': Name,
                    'supplier': True,
                    'active': True,
                }
                proveedor_id = self.pool.get('res.partner').create(cr, uid, proveedor_vals)
                address_vals = {
                    'partner_id': proveedor_id,
                    'type' : 'default',
                    'street': Address,
                    'zip': Zipcode,
                    'city': City,
                    'active': True,
                    'country_id': 67,
                }
                address_id = self.pool.get('res.partner.address').create(cr, uid, address_vals)
                
                
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
            'partner_id': proveedor_id,
            'note': num_recibo,
        }
        picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals)        
                
        
        summary_items = []
        for node in tree.getiterator('Item'):        
        #for node in tree.iter('SummaryItem'):
            sid = node.attrib.get('SID')
            psn = node.attrib.get('PSN')
            
            if node.find('ProducerProductCode') is not None:
                ProducerProductCode = node.find('ProducerProductCode').text
#             if node.find('ProducerProductName') is not None:
#                 ProducerProductName = node.find('ProducerProductName').text
#             if node.find('ItemQuantity') is not None:
#                 ItemQuantity = node.find('ItemQuantity').text
#             if node.find('CountOfTradeUnits') is not None:
#                 CountOfTradeUnits = node.find('CountOfTradeUnits').text
            if node.find('PackagingLevel') is not None:
                PackagingLevel = node.find('PackagingLevel').text
#             if node.find('ProductionDate') is not None:
#                 ProductionDate = node.find('ProductionDate').text
#             if node.find('Length') is not None:
#                 Length = node.find('Length').text
#             if node.find('UnitOfMeasure') is not None:
#                 UnitOfMeasure = node.find('UnitOfMeasure').text

            new_sum_item = {'sid': sid, 'psn': psn, 'product_code': ProducerProductCode, 'level': PackagingLevel}
            summary_items.append(new_sum_item)
                        
        units = tree.find('Units')
        sem = 0
        for unit in units._children:
            if unit.attrib.get('SID') is None:
                continue
            
            sid = unit.attrib.get('SID')
            for i in range(len(summary_items)):
                if summary_items[i]['sid']==sid and sem==0:
                    psn = summary_items[i]['psn']
                    product_code = summary_items[i]['product_code']
                    level = int(summary_items[i]['level'])
                    uid_code = unit.attrib.get('UID')
                    serial = str(psn) + str(uid_code)
                    tracking_vals = {
                         'active': True,
                         'serial': serial,
                         'date': datetime_now,
                         'name': serial,
                         'nivel': level,
                         }    
                    tracking_id = self.pool.get('stock.tracking').create(cr, uid, tracking_vals)
                    sem = 1
            
            if unit.find('Units') is not None:
                units2 = unit.find('Units')
                sem2 = 0
                for unit2 in units2._children:
                    sid = unit2.attrib.get('SID')
                    for i in range(len(summary_items)):
                        if summary_items[i]['sid']==sid and sem2==0:
                            psn = summary_items[i]['psn']
                            product_code = summary_items[i]['product_code']
                            level = int(summary_items[i]['level'])
                            uid_code = unit.attrib.get('UID')
                            serial = str(psn) + str(uid_code)
                            tracking_vals = {
                                 'active': True,
                                 'serial': serial,
                                 'date': datetime_now,
                                 'name': serial,
                                 'nivel': level,
                                 'parent_id': tracking_id,
                                 }    
                            tracking_id = self.pool.get('stock.tracking').create(cr, uid, tracking_vals) 
                            sem2 = 1
                    if unit2.find('Items') is not None:
                        items = unit2.find('Items')
                        for item in items._children:
                            sid = item.attrib.get('SID')
                            uid_code = item.attrib.get('UID')
                            psn = item.attrib.get('PSN')
                            serial = str(psn) + str(uid_code)
                            product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', product_code)])
                            if product_ids:
                                product_id = product_ids[0]
                            else:
                                p_template_vals = {
                                    'supply_method': 'buy',
                                    'standard_price': 1.00,
                                    'mes_type': 'fixed',
                                    'uom_id': 1,
                                    'uom_po_id': 1,
                                    'name': product_code,
                                    'description': product_code,
                                    'description_purchase': product_code,
                                    'description_sale': product_code,
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
                                    'default_code': product_code,
                                    'valuation': 'manual_periodic',
                                    'lot_split_type': 'single',
                                    'price_extra': 0.00,
                                    'name_template': product_code,
                                    'active': True,
                                    'price_margin': 1.00,
                                    'track_production': False,
                                    'track_outgoing': False,
                                    'track_incoming': True,
                                }
                                
                                product_id = self.pool.get('product.product').create(cr, uid, p_product_vals)
                                
                            move_vals = {
                                'location_id': 8,
                                'location_dest_id': 12,
                                'product_id': product_id,
                                'picking_id': picking_id,
                                'product_uom': 1,
                                'product_uos_qty': 1,
                                'product_qty': 1,
                                'serial': serial,
                                'name': serial,
                                'tracking_id': tracking_id,
                            }    
                            move_id = self.pool.get('stock.move').create(cr, uid, move_vals)  
                            
             
        f.close()
        
        cr.execute(
                            "select id,name from ir_ui_view \
                            where model= 'stock.picking' \
                            and name = 'view.picking.in.form_traza'"
                        )
        view_res = cr.fetchone()
         
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
