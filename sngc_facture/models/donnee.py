from odoo import fields, models


class SngcTypeArticle(models.Model):
    _name = "sngc.type.article"
    _description = 'Modele des types articles'

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)


class SngcArticle(models.Model):
    _name = "sngc.article"
    _description = 'Modele des articles'

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)


class SngcRegion(models.Model):
    _name = "sngc.region"
    _description = "Modele des régions"

    name = fields.Char("Libellé", required=True)
    active = fields.Boolean("Actif", default=True)
    province_ids = fields.One2many("sngc.province", "region_id")


class SngcProvince(models.Model):
    _name = "sngc.province"
    _description = "Modele des provinces"

    region_id = fields.Many2one("sngc.region")
    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)
    commune_ids = fields.One2many("sngc.ville", "province_id")


class SngcVille(models.Model):
    _name = "sngc.ville"
    _description = "Modele des villes"

    province_id = fields.Many2one("sngc.province")
    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif", default=True)

