# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning

from suds.client import Client, WebFault
from suds.xsd.doctor import Import, ImportDoctor

import json
import tempfile
import zipfile
import base64


import logging

_logger = logging.getLogger("========= TIMBRADO =========")


class PacConfig(models.Model):
    _inherit = 'cfdi.pac.config'

    id_equipo = fields.Char(string='Id Equipo', required=True)

    def timbrar_xml(self, object, xml):
        Usuario = self.user
        Password = self.password
        Serie = ""
        IdEquipo = self.id_equipo
        url = self.url

        zip_file = tempfile.NamedTemporaryFile(suffix=".zip", prefix="cfdi_")
        zipf = zipfile.ZipFile(zip_file.name, "w", zipfile.ZIP_DEFLATED)
        zipf.writestr('cfdi.xml', xml)
        zipf.close()
        with open(zip_file.name, "rb") as zip_binary:
            archivoXMLZip = base64.b64encode(zip_binary.read())
        zip_file.close()
        client = Client(url)
        timbrar = getattr(client.service, self.timbrar)
        try:
            response = timbrar(Usuario, Password, archivoXMLZip, Serie, IdEquipo)
        except WebFault as error:
            return {
                'validate': False,
                'code': error.fault.detail.SifeiException.codigo,
                'description': error.fault.detail.SifeiException.message + "(" +error.fault.detail.SifeiException.error + ")",
            }
        zip_file = tempfile.NamedTemporaryFile(suffix=".zip", prefix="cfdi_")
        zip_file.write(base64.b64decode(response))
        zip_file.flush()
        zipf = zipfile.ZipFile(zip_file.name, "r")
        xml = zipf.read(zipf.namelist()[0])
        zipf.close()
        zip_file.close()
        _logger.info("RESULTADO:\n%s" % xml)
        return {
            'validate': True,
            'xml': xml,
            'uuid': False
        }
