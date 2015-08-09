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
import pooler
from report import report_sxw

class acta(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(acta, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'process':self.process,
        })
        
    def _arreglar_serials(self,serials):
        return serials
        
    def process(self,moves_ids):
#         acta_obj = pooler.get_pool(self.cr.dbname).get('iso.traza.acta')
#         move_obj = pooler.get_pool(self.cr.dbname).get('stock.move')
#         moves_id = move_obj.search(self.cr,self.uid, [('acta_id', '=', acta_id)])

        movimientos = []
        for move_id in moves_ids:
            m = {}
            m['nombre'] = move_id.product_id.name
            m['serial'] = move_id.serial
            m['cantidad'] = move_id.product_qty
            m['unidad'] = move_id.product_uom.name
            movimientos.append(m)
        movimientos.sort(key=lambda d:(d['nombre'],d['serial']))

        nombre = ""
        aux = 0
        cant_sobrante = 0.00
        serial_anterior = 0
        lineas = []
        data = {}
        #serials = ""
        for movimiento in movimientos:
            #si cambia el producto, nueva línea y nuevo recuento
            if nombre <> movimiento['nombre']:
                if data:
                    #antes de nada escribo el resultado del recuento del producto anterior
                    #data['serial'] = self._arreglar_serials(serials)
                    if aux==2 and serial_anterior:
                        data['serial'] = data['serial'] + "\n" + serial_anterior
                    data['entregado'] = "{0:.2f}".format(data['entregado'])
                    data['consumido'] = "{0:.2f}".format(data['consumido'])
                    lineas.append(data)
                    data = {}
                aux = 0
                cant_sobrante = 0.00
                nombre = movimiento['nombre']
                data['nombre'] = movimiento['nombre']
                data['unidad'] = movimiento['unidad']
                data['entregado'] = 0.00
                data['sobrante'] = ""
                if movimiento['cantidad']>0:
                    data['entregado'] = movimiento['cantidad']
                    data['serial'] = movimiento['serial']
                    serial_anterior = movimiento['serial']
                elif movimiento['cantidad']<0:
                    cant_sobrante = abs(movimiento['cantidad'])
                    if data['sobrante']=="":
                        data['sobrante'] = "{0:.2f}".format(abs(movimiento['cantidad'])) + "\n" + movimiento['serial']
                    else: 
                        data['sobrante'] = data['sobrante'] + "\n" + "{0:.2f}".format(abs(movimiento['cantidad'])) + "\n" + movimiento['serial']
                data['consumido'] = data['entregado'] - cant_sobrante  
                data['consumido'] = abs(data['consumido'])
            else:
                if movimiento['cantidad']<0:
                    cant_sobrante = cant_sobrante + abs(movimiento['cantidad'])
                    if data['sobrante']=="":
                        data['sobrante'] = "{0:.2f}".format(abs(movimiento['cantidad'])) + "\n" + movimiento['serial']
                    else:
                        data['sobrante'] = data['sobrante'] + "\n" + "{0:.2f}".format(abs(movimiento['cantidad'])) + "\n" + movimiento['serial']
                elif movimiento['cantidad']>0:
                    data['entregado'] = data['entregado'] + movimiento['cantidad']
                    if int(movimiento['serial'][-6:]) == ( int(serial_anterior[-6:]) + 1 ):
                        if aux==0:
                            data['serial'] = data['serial'] + "\n" + "          al"
                            aux = 2
                            serial_anterior = movimiento['serial']
                        elif aux>0:
                            serial_anterior = movimiento['serial']
                            aux = 2
                    else:
                        if aux>0:
                            data['serial'] = data['serial'] + "\n" + serial_anterior + "\n" + "    ----------------" + "\n" + movimiento['serial']
                            serial_anterior = movimiento['serial']
                            aux = 0
                        else:
                            data['serial'] = movimiento['serial']
                            serial_anterior = movimiento['serial']
                            aux = 0
                
                data['consumido'] = data['entregado'] - cant_sobrante
                data['consumido'] = abs(data['consumido'])
        #antes de nada escribo el resultado del recuento del último producto
        if aux==2 and serial_anterior:
            data['serial'] = data['serial'] + "\n" + serial_anterior
        data['entregado'] = "{0:.2f}".format(data['entregado'])
        data['consumido'] = "{0:.2f}".format(data['consumido'])
        lineas.append(data)
        return lineas

report_sxw.report_sxw('report.acta', 'iso.traza.acta', 'addons/iso_traza/report/acta.rml', parser=acta, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

