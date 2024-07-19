================================
DEPLACEMENT DANS LES REPERTOIRES
================================
cd /srv/backupdatas/docker-home/_datas/odoo14/
docker-compose down && docker-compose up -d

cd /srv/backupdatas/docker-home/_volumes/odoo14/datas00/
cd wasscom_addons_customs
git pull

================================
SELECTION D'UNE FACTURE
================================
select id, name as numFact, x_adress as adrClt, x_objet as objetFact,date_operation as dateFact,x_total_facture as Montant,x_mnt_lettre as lettre from facture_facture where name like '%002/2024%' order by id desc ;


================================
SELECTION D'UN BL D'UNE FACTURE
================================
select id,x_chauffeur_id as chauffeur, x_fact_id as idFact, x_date_be  as dateBe, x_num_be as numBe,x_date_bl  as dateBl, x_num_bl as numBl,x_capacite as capacite,x_taux as taux,x_mt_ligne as montant, x_manquant as qteManquant,x_mnt_perte as montantPerte from facture_facture_line where 15 = 15 order by x_chauffeur_id,x_date_be asc ;

================================
SELECTION DES MANQUANTS
================================
select 
coalesce(c.name, 'WASSCOM') as chauffeur,
to_char(fl.x_date_bl, 'DD/MM/YYYY') as date_bl,
to_char(fl.x_date_be, 'DD/MM/YYYY') as date_be,
fl.x_num_be as num_be,
fl.x_num_bl as num_bl,
f.name as facture, 
coalesce(p.libelle, 'WASSCOM') as produit,
fl.x_capacite as capacite,
fl.x_manquant as qte_manquant,
fl.x_mnt_perte as montant_perte
from facture_facture_line fl
inner join facture_facture f on f.id = fl.x_fact_id
inner join facture_produit p on p.id = fl.x_produit_id
left join facture_conducteur_camion c on c.id= fl.x_chauffeur_id
where fl.x_manquant > 0
order by c.name asc, fl.x_date_bl asc ;

================================
SUPPRESSION D'UNE FACTURE
================================
delete from facture_facture_line where x_fact_id = 15 ;
delete from facture_facture where id = 15 ;




