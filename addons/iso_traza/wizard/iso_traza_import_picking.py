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
    
    def alta_tracking(self, cr, uid, ids, serial, level, tracking_parent):
        datetime_now = datetime.datetime.today()
        if not level:
            level = 0
        if not tracking_parent:
            tracking_vals = {
                 'active': True,
                 'serial': serial,
                 'date': datetime_now,
                 'name': serial,
                 'nivel': level,
                 }    
            tracking_id = self.pool.get('stock.tracking').create(cr, uid, tracking_vals)
        else:
            tracking_vals = {
                 'active': True,
                 'serial': serial,
                 'date': datetime_now,
                 'name': serial,
                 'nivel': level,
                 'parent_id': tracking_parent,
                 }    
            tracking_id = self.pool.get('stock.tracking').create(cr, uid, tracking_vals)
        return tracking_id 
        
    def alta_product(self, cr, uid, ids, product_code, ProducerProductName=None, uom=None):
        if uom is not None:
            if uom == "KGM":
                uom_id = 2
            elif uom == 'C62':
                uom_id = 1
            elif uom == 'MTR':
                uom_id = 7
            else:
                uom_id = 1
        else:
            uom_id = 1
        if ProducerProductName is not None:
            p_name = ProducerProductName
        else:
            p_name = product_code
        p_template_vals = {
            'supply_method': 'buy',
            'standard_price': 1.00,
            'mes_type': 'fixed',
            'uom_id': uom_id,
            'uom_po_id': uom_id,
            'name': p_name,
            'description': p_name,
            'description_purchase': p_name,
            'description_sale': p_name,
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
            'name_template': p_name,
            'active': True,
            'price_margin': 1.00,
            'track_production': False,
            'track_outgoing': False,
            'track_incoming': True,
        }
                
        product_id = self.pool.get('product.product').create(cr, uid, p_product_vals)
        return product_id
    
    
    def alta_move(self, cr, uid, ids, product, picking, serial, tracking, cant, uom=None):
        if uom is not None:
            if uom == "KGM":
                uom_id = 2
            elif uom == 'C62':
                uom_id = 1
            elif uom == 'MTR':
                uom_id = 7
            else:
                uom_id = 1
        else:
            uom_id = 1
        move_vals = {
            'location_id': 8,
            'location_dest_id': 12,
            'product_id': product,
            'picking_id': picking,
            'product_uom': uom_id,
            'product_uos_qty': cant,
            'product_qty': cant,
            'serial': serial,
            'name': serial,
            'tracking_id': tracking,
        }    
        move_id = self.pool.get('stock.move').create(cr, uid, move_vals)  
        return move_id
    
    def parsear_item(self, cr, uid, ids, item, picking_id, proveedor_id, summary_items, tracking_id=None):
        uid_item = item.attrib.get('UID')
        psn = item.attrib.get('PSN')
        serial = str(psn) + str(uid_item)
        sid = item.attrib.get('SID')
        uom_found = 0
        cant_found = 0
        uom = ""
        uom2 = ""
        if item.find('UnitOfMeasure') is not None:
            uom_found = 1
            uom = item.find('UnitOfMeasure').text
            if item.find('Length') is not None:
                cant = float(item.find('Length').text)
                cant_found = 1
            elif item.find('NEW') is not None and uom<>"MTR":
                cant = float(item.find('NEW').text)
                cant_found = 1
            else:
                cant = 1
        for i in range(len(summary_items)):
            if summary_items[i]['sid']==sid:
                product_code = summary_items[i]['product_code']
                product_name = summary_items[i]['product_name']
                if uom_found==0:
                    uom2 = summary_items[i]['uom']
                    if uom2 is not None and summary_items[i]['height'] is not None:
                        uom_found = 1
                        cant = float(summary_items[i]['height'])
                        cant_found = 1
                    elif uom2 is not None and summary_items[i]['lenght'] is not None:
                        uom_found = 1
                        cant = float(summary_items[i]['lenght'])
                        cant_found = 1
                    else:
                        cant = 1
                elif uom_found==1 and uom=="MTR" and summary_items[i]['lenght'] is not None:
                    cant = float(summary_items[i]['lenght'])
                    cant_found = 1
                product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', product_code)])
                if product_ids:
                    product_id = product_ids[0]
                    if uom_found==1:
                        if uom == "KGM" or uom2 == "KGM":
                            uom_id = 2
                        elif uom == 'MTR' or uom2 == 'MTR':
                            uom_id = 7
                        else:
                            uom_id = 1
                        self.pool.get('product.template').write(cr, uid, [product_id], {'uom_id': uom_id, 'uom_po_id': uom_id})
                else:
                    if uom == "":
                        uom = uom2
                    product_id = self.alta_product(cr, uid, ids, product_code, product_name, uom)
                break
        if uom == "":
            uom = uom2
        move_id = self.alta_move(cr, uid, ids, product_id, picking_id, serial, tracking_id, cant, uom)
        return False
    
    def parsear_unit(self, cr, uid, ids, unit, picking_id, proveedor_id, summary_items, tracking_parent=None):
        uid_unit = unit.attrib.get('UID')
        psn = unit.attrib.get('PSN')
        serial = str(psn) + str(uid_unit)
        aux_sid = 0
        uom_found = 0
        cant_found = 0
        uom = ""
        uom2 = ""
        if unit.find('UnitOfMeasure') is not None:
            uom_found = 1
            uom = unit.find('UnitOfMeasure').text
            if unit.find('Length') is not None:
                cant = float(unit.find('Length').text)
                cant_found = 1
            elif unit.find('NEW') is not None and uom<>"MTR":
                cant = float(unit.find('NEW').text)
                cant_found = 1
            else:
                cant = 1
        if unit.attrib.get('SID') is not None:
            aux_sid = 1
            sid = unit.attrib.get('SID')
            for i in range(len(summary_items)):
                if summary_items[i]['sid']==sid:
                    product_code = summary_items[i]['product_code']
                    product_name = summary_items[i]['product_name']
                    level = int(summary_items[i]['level'])
                    if uom_found==0:
                        uom2 = summary_items[i]['uom']
                        if uom2 is not None and summary_items[i]['height'] is not None:
                            uom_found = 1
                            cant = float(summary_items[i]['height'])
                            cant_found = 1
                        elif uom2 is not None and summary_items[i]['lenght'] is not None:
                            uom_found = 1
                            cant = float(summary_items[i]['lenght'])
                            cant_found = 1
                        else:
                            cant = 1
                    elif uom_found==1 and uom=="MTR" and summary_items[i]['lenght'] is not None:
                        cant = float(summary_items[i]['lenght'])
                        cant_found = 1
                    product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', product_code)])
                    if product_ids:
                        product_id = product_ids[0]
                        if uom_found==1:
                            if uom == "KGM" or uom2 == "KGM":
                                uom_id = 2
                            elif uom == 'MTR' or uom2 == 'MTR':
                                uom_id = 7
                            else:
                                uom_id = 1
                            self.pool.get('product.template').write(cr, uid, [product_id], {'uom_id': uom_id, 'uom_po_id': uom_id})
                    else:
                        if uom == "":
                            uom = uom2
                        product_id = self.alta_product(cr, uid, ids, product_code, product_name, uom)
                    break
        else:
            product_id = None    
        if unit.find('PackagingLevel') is not None:
            level = unit.find('PackagingLevel').text
        tracking_id = self.alta_tracking(cr, uid, ids, serial, level, tracking_parent)
        aux = 0
        for subelement in unit.getchildren():
            if subelement.tag=='Units':
                aux = 1
                for unit in subelement._children:
                    self.parsear_unit(cr, uid, ids, unit, picking_id, proveedor_id, summary_items, tracking_id)
            if subelement.tag=='Items':
                aux = 1
                for item in subelement._children:
                    self.parsear_item(cr, uid, ids, item, picking_id, proveedor_id, summary_items, tracking_id)
        if aux == 0 and aux_sid == 1:
            if uom == "":
                uom = uom2
            move_id = self.alta_move(cr, uid, ids, product_id, picking_id, serial, tracking_parent, cant, uom)
        elif aux==0 and aux_sid==0 and unit.find('CountOfTradeUnits') is not None and unit.find('ItemQuantity') is not None:
            cant = float(unit.find('CountOfTradeUnits').text)
            for i in range(len(summary_items)):
                if summary_items[i]['sid']==serial:
                    product_code = summary_items[i]['product_code']
                    level = int(summary_items[i]['level'])
                    product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', product_code)])
                    if product_ids:
                        product_id = product_ids[0]
                    else:
                        product_id = self.alta_product(cr, uid, ids, product_code)
                    break
            move_id = self.alta_move(cr, uid, ids, product_id, picking_id, serial, tracking_id, cant)   
        return False

    
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
        for node in tree.getiterator('SummaryItem'):        
        #for node in tree.iter('SummaryItem'):
            sid = node.attrib.get('SID')
#             psn = node.attrib.get('PSN')
            
            if node.find('ProducerProductCode') is not None:
                ProducerProductCode = node.find('ProducerProductCode').text
            if node.find('ProducerProductName') is not None:
                ProducerProductName = node.find('ProducerProductName').text
            else:
                ProducerProductName = None
#             if node.find('ItemQuantity') is not None:
#                 ItemQuantity = node.find('ItemQuantity').text
#             if node.find('CountOfTradeUnits') is not None:
#                 CountOfTradeUnits = node.find('CountOfTradeUnits').text
            if node.find('PackagingLevel') is not None:
                PackagingLevel = node.find('PackagingLevel').text
#             if node.find('ProductionDate') is not None:
#                 ProductionDate = node.find('ProductionDate').text
            if node.find('Length') is not None:
                Length = node.find('Length').text
            else:
                Length = None
            if node.find('NEW') is not None:
                Height = node.find('NEW').text
            else:
                Height = None
            if node.find('UnitOfMeasure') is not None:
                UnitOfMeasure = node.find('UnitOfMeasure').text
            else:
                UnitOfMeasure = None

            new_sum_item = {'sid': sid, 'product_code': ProducerProductCode, 'level': PackagingLevel, 'product_name': ProducerProductName, 'uom': UnitOfMeasure, 'height': Height, 'lenght': Length}
            summary_items.append(new_sum_item)
                        
        units = tree.find('Units')
        for unit in units._children:
            self.parsear_unit(cr, uid, ids, unit, picking_id, proveedor_id, summary_items)
                                     
        items_sueltos = tree.find('Items')
        if items_sueltos:
            for item_suelto in items_sueltos._children:
                self.parsear_item(cr, uid, ids, item_suelto, picking_id, proveedor_id, summary_items, None)
            
        
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
