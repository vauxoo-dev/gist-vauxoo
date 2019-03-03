env.ref('base.main_company').write({'fiscalyear_lock_date': False, 'period_lock_date': False})
invoice_obj = env['account.invoice']
config = env['ir.config_parameter'].sudo()
config.set_param('l10n_mx_edi.avoid_stamp_payments', False)
env['account.journal'].search(['|',('active','=',False),('active','=',True)]).write({'update_posted': True})
taxes = env['account.tax'].search([('type_tax_use', '=', 'sale'), ('account_id.reconcile', '=', True)])
if taxes:
    env.cr.execute('''UPDATE account_account SET reconcile=false WHERE id IN %s''', (tuple(taxes.mapped('account_id').ids), ))
env.cr.execute('''UPDATE account_invoice SET date=date_invoice WHERE state in ('open', 'paid') AND date IS NULL''')
exchenge_journal = env['account.journal'].search([('code', '=', 'ACMON')])
env.ref('base.main_company').write({'realization_journal_id': exchenge_journal.id})
env.cr.execute("DELETE FROM ir_model_data WHERE model= 'account.full.reconcile'" )
