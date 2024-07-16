================================
DEPLACEMENT DANS LES REPERTOIRES
================================
cd /srv/backupdatas/docker-home/_datas/odoo14/
docker-compose down

cd /srv/backupdatas/docker-home/_volumes/odoo14/datas00/
git pull

================================
SELECTION D'UNE FACTURE
================================
select id, name as numFact, x_adress as adrClt, x_objet as objetFact,date_operation as dateFact,x_total_facture as Montant,x_mnt_lettre as lettre from facture_facture where name like '%002/2024%' order by id desc ;


================================
SELECTION D'UN BL D'UNE FACTURE
================================
select id, x_fact_id as idFact, x_date_be  as dateBe, x_num_be as numBe,x_date_bl  as dateBl, x_num_bl as numBl,x_capacite as capacite,x_taux as taux,x_mt_ligne as montant from facture_facture_line where x_fact_id = 15 order by id desc ;

================================
SUPPRESSION D'UNE FACTURE
================================
delete from facture_facture_line where x_fact_id = 15 ;
delete from facture_facture where id = 15 ;




