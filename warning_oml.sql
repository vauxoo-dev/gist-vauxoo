--Esta debe retornar 4 registros
select * from ir_model_constraint 
where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

-- Eliminarlos
delete from ir_model_constraint where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

-- Un registro
select * from ir_model_relation where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

--Eliminar
delete from ir_model_relation where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

-- Eliminar las tablas de los modelos

drop table invoice_facturae_txt_rel;
drop table wizard_invoice_facturae_txt_v6;

-- Eliminar modelos
delete from ir_model where name='invoice.facturae.txt.rel';
delete from ir_model where name='wizard.invoice.facturae.txt.v6';
