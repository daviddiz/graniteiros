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
                elif node[i].tag == "NEW":
                    NEW = node[i].text
            
        f.close()
        
        f = open(file_path,'r')
        tree = ElementTree.parse(f)
        
        for node in tree.iter('Item'):
            
            uid = node.attrib.get('UID')
            sid = node.attrib.get('SID')
            psn = node.attrib.get('PSN')
            
        f.close()
        
        os.remove(f)
        


#         book = xlrd.open_workbook(file_contents=s)
#         
#         data = {
#                 'origin': self.browse(cr,uid,ids)[0].origin,
#                 'type': 'in',
#                 }
#         picking_id = self.pool.get('stock.picking').create(cr, uid, data)      
#         
#         for s in book.sheets():
#             end = s.nrows - 1
#             model = s.cell(9,4).value
#             #comienzo de las lineas de detalle : row
#             #intento de encontrar esa linea:
#             row = self._start_line(cr, uid, s)
#             while row <= end:
#                 if (row + 1 == s.nrows) or (s.cell(row+1,6).value=="" and s.cell(row+2,6).value==""):
#                     end = row
#                 color = s.cell(row,5).value
#                 if s.cell(row,7).value<>"":
#                     a = s.cell(14,7).value.find(".")
#                     talla = s.cell(14,7).value[a+1:]
#                     qty = s.cell(row,12).value
#                 elif s.cell(row,8).value<>"":
#                     a = s.cell(14,8).value.find(".")
#                     talla = s.cell(14,8).value[a+1:]
#                     qty = s.cell(row,12).value
#                 elif s.cell(row,9).value<>"":
#                     a = s.cell(14,9).value.find(".")
#                     talla = s.cell(14,9).value[a+1:]
#                     qty = s.cell(row,12).value
#                 elif s.cell(row,10).value<>"":
#                     a = s.cell(14,10).value.find(".")
#                     talla = s.cell(14,10).value[a+1:]
#                     qty = s.cell(row,12).value
#                 ref = model+"-"+color+"-"+talla
#                 
#                 result = self.pool.get('product.product').search(cr,uid,[('default_code','=',ref)])
#                 if result:
#                     product_id = result[0]
#                 else:
#                     val = {
#                            'name': ref,
#                            }
#                     product_template_id = self.pool.get('product.template').create(cr, uid, val)
#                     
#                     val1 = {
#                            'product_tmpl_id': product_template_id,
#                            'default_code': ref,
#                            'name_template': ref,
#                            }
#                     product_id = self.pool.get('product.product').create(cr, uid, val1)
#                 
#                 data1 = {
#                          'origin': self.browse(cr,uid,ids)[0].origin,
#                          'location_id': loc,
#                          'location_dest_id': loc_dest,
#                          'product_id': product_id,
#                          'picking_id': picking_id,
#                          'product_uom': 1,
#                          'product_uos_qty': qty,
#                          'product_qty': qty,
#                          'name': ref,
#                          }    
#                 move_id = self.pool.get('stock.move').create(cr, uid, data1)
#                 row += 1
# 
#         return {
#                 'domain': "[('id','=',%s)]" % (picking_id),
#                 'view_type': 'form',
#                 'view_mode': 'tree,form',
#                 'res_model': 'stock.picking',
#                 'view_id': False,
#                 'type': 'ir.actions.act_window',
#         }

iso_traza_import_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: