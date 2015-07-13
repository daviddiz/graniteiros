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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pooler
from report import report_sxw

class libro(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(libro, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process_lines':self.process_lines,
        })
        
    def _resumir(self, listado_original):
        lista = listado_original.split("\n")
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
                        listado_resumido = listado_resumido + "\n" + "          al"
                        aux = 1
                        serial_anterior = serial
                    elif aux>0:
                        serial_anterior = serial
                        aux = 1
                else:
                    if aux>0:
                        listado_resumido = listado_resumido + "\n" + serial_anterior + "\n" + "    ----------------" + "\n" + serial
                        serial_anterior = serial
                        aux = 0
                    else:
                        listado_resumido = serial
                        serial_anterior = serial
                        aux = 0
            if aux == 1:
                listado_resumido = listado_resumido + "\n" + serial_anterior
        return listado_resumido
        
#     def _escribir_linea_anterior(self, lineas, res):
#         
#         lineas.append(res)
#         return (lineas, res)
        
    def process_lines(self, obra_id, date_from, date_to, resp_explot_id):
        if date_from:
            start = (datetime.strptime(date_from,"%Y-%m-%d")).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start = (datetime.strptime("2000-01-01","%Y-%m-%d")).strftime('%Y-%m-%d %H:%M:%S')
        if date_to:
            end = (datetime.strptime(date_to,"%Y-%m-%d") + relativedelta(hours=+23, minutes=+59, seconds=+59)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end = (datetime.now() + relativedelta(days=+1)).strftime('%Y-%m-%d %H:%M:%S')
        move_obj = pooler.get_pool(self.cr.dbname).get('stock.move')
        movimientos_con_obra = move_obj.search(self.cr, self.uid, [('location_dest_id','=',obra_id)])
        ubicaciones_destino_polv_obra = [obra_id]
        for movimiento_con_obra in movimientos_con_obra:
            p = move_obj.browse(self.cr, self.uid, movimiento_con_obra).location_id.id
            if p in ubicaciones_destino_polv_obra:
                continue
            else:
                ubicaciones_destino_polv_obra.append(p)
        movimientos_ids = move_obj.search(self.cr, self.uid, [('date_expected','<=',end),('date_expected','>=',start),('location_dest_id','in',ubicaciones_destino_polv_obra)], order='date_expected ,product_id, serial')
        m = []
        for movimiento_id in movimientos_ids:
            move = []
            move_data = move_obj.browse(self.cr, self.uid, movimiento_id)
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
            move.append(move_data.picking_id.num_catalog or "")
            if move_data.acta_id:
                move.append(move_data.acta_id.resp_explot_id.dni or "")
            else:
                move.append(move_data.picking_id.resp_explot_id.dni or "")
            if move_data.acta_id:
                move.append(move_data.acta_id.artillero_id.cartilla or "")
            else:
                move.append(move_data.picking_id.artillero_id.cartilla or "")
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
                    res['cant_recibida_entregada'] = "{:.2f}".format(res['cant_recibida_entregada'])
                    res['cant_consumida'] = "{:.2f}".format(res['cant_consumida'])
                    res['cant_sobrante'] = "{:.2f}".format(res['cant_sobrante'])
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
                if res['picking_id']:
                    res['cant_recibida_entregada'] = res['cant_recibida_entregada'] + move[5]
                    res['cant_consumida'] = res['cant_consumida']
                    res['cant_sobrante'] = res['cant_sobrante']
                    res['lista_serials'] = res['lista_serials'] + "\n" + move[7]
                    res['lista_serials_sobrante'] = res['lista_serials_sobrante']
                elif res['acta_id']:
                    if move[5] > 0:
                        res['cant_recibida_entregada'] = res['cant_recibida_entregada'] + move[5]
                        res['cant_consumida'] = res['cant_consumida'] + move[5]
                        res['cant_sobrante'] = res['cant_sobrante']
                        res['lista_serials'] = res['lista_serials'] + "\n" + move[7]
#                         res['lista_serials_sobrante'] = res['lista_serials_sobrante']
                    elif move[5] < 0:
#                         res['cant_recibida_entregada'] = res['cant_recibida_entregada']
#                         res['cant_consumida'] = res['cant_consumida']
                        res['cant_sobrante'] = res['cant_sobrante'] + abs(move[5])
#                         res['lista_serials'] = res['lista_serials']
                        res['lista_serials_sobrante'] = res['lista_serials_sobrante'] + "\n" + move[7]
        if res:
#             if res['lista_serials']:
#                 res['lista_serials'] = self._resumir(res[i'lista_serials'])
#             if res['lista_serials_sobrante']:
#                 res['lista_serials_sobrante'] = self._resumir(res['lista_serials_sobrante'])
            if res['cant_consumida']>0.0:
                res['tipo'] = "Entregado:"
            else:
                res['tipo'] = "Recibido:"
            res['cant_consumida'] = res['cant_recibida_entregada'] - res['cant_sobrante']
            res['cant_recibida_entregada'] = "{:.2f}".format(res['cant_recibida_entregada'])
            res['cant_consumida'] = "{:.2f}".format(res['cant_consumida'])
            res['cant_sobrante'] = "{:.2f}".format(res['cant_sobrante'])
            lineas.append(res)
#             a = self._escribir_linea_anterior(lineas, res)
#             lineas = a[0]
#             res = a[1]
        return lineas

report_sxw.report_sxw('report.libro', 'iso.traza.libro.report', 'addons/iso_traza/report/libro.rml', parser=libro, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

