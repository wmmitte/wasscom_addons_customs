from odoo import fields,api,models,tools,_
import string
from datetime import datetime,date
import pdb
import calendar
from calendar import monthrange
from odoo.exceptions import UserError,ValidationError
from dateutil.relativedelta import relativedelta


# class produit
class Facturation_Produit(models.Model):
    _name = 'facture_produit'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of produit.", default=10)

    name = fields.Char(string = "Désignation" ,required = False)
    libelle = fields.Char(string = "Désignation" ,required = True)
    description = fields.Text(string = "Description" ,required = False)
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)

    @api.constrains('libelle')
    def action_convertir(self):
        for record in self:
            record.name = record.libelle.upper()



# class localité
class Facturation_Localite(models.Model):
    _name = 'facture_localite'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of localite.", default=10)

    name = fields.Char(string = "Intitulé" ,required = False)
    libelle = fields.Char(string = "Intitulé" ,required = True)
    description = fields.Text(string = "Description" ,required = False)
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)

    @api.constrains('libelle')
    def action_convertir_(self):
        for record in self:
            record.name = record.libelle.upper()


# class trajet
class Facturation_Trajet(models.Model):
    _name = 'facture_trajet'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of trajet.", default=10)

    name = fields.Char('Trajet',compute = 'action_concat',store = True)
    localite_a = fields.Many2one('facture_localite',string = "Localité A" ,required = True)
    localite_b = fields.Many2one('facture_localite',string = "Localité B" ,required = True)
    x_distance = fields.Integer(string = 'Distance (km)',required = True)
    description = fields.Text(string = "Description" ,required = False)
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)

    @api.depends('localite_a','localite_b')
    def action_concat(self):
        for record in self:
            if record.localite_a.name and record.localite_b.name:
                record.name = record.localite_a.name + ' - ' + record.localite_b.name



# class client
class Facturation_Client(models.Model):
    _name = 'facture_client'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of client.", default=10)
    _rec_name = 'x_designation_'
    name = fields.Char(string = "Sigle" ,required = True)
    x_designation_client = fields.Char(string = "Raison sociale/nom" ,required = True)
    x_designation_ = fields.Char(compute = 'action_client_fullname',store = True,string = "Raison sociale/nom")
    x_adress = fields.Char(string = "Adresse" ,required = True)
    x_tel = fields.Char(string = "Télephone" ,required = True)
    x_contact = fields.Char(compute = 'action_client_contact',store = True,string = "Contact")
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)

    _sql_constraints = [
        ('code_client_unique','UNIQUE (name)','Le code du client doit être unique'),
        ('adresse_client_unique', 'UNIQUE (x_adress)', "L'adresse' du client doit être unique")
    ]


    @api.depends('name','x_designation_client','x_tel')
    def action_concat_code_desig(self):
        for record in self:
            if record.name and record.x_designation_client and record.x_tel:
                record.x_designation_ = record.name + '/' + record.x_designation_client+ '/'+ record.x_tel
   
    @api.onchange('name','x_designation_client','x_tel')
    def action_client_fullname(self):
        for record in self:
            if record.name and record.x_designation_client:
                record.x_designation_ = record.x_designation_client+ ' (' + record.name + ')'
    
    @api.depends('x_adress','x_tel')
    def action_client_contact(self):
        for record in self:
            if record.x_adress and record.x_tel:
                record.x_contact = record.x_tel + ', ' + record.x_adress


# class conducteur camion
class Facturation_Conducteur_Camion(models.Model):
    _name = 'facture_conducteur_camion'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of conducteur camion.", default=10)

    name = fields.Char(string = "Nom & Prénom(s)" ,required = True)
    x_tel = fields.Char(string = "Télephone",required = True)
    description = fields.Text(string = "Description" ,required = False)
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)


# class camion
class Facturation_Camion(models.Model):
    _name = 'facture_camion'
    _order = 'sequence, id'
    sequence = fields.Integer(help="Gives the sequence when displaying a list of camion.", default=10)

    name = fields.Text(string = "Immatriculation" ,required = True)
    x_conducteur_id = fields.Many2one('facture_conducteur_camion',string = 'Conducteur',required = True)
    description = fields.Text(string = "Description" ,required = False)
    x_struct_id = fields.Many2one('res.company' ,string = "Structure" ,default=lambda self: self.env.user.company_id.id, required = True)
    active = fields.Boolean(string = "Etat", default=True)

