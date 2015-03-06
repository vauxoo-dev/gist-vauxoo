#!/usr/bin/python
import oerplib
import os
import sys

HOST= ''
PORT= 
DB= ''
USER= ''
PASS= ''

con = oerplib.OERP(
server=HOST,
database=DB,
port=PORT,
)

con.login(USER, PASS)
ids = []
modules = [
    "oml",
    "l10n_mx_addendas_chedraui",
    "l10n_mx_accountinge",
    "l10n_mx_account_type",
    "l10n_mx_validate_xml_sat",
    "l10n_mx_journal_type",
    "l10n_mx_cfdi_test",
    "hr_expense_replenishment_tax",
    "hr_expense_replenishment",
    "hr_expense_analytic",
    "account_move_report",
    "account_invoice_line_currency",
    "l10n_mx_facturae_pac_sf",
    "l10n_mx_payroll_base",
    "l10n_mx_hr_payroll",
    "l10n_mx_payroll_concept",
    "l10n_mx_payroll_regime_employee",
    "l10n_mx_payroll_risk_rank_contract",
    "lang_conf",
    "hr_payroll",
    "hr_holidays",
    "calendar",
    "hr_contract",
    "hr_payroll_account",
    "hr_payroll_cancel",
    "hr_payslip_validation_home_address",
    "l10n_mx_data_bank",
]

attachment_mx_ids_before = con.search('ir.attachment.facturae.mx', [])
invoice_ids_before = con.search('account.invoice', [])
account_ids_before = con.search('account.account', [])
sale_order_ids_before = con.search('sale.order', [])
pickins_ids_before = con.search('stock.picking', [])
stock_moves_ids_before = con.search('stock.move', [])
account_bank_statement_ids_before = con.search('account.bank.statement', [])

for name in modules:
    ids = con.search('ir.module.module', [('name', '=', name),
                                          ('state', '=', 'installed')])

    for id in ids:
        try:
            print 'Desinstalando el modulo', name
            con.execute('ir.module.module', 'button_immediate_uninstall', [id])

        except:
            print 'No se pudo desinstalar el modulo', name
            st_ids = con.search('ir.module.module', [
                ('state', '=', 'to install')])
        print con.read('ir.module.module', [id], ['state'])[0].get('state')

attachment_mx_ids_after = con.search('ir.attachment.facturae.mx', [])
invoice_ids_after = con.search('account.invoice', [])
account_ids_after = con.search('account.account', [])
sale_order_ids_after = con.search('sale.order', [])
pickins_ids_after = con.search('stock.picking', [])
stock_moves_ids_after = con.search('stock.move', [])
account_bank_statement_ids_after = con.search('account.bank.statement', [])

print "**************************RESULTS************************************"
print 'Atta MX before:',len(attachment_mx_ids_before),' after:',len(attachment_mx_ids_after)
print 'Invoice before:',len(invoice_ids_before),' after:',len(invoice_ids_after)
print 'Account before:',len(account_ids_before),' after:',len(account_ids_after)
print 'Sale orders before:',len(sale_order_ids_before),' after:',len(sale_order_ids_after)
print 'Pickings before:',len(pickins_ids_before),' after:',len(pickins_ids_after)
print 'Stock moves before:',len(stock_moves_ids_before),' after:',len(stock_moves_ids_after)
print 'Bank Statement before:',len(account_bank_statement_ids_before),' after:',len(account_bank_statement_ids_after)
print "******************************************************************"
