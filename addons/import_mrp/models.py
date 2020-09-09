# -*- coding: utf-8 -*-

from odoo import models, fields, api
import csv
from io import StringIO, BytesIO
import os
import base64
import logging


_log = logging.getLogger(__name__)

PRODUCT_ID = 0
QUANTITY = 1
MRP_NAME = 2
COMPONENT_ID = 3
COMPONENT_QTY = 4

class ImportMrpWizard(models.TransientModel):
    _name = "import.mrp.wizard"

    csv_file = fields.Binary(string="Archivo CSV", required=True)


    def do_process(self):
        csv_file = base64.b64decode(self.csv_file).decode()
        file_input = StringIO(csv_file)
        file_input.seek(0)

        reader = csv.reader(file_input, delimiter=',', lineterminator='\r\n')
        i = 0
        last_mrp_id = self.env["mrp.bom"]
        data = []
        _last_data = {}
        for row in reader:
            i += 1
            if i == 1:
                continue

            product_ref = row[PRODUCT_ID]
            mrp_qty = row[QUANTITY]
            mrp_name = row[MRP_NAME]

            if len(product_ref) > 0:
                _last_data = {
                    "ref_id": product_ref,
                    "mrp_qty": mrp_qty,
                    "mrp_name": mrp_name,
                    "lines": []
                }
                data.append(_last_data)
            else:
                component_ref_id = row[COMPONENT_ID]
                component_qty = row[COMPONENT_QTY]
                _last_data["lines"].append({
                    "ref_id": component_ref_id,
                    "qty": component_qty
                })

        for d in data:
            product_ref_id = d.get("ref_id", False)
            mrp_qty = d.get("mrp_qty", False)
            mrp_name = d.get("mrp_name", False)

            product_id = self.env["product.template"].search([
                ('default_code', '=', product_ref_id)
            ], limit=1)

            if not product_id.exists():
                continue

            last_mrp_id = self.env["mrp.bom"].create(dict(
                product_tmpl_id=product_id.id,
                code=mrp_name,
                product_qty=mrp_qty
            ))

            for l in d.get("lines", []):
                product_ref_id = l.get("ref_id", False)
                qty = l.get("qty", 0)

                product_id = self.env["product.product"].search([
                    ('default_code', '=', product_ref_id)
                ], limit=1)

                if not product_id.exists():
                    continue

                self.env["mrp.bom.line"].create(dict(
                    bom_id=last_mrp_id.id,
                    product_id=product_id.id,
                    product_qty=qty
                ))


