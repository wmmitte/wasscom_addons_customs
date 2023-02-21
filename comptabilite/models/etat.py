from odoo import fields, models, api
from datetime import date


class BilanComptable(models.Model):
    _name = 'bilan.comptable'

    name = fields.Char("Libellé", required=True)

