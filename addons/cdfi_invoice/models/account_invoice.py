# -*- coding: utf-8 -*-

import base64
import json
import requests
import datetime
import os
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, Warning
from lxml import etree as ET2
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
from . import amount_to_text_es_MX
import pytz

import logging

_logger = logging.getLogger(__name__)
NSMAP = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'cfdi': 'http://www.sat.gob.mx/cfd/3', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}

class AccountMove(models.Model):
    _inherit = 'account.move'

    factura_cfdi = fields.Boolean('Factura CFDI')
    tipo_comprobante = fields.Selection(
        selection=[('I', 'Ingreso'),
                   ('E', 'Egreso'),
                   ('T', 'Traslado'), ],
        string=_('Tipo de comprobante'),
    )
    forma_pago = fields.Selection(
        selection=[('01', '01 - Efectivo'),
                   ('02', '02 - Cheque nominativo'),
                   ('03', '03 - Transferencia electrónica de fondos'),
                   ('04', '04 - Tarjeta de Crédito'),
                   ('05', '05 - Monedero electrónico'),
                   ('06', '06 - Dinero electrónico'),
                   ('08', '08 - Vales de despensa'),
                   ('12', '12 - Dación en pago'),
                   ('13', '13 - Pago por subrogación'),
                   ('14', '14 - Pago por consignación'),
                   ('15', '15 - Condonación'),
                   ('17', '17 - Compensación'),
                   ('23', '23 - Novación'),
                   ('24', '24 - Confusión'),
                   ('25', '25 - Remisión de deuda'),
                   ('26', '26 - Prescripción o caducidad'),
                   ('27', '27 - A satisfacción del acreedor'),
                   ('28', '28 - Tarjeta de débito'),
                   ('29', '29 - Tarjeta de servicios'),
                   ('30', '30 - Aplicación de anticipos'),
                   ('31', '31 - Intermediario pagos'),
                   ('99', '99 - Por definir'), ],
        string=_('Forma de pago'),
    )
    methodo_pago = fields.Selection(
        selection=[('PUE', _('Pago en una sola exhibición')),
                   ('PPD', _('Pago en parcialidades o diferido'))],
        string=_('Método de pago'), default='PUE'
    )
    uso_cfdi = fields.Selection(
        selection=[('G01', _('Adquisición de mercancías')),
                   ('G02', _('Devoluciones, descuentos o bonificaciones')),
                   ('G03', _('Gastos en general')),
                   ('I01', _('Construcciones')),
                   ('I02', _('Mobiliario y equipo de oficina por inversiones')),
                   ('I03', _('Equipo de transporte')),
                   ('I04', _('Equipo de cómputo y accesorios')),
                   ('I05', _('Dados, troqueles, moldes, matrices y herramental')),
                   ('I06', _('Comunicacion telefónica')),
                   ('I07', _('Comunicación Satelital')),
                   ('I08', _('Otra maquinaria y equipo')),
                   ('D01', _('Honorarios médicos, dentales y gastos hospitalarios')),
                   ('D02', _('Gastos médicos por incapacidad o discapacidad')),
                   ('D03', _('Gastos funerales')),
                   ('D04', _('Donativos')),
                   ('D07', _('Primas por seguros de gastos médicos')),
                   ('D08', _('Gastos de transportación escolar obligatoria')),
                   ('D10', _('Pagos por servicios educativos (colegiaturas)')),
                   ('P01', _('Por definir')), ],
        string=_('Uso CFDI (cliente)'),
    )
    xml_invoice_link = fields.Char(string=_('XML Invoice Link'))
    estado_factura = fields.Selection(
        selection=[('factura_no_generada', 'Factura no generada'), ('factura_correcta', 'Factura correcta'),
                   ('solicitud_cancelar', 'Cancelación en proceso'), ('factura_cancelada', 'Factura cancelada'),
                   ('solicitud_rechazada', 'Cancelación rechazada'), ],
        string=_('Estado de factura'),
        default='factura_no_generada',
        readonly=True
    )
    #pdf_cdfi_invoice = fields.Binary("CDFI Invoice pdf")
    #xml_cdfi_invoice = fields.Binary("CDFI Invoice xml")
    #cdfi_invoice_name = fields.Char("CDFI Invoice")
    cfdi_xml = fields.Many2one("ir.attachment", string="CFDI xml",copy=False)
    qrcode_image = fields.Binary("QRCode",copy=False)
    numero_cetificado = fields.Char(string=_('Numero de cetificado'))
    cetificaso_sat = fields.Char(string=_('Cetificao SAT'),copy=False)
    folio_fiscal = fields.Char(string=_('Folio Fiscal'), readonly=True)
    fecha_certificacion = fields.Char(string=_('Fecha y Hora Certificación'))
    cadena_origenal = fields.Char(string=_('Cadena Origenal del Complemento digital de SAT'))
    selo_digital_cdfi = fields.Char(string=_('Selo Digital del CDFI'))
    selo_sat = fields.Char(string=_('Selo del SAT'),copy=False)
    moneda = fields.Char(string=_('Moneda'))
    tipocambio = fields.Char(string=_('TipoCambio'))
    folio = fields.Char(string=_('Folio'))
    version = fields.Char(string=_('Version'))
    number_folio = fields.Char(string=_('Folio'), compute='_get_number_folio')
    amount_to_text = fields.Char('Amount to Text', compute='_get_amount_to_text',
                                 size=256,
                                 help='Amount of the invoice in letter')
    qr_value = fields.Char(string=_('QR Code Value'),copy=False)
    invoice_datetime = fields.Char(string=_('11/12/17 12:34:12'))
    fecha_factura = fields.Datetime(string=_('Fecha Factura'), readonly=True)
    rfc_emisor = fields.Char(string=_('RFC'),copy=False)
    name_emisor = fields.Char(string=_('Name'),copy=False)
    serie_emisor = fields.Char(string=_('A'))
    tipo_relacion = fields.Selection(
        selection=[('01', 'Nota de crédito de los documentos relacionados'),
                   ('02', 'Nota de débito de los documentos relacionados'),
                   ('03', 'Devolución de mercancía sobre facturas o traslados previos'),
                   ('04', 'Sustitución de los CFDI previos'),
                   ('05', 'Traslados de mercancías facturados previamente'),
                   ('06', 'Factura generada por los traslados previos'),
                   ('07', 'CFDI por aplicación de anticipo'), ],
        string=_('Tipo relación'),
    )
    uuid_relacionado = fields.Char(string=_('CFDI Relacionado'),copy=False)
    confirmacion = fields.Char(string=_('Confirmación'),copy=False)
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Product Price'))
    monto = fields.Float(string='Amount', digits=dp.get_precision('Product Price'))
    precio_unitario = fields.Float(string='Precio unitario', digits=dp.get_precision('Product Price'))
    monto_impuesto = fields.Float(string='Monto impuesto', digits=dp.get_precision('Product Price'))
    total_impuesto = fields.Float(string='Monto impuesto', digits=dp.get_precision('Product Price'))
    decimales = fields.Float(string='decimales')
    desc = fields.Float(string='descuento', digits=dp.get_precision('Product Price'))
    subtotal = fields.Float(string='subtotal', digits=dp.get_precision('Product Price'))
    total = fields.Float(string='total', digits=dp.get_precision('Product Price'))

    debug_xml = fields.Text('Debug XML', readonly=True, copy=False)
    usuario_timbrado = fields.Many2one('res.users', 'Timbrado por', readonly=True, copy=False)
    fecha_timbrado = fields.Char('Fecha de Timbrado', readonly=True, copy=False)
    certificado_emisor = fields.Char('Certificador emisor', readonly=True, copy=False)
    lugar_expedicion = fields.Char('Lugar de expedición', readonly=True, copy=False)
    cad_org_tfd = fields.Char('Cadena Original TFD', readonly=True, copy=False)

    invoice_date_timbrar = fields.Datetime('Fecha a timbrar', default=fields.Datetime.now())
    invoice_date = fields.Date('Fecha de Creacion', default=datetime.date.today())



    @api.model
    def _reverse_move_vals(self, default_values, cancel=True):
        values = super(AccountMove, self)._reverse_move_vals(default_values, cancel)
        if self.estado_factura == 'factura_correcta':
            values['uuid_relacionado'] = self.folio_fiscal
            values['methodo_pago'] = self.methodo_pago
            values['forma_pago'] = self.forma_pago
            values['tipo_comprobante'] = 'E'
            values['uso_cfdi'] = 'G02'
            values['tipo_relacion'] = '01'
            values['fecha_factura'] = None
        return values

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if self.estado_factura == 'factura_correcta' or self.estado_factura == 'factura_cancelada':
            default['estado_factura'] = 'factura_no_generada'
            default['folio_fiscal'] = ''
            default['fecha_factura'] = None
            default['factura_cfdi'] = False
        return super(AccountMove, self).copy(default=default)

    @api.depends('name')
    def _get_number_folio(self):
        for record in self:
            if record.name:
                record.number_folio = record.name.replace('INV', '').replace('/', '')

    @api.depends('amount_total', 'currency_id')
    def _get_amount_to_text(self):
        for record in self:
            record.amount_to_text = amount_to_text_es_MX.get_amount_to_text(record, record.amount_total, 'es_cheque',
                                                                            record.currency_id.name)

    @api.model
    def _get_amount_2_text(self, amount_total):
        return amount_to_text_es_MX.get_amount_to_text(self, amount_total, 'es_cheque', self.currency_id.name)

    @api.onchange('partner_id')
    def _get_uso_cfdi(self):
        if self.partner_id:
            values = {
                'uso_cfdi': self.partner_id.uso_cfdi
            }
            self.update(values)

    @api.onchange('invoice_payment_term_id')
    def _get_metodo_pago(self):
        if self.invoice_payment_term_id:
            if self.invoice_payment_term_id.methodo_pago == 'PPD':
                values = {
                    'methodo_pago': self.invoice_payment_term_id.methodo_pago,
                    'forma_pago': '99'
                }
            else:
                values = {
                    'methodo_pago': self.invoice_payment_term_id.methodo_pago,
                    'forma_pago': False
                }
        else:
            values = {
                'methodo_pago': False,
                'forma_pago': False
            }
        self.update(values)

    def validations(self):
        warning = u""
        if not self.env.user.tz or self.env.user.tz == "":
            warning = warning + u"El usuario debe tener configurada la zona horaria para poder timbrar. Para configurarla:\n" \
                                u"Clic en su nombre (parte superior derecha).\n" \
                                u"Clic en preferencias.\n" \
                                u"Seleccionar la zona horaria que se debe utilizar, ejemplo: America/Mexico_City.\n\n"
        if not self.env.user.company_id or len(self.env.user.company_id) != 1:
            warning = warning + u"El usuario deber tener asociada la sucursal sobre la que factura.\n\n"
        if not self.user_id.company_id.zip or self.user_id.company_id.zip == "":
            warning = warning + u"La dirección de la sucursal debe tener un código postal.\n\n"
        if not self.company_id.vat or (len(self.company_id.vat) != 13 and len(self.company_id.vat) != 12):
            warning = warning + u"El RFC del emisor parece ser invalido.\n\n"
        if not self.partner_id.vat or (len(self.partner_id.vat) != 13 and len(self.partner_id.vat) != 12):
            warning = warning + u"El RFC del receptor parece ser invalido.\n\n"
        if not self.tipo_comprobante or self.tipo_comprobante == "":
            warning = warning + u"El tipo de comprobante no fue fijado correctamente.\n\n"
        if not self.forma_pago or len(self.forma_pago) == 0:
            warning = warning + u"Debe seleccionar la forma de pago.\n\n"
        if not self.methodo_pago or len(self.methodo_pago) == 0:
            warning = warning + u"Debe seleccionar el metodo de pago.\n\n"
        if len(self.uso_cfdi) == 0:
            warning = warning + u"Debe seleccionar el uso de que dará el cliente al CFDI.\n\n"
        if fields.Datetime.from_string(self.invoice_date_timbrar) < datetime.datetime.now() - datetime.timedelta(days=3):
            warning = warning + u"No puedes timbrar una factura con fecha anterior a hace tres dias.\n\n"
        if fields.Datetime.from_string(self.invoice_date_timbrar) > datetime.datetime.now():
            warning = warning + u"No puedes timbrar una factura con fecha posterior a el ahora.\n\n"
        if warning != "":
            raise Warning(warning)

    @api.model
    def to_json(self):
        self.validations()
        comprobante = {}
        timezone = self._context.get('tz')
        if not timezone:
            timezone = self.journal_id.tz or self.env.user.partner_id.tz or 'America/Mexico_City'
        local = pytz.timezone(timezone)
        fecha_factura = fields.Datetime.from_string(self.invoice_date_timbrar).replace(tzinfo=pytz.utc).astimezone(local)
        date_from = fecha_factura.strftime("%Y-%m-%dT%H:%M:%S")
        comprobante['Prueba'] = self.env.user.company_id.modo_prueba
        comprobante['TipoCFDI'] = 'invoice'
        comprobante['Folio'] = self.name.replace('INV', '').replace('/', '')
        comprobante['Fecha'] = date_from
        comprobante['Serie'] = self.company_id.serie_factura or self.journal_id.serie_diario or 'A'
        comprobante['NoCertificado'] = self.env.user.company_id.pac_config.no_cer
        comprobante['Certificado'] = self.env.user.company_id.pac_config.cer.decode()
        comprobante['Moneda'] = self.currency_id.name or ''
        comprobante['TipoCambio'] = '%.2f' % self.currency_id.rate if self.currency_id.name != "MXN" else '1'
        comprobante['TipoDeComprobante'] = self.tipo_comprobante or ''
        comprobante['FormaPago'] = self.forma_pago
        comprobante['MetodoPago'] = self.methodo_pago
        comprobante['LugarExpedicion'] = self.env.user.company_id.zip or ''
        if self.tipo_relacion and len(self.tipo_relacion) > 0:
            cfdi_relacionados = {}
            cfdi_relacionados['TipoRelacion'] = self.tipo_relacion
            cfdi_relacionados['UUID'] = self.uuid_relacionado.split(',')
            comprobante['CfdiRelacionado'] = cfdi_relacionados
        emisor = {}
        emisor['Rfc'] = self.company_id.vat or ''
        emisor['Nombre'] = self.company_id.nombre_fiscal or ''
        emisor['RegimenFiscal'] = self.company_id.regimen_fiscal or ''
        comprobante['Emisor'] = emisor
        receptor = {}
        receptor['Rfc'] = self.partner_id.vat or ''
        receptor['Nombre'] =self.partner_id.name or ''
        receptor['UsoCFDI'] = self.uso_cfdi
        comprobante['Receptor'] = receptor
        conceptos = []

        for l in self.invoice_line_ids:
            concepto = {}
            importe = self.currency_id.round(l.quantity * max(l.price_unit,0.01))
            concepto['ClaveProdServ'] = l.product_id.clave_producto or ''
            concepto['ClaveUnidad']= l.product_id.clave_unidad or ''
            concepto['Unidad'] = l.product_id.unidad_medida or ''
            concepto['NoIdentificacion'] = l.product_id.default_code or l.product_id.clave_producto or ''
            concepto['Cantidad'] = '%.2f' % l.quantity
            concepto['Descripcion'] = l.name or ''
            #descuento = (l.discount * l.quantity * l.price_unit) / 100.0
            concepto['Descuento'] = ('%.2f' % l.discount)
            concepto['ValorUnitario'] = ('%.2f' % max(l.price_unit,0.01))
            concepto['Importe'] = ('%.2f' % importe)
            impuetos = []
            for i in l.tax_ids:
                name = 'IVA' if 'IVA' in i.description.upper() else 'ISR' if 'ISR' in i.description.upper() else ''
                name = ('R_' + name) if i.amount<0 else name
                _logger.warning(name)
                impuetos.append({'Code':i.impuesto,'Nombre':name,'Id':i.id,'Valor':i.amount,'Tipo':i.tipo_factor if i.tipo_factor else 'Tasa'})
            concepto['Impuestos'] = impuetos
            conceptos.append(concepto)

        comprobante['Conceptos'] = conceptos

        pas = self.encode(self.env.user.company_id.pac_config.user,self.env.user.company_id.pac_config.contrasena)
        comprobante['Sellos'] = {}
        comprobante['Sellos']['Password'] = pas
        comprobante['Sellos']['Key'] = self.env.user.company_id.pac_config.key.decode()
        return comprobante

    def action_cfdi_generate(self):
        # after validate, send invoice data to external system via http post
        for invoice in self:
            if invoice.fecha_factura == False:
                invoice.fecha_factura = datetime.datetime.now()
                invoice.write({'fecha_factura': invoice.fecha_factura})
            if invoice.estado_factura == 'factura_correcta':
                if invoice.folio_fiscal:
                    invoice.write({'factura_cfdi': True})
                    return True
                else:
                    raise UserError(_('Error para timbrar factura, Factura ya generada.'))
            if invoice.estado_factura == 'factura_cancelada':
                raise UserError(_('Error para timbrar factura, Factura ya generada y cancelada.'))

            values = invoice.to_json()
            pacs = self.env.user.company_id.pac_config
            if len(pacs) > 0:
                pac=pacs[0]
                result = pac.timbrar_xml(values)
                if result['validate']:
                    xml_signed = ""
                    if 'xml' in result:
                        xml_signed = base64.b64decode(result['xml'])
                    else:
                        raise Warning("No se recibio el elemento 'xml' o 'xml_base64'")
                    xml_obj = ET2.fromstring(xml_signed)
                    _logger.warning(xml_signed)
                    _logger.warning(xml_obj)
                    xml_name = "factura_%s.xml" % invoice.name.replace(' ', '_')
                    TFD = xml_obj.find('cfdi:Complemento', NSMAP).find('tfd:TimbreFiscalDigital', NSMAP)
                    UUID = result['uuid'] or TFD.attrib['UUID']
                    fecha_timbrado = TFD.attrib['FechaTimbrado']
                    certificado_emisor = xml_obj.attrib['NoCertificado']
                    certificado_sat = TFD.attrib['NoCertificadoSAT']
                    lugar_expedicion = xml_obj.attrib['LugarExpedicion']
                    sello_digital = xml_obj.attrib['Sello']
                    sello_digital_sat = TFD.attrib['SelloSAT']
                    url = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx'
                    qr_value = '%s?id=%s&re=%s&rr=%s&tt=%s&fe=%s' % (
                    url, UUID, invoice.company_id.vat, invoice.partner_id.vat, invoice.amount_total,sello_digital[-8:])
                    options = {'width': 275 * mm, 'height': 275 * mm}
                    ret_val = createBarcodeDrawing('QR', value=qr_value, **options)
                    qrcode = base64.encodestring(ret_val.asString('jpg'))
                    xslt_file = os.path.dirname(os.path.realpath(__file__)).replace('models','data_sat/cadenaoriginal_TFD_1_1.xslt')
                    xslt = ET2.parse(xslt_file)
                    transform = ET2.XSLT(xslt)
                    cad_org_tfd = '%s' % transform(TFD)
                    vals = {
                        'usuario_timbrado': self.env.user.id,
                        #'cdfi_invoice_name': xml_name,
                        'folio_fiscal': UUID,
                        'fecha_timbrado': fecha_timbrado,
                        'certificado_emisor': certificado_emisor,
                        'cetificaso_sat': certificado_sat,
                        'rfc_emisor': self.env.user.company_id.vat,
                        'lugar_expedicion': lugar_expedicion,
                        'selo_digital_cdfi': sello_digital,
                        'selo_sat': sello_digital_sat,
                        'qrcode_image': qrcode,
                        'cad_org_tfd': cad_org_tfd,
                        'factura_cfdi': True,
                        'estado_factura': 'factura_correcta'
                    }
                    _logger.warning(vals)
                    pac.write({'timbres': pac.timbres + 1})
                    invoice.write(vals)
                    _logger.warning("Vals guardados")
                    xml_binary = self.env['ir.attachment'].sudo().create({
                        'name': xml_name,
                        'datas': result['xml'],
                        'res_model': self._name,
                        'res_id': invoice.id,
                        'type': 'binary'
                    })
                    invoice.cfdi_xml = xml_binary
                else:
                    result['description'] = result.get('description', False) or ''
                    description = result['description'] if result['description'] else ""
                    error = "%s: %s\n" % (result['code'], description)
                    raise Warning("%s\n%s" % (error, values))

        return True

    def action_cfdi_rechazada(self):
        for invoice in self:
            if invoice.factura_cfdi:
                if invoice.estado_factura == 'solicitud_rechazada':
                    invoice.estado_factura = 'factura_correcta'
                    # raise UserError(_('La factura ya fue cancelada, no puede volver a cancelarse.'))

    def encode(self,key, string):
        encoded_chars = []
        for i in range(len(string)):
            key_c = key[i % len(key)]
            encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
            encoded_chars.append(encoded_c)
        encoded_string = "".join(encoded_chars)
        return encoded_string

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pedimento = fields.Char('Pedimento')
    predial = fields.Char('No. Predial')


