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
import csv
import tempfile
import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pooler
import subprocess
import base64

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
        'obra_id': lambda self, cr, uid, c: self.pool.get('stock.location').search(cr, uid, [('obra', '=', True)])[0] if (self.pool.get('stock.location').search(cr, uid, [('obra', '=', True)])) else None,
        'dir_facul_id': lambda self, cr, uid, c: self.pool.get('iso.traza.dirfacul').search(cr, uid, [])[0] if (self.pool.get('iso.traza.dirfacul').search(cr, uid, [])) else None,
        'resp_explot_id': lambda self, cr, uid, c: self.pool.get('iso.traza.respexplot').search(cr, uid, [])[0] if (self.pool.get('iso.traza.respexplot').search(cr, uid, [])) else None,
        'delegacion_id': lambda self, cr, uid, c: self.pool.get('iso.traza.delegacion').search(cr, uid, [])[0] if (self.pool.get('iso.traza.delegacion').search(cr, uid, [])) else None,
        'subdelegacion_id': lambda self, cr, uid, c: self.pool.get('iso.traza.subdelegacion').search(cr, uid, [])[0] if (self.pool.get('iso.traza.subdelegacion').search(cr, uid, [])) else None,
        'area_id': lambda self, cr, uid, c: self.pool.get('iso.traza.area').search(cr, uid, [])[0] if (self.pool.get('iso.traza.area').search(cr, uid, [])) else None,
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['obra_id',  'date_from', 'date_to', 'delegacion_id', 'subdelegacion_id', 'area_id', 'dir_facul_id', 'resp_explot_id'])[0]
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'libro',
            'datas': data,
            }
        
    def _queda_en_deposito(self, cr, uid,  move_id):
        move_obj = pooler.get_pool(cr.dbname).get('stock.move')
        move_data = move_obj.browse(cr, uid, move_id)
        fecha = move_data.date_expected
        product_id = move_data.product_id.id
        cr.execute("""SELECT sum(product_qty) FROM (
                            (SELECT product_qty FROM (SELECT product_qty FROM stock_move WHERE (picking_id IS NOT NULL) AND (state='done') AND (product_id=%s) AND (date_expected<=%s)) AS cantidad)
                            UNION ALL
                            (SELECT -product_qty FROM (SELECT product_qty FROM stock_move WHERE (acta_id IS NOT NULL) AND (state='done') AND (product_id=%s) AND (date_expected<=%s)) AS cantidad)
                        ) AS total""", (product_id, fecha, product_id, fecha))
        return cr.fetchone()[0] or 0.0
        
    def _resumir(self, listado_original):
        lista = listado_original.split("//")
        if len(lista)<4:
            listado_resumido = listado_original
        else:
            serial_anterior = "0000000"
            aux = 0
            listado_resumido = ""
            for serial in lista:
#                 print lista
#                 print serial
#                 print serial_anterior
                if (int(serial[-6:])) == (int(serial_anterior[-6:]) + 1 ):
                    if aux==0:
                        listado_resumido = listado_resumido + "//" + " al "
                        aux = 1
                        serial_anterior = serial
                    elif aux>0:
                        serial_anterior = serial
                        aux = 1
                else:
                    if aux>0:
                        listado_resumido = listado_resumido + "//" + serial_anterior + "//" + "---" + "//" + serial
                        serial_anterior = serial
                        aux = 0
                    else:
                        if listado_resumido:
                            listado_resumido = listado_resumido + "//" + serial
                        else:
                            listado_resumido = serial
                        serial_anterior = serial
                        aux = 0
            if aux == 1:
                listado_resumido = listado_resumido + "//" + serial_anterior
        return listado_resumido
        
    def process_lines(self, cr, uid, ids, obra_id, date_from, date_to, resp_explot_id):
        if date_from:
            start = (datetime.strptime(date_from,"%Y-%m-%d")).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start = (datetime.strptime("2000-01-01","%Y-%m-%d")).strftime('%Y-%m-%d %H:%M:%S')
        if date_to:
            end = (datetime.strptime(date_to,"%Y-%m-%d") + relativedelta(hours=+23, minutes=+59, seconds=+59)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end = (datetime.now() + relativedelta(days=+1)).strftime('%Y-%m-%d %H:%M:%S')
        move_obj = pooler.get_pool(cr.dbname).get('stock.move')
        movimientos_con_obra = move_obj.search(cr, uid, [('location_dest_id','=',obra_id)])
        ubicaciones_destino_polv_obra = [obra_id]
        for movimiento_con_obra in movimientos_con_obra:
            p = move_obj.browse(cr, uid, movimiento_con_obra).location_id.id
            if p in ubicaciones_destino_polv_obra:
                continue
            else:
                ubicaciones_destino_polv_obra.append(p)
        movimientos_ids = move_obj.search(cr, uid, [('date_expected','<=',end),('date_expected','>=',start),('location_dest_id','in',ubicaciones_destino_polv_obra)], order='date_expected ,product_id, serial')
        m = []
        for movimiento_id in movimientos_ids:
            move = []
            move_data = move_obj.browse(cr, uid, movimiento_id)
            move.append(movimiento_id)
            move.append((datetime.strptime(move_data.date_expected,"%Y-%m-%d %H:%M:%S")).strftime('%d/%m/%Y'))
            if move_data.picking_id:
                move.append(move_data.picking_id.id)
            else:
                move.append("")
            if move_data.acta_id:
                move.append(move_data.acta_id.id)
            else:
                move.append("")
            move.append(move_data.product_id.name_template)
            move.append(move_data.product_qty)
            uom = move_data.product_uom.name
            if uom == "PCE":
                uom = "unid."
            move.append(uom)
            move.append(move_data.serial)
            move.append(move_data.location_id.id)
            move.append(move_data.location_dest_id.id)
            if move_data.tracking_id:
                move.append(move_data.tracking_id.id)
            else:
                move.append("")
            move.append(move_data.state)
            move.append(time.strptime(move[1],"%d/%m/%Y"))
            move.append(move_data.picking_id.num_guia or "")
            move.append(move_data.product_id.num_catalog or "")
            if move_data.acta_id:
                move.append(move_data.acta_id.resp_explot_id.dni or "")
            elif move_data.picking_id:
                move.append(move_data.picking_id.resp_explot_id.dni or "")
            else:
                move.append("")
            if move_data.acta_id:
                move.append(move_data.acta_id.artillero_id.cartilla or "")
            elif move_data.picking_id:
                move.append(move_data.picking_id.artillero_id.cartilla or "")
            else:
                move.append("")
            m.append(move)
            
        m.sort(key=lambda x: (x[12],x[2],x[3],x[4],x[7],-x[5]))
               
        lineas = []
        res = {}
        
        for move in m:
            if (not res) or (move[12]!=res['fecha']) or (move[4]!=res['product']) or (move[2]!=res['picking_id']) or (move[3]!=res['acta_id']): 
                if res:
                    res['lista_serials'] = self._resumir(res['lista_serials'])
                    res['lista_serials_sobrante'] = self._resumir(res['lista_serials_sobrante'])
                    if res['cant_consumida']>0.0:
                        res['tipo'] = "Entregado:"
                    else:
                        res['tipo'] = "Recibido:"
                    res['cant_consumida'] = res['cant_recibida_entregada'] - res['cant_sobrante']
                    res['cant_recibida_entregada'] = "{0:.2f}".format(res['cant_recibida_entregada'])
                    res['cant_consumida'] = "{0:.2f}".format(res['cant_consumida'])
                    res['cant_sobrante'] = "{0:.2f}".format(res['cant_sobrante'])
                    res['cant_queda'] = self._queda_en_deposito(cr, uid, res['move_id'])
                    res['cant_queda'] = "{0:.2f}".format(res['cant_queda'])
                    lineas.append(res)
#                     a = self._escribir_linea_anterior(lineas, res)
#                     lineas = a[0]
#                     res = a[1]
                res = {}
                res['fecha'] = move[12]
                res['product'] = move[4]
                res['picking_id'] = move[2]
                res['acta_id'] = move[3]
                res['serial'] = move[7]
                res['unidad'] = move[6]
                res['num_guia'] = move[13]
                res['num_catalog'] = move[14]
                res['resp_explot_id'] = move[15]
                res['artillero_id'] = move[16]
                res['lista_serials'] = ""
                res['lista_serials_sobrante'] = ""
                res['cant_recibida_entregada'] = 0
                res['cant_consumida'] = 0
                res['cant_sobrante'] = 0
                res['cant_queda'] = 0
                res['move_id'] = move[0]
                if res['picking_id']:
                    res['cant_recibida_entregada'] = move[5]
                    res['cant_consumida'] = 0
                    res['cant_sobrante'] = 0
                    res['lista_serials'] = move[7]
                    res['lista_serials_sobrante'] = ""
                elif res['acta_id']:
                    if move[5] > 0:
                        res['cant_recibida_entregada'] = move[5]
                        res['cant_consumida'] = move[5]
                        res['cant_sobrante'] = 0
                        res['lista_serials'] = move[7]
#                         res['lista_serials_sobrante'] = ""
                    elif move[5] < 0:
#                         res['cant_recibida_entregada'] = 0
#                         res['cant_consumida'] = 0
                        res['cant_sobrante'] = abs(move[5])
#                         res['lista_serials'] = ""
                        res['lista_serials_sobrante'] = move[7]
            else:
                res['serial'] = move[7]
                res['move_id'] = move[0]
                if res['picking_id']:
                    res['cant_recibida_entregada'] = res['cant_recibida_entregada'] + move[5]
                    res['cant_consumida'] = res['cant_consumida']
                    res['cant_sobrante'] = res['cant_sobrante']
                    res['lista_serials'] = res['lista_serials'] + "//" + move[7]
                    res['lista_serials_sobrante'] = res['lista_serials_sobrante']
                elif res['acta_id']:
                    if move[5] > 0:
                        res['cant_recibida_entregada'] = res['cant_recibida_entregada'] + move[5]
                        res['cant_consumida'] = res['cant_consumida'] + move[5]
                        res['cant_sobrante'] = res['cant_sobrante']
                        res['lista_serials'] = res['lista_serials'] + "//" + move[7]
#                         res['lista_serials_sobrante'] = res['lista_serials_sobrante']
                    elif move[5] < 0:
#                         res['cant_recibida_entregada'] = res['cant_recibida_entregada']
#                         res['cant_consumida'] = res['cant_consumida']
                        res['cant_sobrante'] = res['cant_sobrante'] + abs(move[5])
#                         res['lista_serials'] = res['lista_serials']
                        res['lista_serials_sobrante'] = res['lista_serials_sobrante'] + "//" + move[7]
        if res:
            if res['lista_serials']:
                res['lista_serials'] = self._resumir(res['lista_serials'])
            if res['lista_serials_sobrante']:
                res['lista_serials_sobrante'] = self._resumir(res['lista_serials_sobrante'])
            if res['cant_consumida']>0.0:
                res['tipo'] = "Entregado:"
            else:
                res['tipo'] = "Recibido:"
            res['cant_consumida'] = res['cant_recibida_entregada'] - res['cant_sobrante']
            res['cant_recibida_entregada'] = "{0:.2f}".format(res['cant_recibida_entregada'])
            res['cant_consumida'] = "{0:.2f}".format(res['cant_consumida'])
            res['cant_sobrante'] = "{0:.2f}".format(res['cant_sobrante'])
            res['cant_queda'] = self._queda_en_deposito(cr, uid, res['move_id'])
            res['cant_queda'] = "{0:.2f}".format(res['cant_queda'])
            lineas.append(res)
#             a = self._escribir_linea_anterior(lineas, res)
#             lineas = a[0]
#             res = a[1]
        return lineas
        
    def export_csv(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, ['obra_id',  'date_from', 'date_to', 'delegacion_id', 'subdelegacion_id', 'area_id', 'dir_facul_id', 'resp_explot_id'])[0]
        
        csv.register_dialect('nuevo_dialecto', delimiter=',')
        user_path =  os.path.expanduser('~')
        file_path = user_path + '/libro_registro.csv'
        #file_path = tempfile.gettempdir()+'/libro_registro.csv'
        csv_result = open(os.path.abspath(file_path), 'wb')
        writer_result = csv.writer(csv_result, dialect='nuevo_dialecto')
        
        str_result = ""
        lineas = self.process_lines(cr, uid, ids, data['obra_id'],data['date_from'],data['date_to'],data['resp_explot_id'])
        aux = 0
        for linea in lineas:
            if aux == 0:
                l = ['Obra','Delegación','Subdelegación','Área','Director Facultativo (nombre)','Director Facultativo (dni)','Director Facultativo (dirección)','Director Facultativo (teléfonos)',
                     'Responsable Explotación (nombre)','Responsable Explotación (dni)','Responsable Explotación (dirección)','Responsable Explotación (teléfonos)','Fecha','Nº Guía','Producto',
                     'Tipo','Cantidad Recibida/Entregada','Unidad','Nº Catalogación','identificación','Artillero','Cantidad Consumida','Unidad','Cantidad Sobrante','Unidad','identificación',
                     'Queda en Depósito','Unidad']
                l_new = []
                for l_item in l:
                    if isinstance(l_item, unicode):
                        l_item = l_item.encode('utf-8')
                        l_new.append(l_item)
                    elif not l_item:
                        l_new.append("")
                    elif not isinstance(l_item, str):
                        l_item = str(l_item)
                        l_new.append(l_item)
                    else:
                        l_new.append(l_item)
                aux +=1
            else:
                linea['fecha'] = time.strftime('%d-%m-%Y',linea['fecha'])
                linea['acta_id'] = str(linea['acta_id'])
                linea['move_id'] = str(linea['move_id'])
                linea['obra'] = pooler.get_pool(cr.dbname).get('stock.location').read(cr, uid, data['obra_id'], ['name'])['name'] if data['obra_id'] else ''
                linea['delegacion'] = pooler.get_pool(cr.dbname).get('iso.traza.delegacion').read(cr, uid, data['delegacion_id'], ['name'])['name'] if data['delegacion_id'] else ''
                linea['subdelegacion'] = pooler.get_pool(cr.dbname).get('iso.traza.subdelegacion').read(cr, uid, data['subdelegacion_id'], ['name'])['name'] if data['subdelegacion_id'] else ''
                linea['area'] = pooler.get_pool(cr.dbname).get('iso.traza.area').read(cr, uid, data['area_id'], ['name'])['name'] if data['area_id'] else ''
                linea['dir_facul_name'] = pooler.get_pool(cr.dbname).get('iso.traza.dirfacul').read(cr, uid, data['dir_facul_id'], ['name'])['name'] if data['dir_facul_id'] else ''
                linea['dir_facul_dni'] = pooler.get_pool(cr.dbname).get('iso.traza.dirfacul').read(cr, uid, data['dir_facul_id'], ['dni'])['dni'] if data['dir_facul_id'] else ''
                linea['dir_facul_direccion'] = pooler.get_pool(cr.dbname).get('iso.traza.dirfacul').read(cr, uid, data['dir_facul_id'], ['direccion'])['direccion'] if data['dir_facul_id'] else ''
                linea['dir_facul_telefonos'] = pooler.get_pool(cr.dbname).get('iso.traza.dirfacul').read(cr, uid, data['dir_facul_id'], ['telefonos'])['telefonos'] if data['dir_facul_id'] else ''
                linea['resp_explot_name'] = pooler.get_pool(cr.dbname).get('iso.traza.respexplot').read(cr, uid, data['resp_explot_id'], ['name'])['name'] if data['resp_explot_id'] else ''
                linea['resp_explot_dni'] = pooler.get_pool(cr.dbname).get('iso.traza.respexplot').read(cr, uid, data['resp_explot_id'], ['dni'])['dni'] if data['resp_explot_id'] else ''
                linea['resp_explot_direccion'] = pooler.get_pool(cr.dbname).get('iso.traza.respexplot').read(cr, uid, data['resp_explot_id'], ['direccion'])['direccion'] if data['resp_explot_id'] else ''
                linea['resp_explot_telefonos'] = pooler.get_pool(cr.dbname).get('iso.traza.respexplot').read(cr, uid, data['resp_explot_id'], ['telefonos'])['telefonos'] if data['resp_explot_id'] else ''
                
                l = [linea['obra'],linea['delegacion'],linea['subdelegacion'],linea['area'],linea['dir_facul_name'],linea['dir_facul_dni'],linea['dir_facul_direccion'],linea['dir_facul_telefonos'],
                     linea['resp_explot_name'],linea['resp_explot_dni'],linea['resp_explot_direccion'],linea['resp_explot_telefonos'],linea['fecha'],linea['num_guia'],linea['product'],
                     linea['tipo'],linea['cant_recibida_entregada'],linea['unidad'],linea['num_catalog'],linea['lista_serials'],linea['artillero_id'],linea['cant_consumida'],linea['unidad'],
                     linea['cant_sobrante'],linea['unidad'],linea['lista_serials_sobrante'],linea['cant_queda'],linea['unidad']]
                l_new = []
                for l_item in l:
                    if isinstance(l_item, unicode):
                        l_item = l_item.encode('utf-8')
                        l_new.append(l_item)
                    elif not l_item:
                        l_new.append("")
                    elif not isinstance(l_item, str):
                        l_item = str(l_item)
                        l_new.append(l_item)
                    else:
                        l_new.append(l_item)
                        
            writer_result.writerow(l_new)
            str_result = str_result +  ', '.join(l_new) + '\n'
            
        csv_result.close()
        
        #crear libro y adjuntarle csv
        vals={
            "date_inicio": data['date_from'],
            "date_fin": data['date_to'],
            'name': "/",
            'dir_facul_id': data['dir_facul_id'],
            'resp_explot_id': data['resp_explot_id'],
            'obra_id': data['obra_id'],
        }
        
        libro_id = self.pool.get('iso.traza.libro').create(cr,uid,vals,context)
        
        data_attach = {
                'name': 'libro_registro.csv',
                'datas': base64.b64encode(str_result),
                'datas_fname': 'libro_registro.csv',
                'description': 'libro_registro.csv',
                'res_model': 'iso.traza.libro',
                'res_id': libro_id,
            }
        self.pool.get('ir.attachment').create(cr, uid, data_attach)
        
#         os.chmod(file_path, 0777)
        #subprocess.call(os.path.abspath(file_path))
#         subprocess.Popen(os.path.abspath(file_path), shell=True)

#         obj_model = self.pool.get('ir.model.data')
#         model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','iso_traza_libro_view_tree')])
#         resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        
        return {
            'res_id': libro_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'iso.traza.libro',
            'type': 'ir.actions.act_window',
            }

iso_traza_libro_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: