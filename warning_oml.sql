-- Delete warning in the follow models when in server is updated repository OML-V2
-- wizard.invoice.facturae.txt.v6
-- wizard.invoice.facturae.xml.v6
-- l10n_facturae_groups_multipac_vauxoo

-- Eliminarlos
delete from ir_model_constraint where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

--Eliminar
delete from ir_model_relation where model in ( select id from ir_model where name='wizard.invoice.facturae.txt.v6');

-- Eliminar las tablas de los modelos

drop table invoice_facturae_txt_rel;
drop table wizard_invoice_facturae_txt_v6;

-- Eliminar modelos
delete from ir_model where name='invoice.facturae.txt.rel';
delete from ir_model where name='wizard.invoice.facturae.txt.v6';

-- Eliminarlos
delete from ir_model_constraint where model in ( select id from ir_model where name='wizard.invoice.facturae.xml.v6');

--Eliminar
delete from ir_model_relation where model in ( select id from ir_model where name='wizard.invoice.facturae.xml.v6');

-- Eliminar las tablas de los modelos

drop table wizard_invoice_facturae_xml_v6;

-- Eliminar modelos
delete from ir_model where name='invoice.facturae.xml.rel';
delete from ir_model where name='wizard.invoice.facturae.xml.v6';

delete from ir_module_module where id in ( 
select id from ir_module_module where name='l10n_facturae_groups_multipac_vauxoo');

drop table wizard_accounting_mexican_statement_wizard;
delete from ir_model where name='accounting.mexican.statement.wizard';

delete from ir_model_constraint where model in ( select id from ir_model where name='accounting.mexican.statement.wizard');
delete from ir_model_relation where model in ( select id from ir_model where name='accounting.mexican.statement.wizard');

--Related with l10n_mx_facturae_group_show_wizards
DELETE FROM ir_module_module WHERE name = 'l10n_mx_facturae_group_show_wizards'
DELETE FROM res_groups WHERE name = 'Show Default Wizards FacturaE'
DELETE FROM ir_model_data WHERE module = 'l10n_mx_facturae_group_show_wizards'
DELETE FROM ir_model_data WHERE name = 'module_l10n_mx_facturae_group_show_wizards'
