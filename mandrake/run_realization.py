invoice_obj = env['account.invoice']
query = """
  SELECT
    i.id AS invoice_id,
    i.date_invoice AT TIME ZONE 'utc' AT TIME ZONE 'America/Mexico_City' AS date_invoice,
    max(aml.date AT TIME ZONE 'utc' AT TIME ZONE 'America/Mexico_City')
FROM
    account_invoice_account_move_line_rel AS rel
INNER JOIN
    account_move_line AS aml ON aml.id = rel.account_move_line_id
INNER JOIN
    account_invoice AS i ON i.id = rel.account_invoice_id
WHERE
    i.state = 'paid' AND i.currency_id = 2 AND aml.date >= '2019-01-01' AND i.date_invoice < aml.date AND EXTRACT(MONTH FROM i.date_invoice) != EXTRACT(MONTH FROM aml.date)
GROUP BY
    i.id,
    i.date_invoice
ORDER BY
    i.date_invoice ASC
"""

# Executing to paid invoices


env.cr.execute(query)
for paid in env.cr.fetchall():
  invoice = invoice_obj.browse(paid[0])
  if invoice.realization_move_ids:
    continue
  amls = invoice.payment_move_line_ids
  amls.remove_move_reconcile()
  today = paid[2]
  date = datetime.date(today.year, today.month, 1) - relativedelta(days=1)
  year = int(paid[1].year)
  year = year if year >= 2018 else 2018
  pay_year = int(date.year)
  try:
    while pay_year > year:
      invoice.create_realization_entries(date.strftime('%Y-%m-%d'))
      date = datetime.date(date.year, date.month, 1) - relativedelta(days=1)
      pay_year = int(date.year)
    invoice.create_realization_entries(date.strftime('%Y-%m-%d'))
    alive_amls = amls.exists()
    if alive_amls:
        invoice.register_payment(alive_amls)
    invoice.message_post(body='Computed Exchange Rate')
    log('Calculado exchange rate a factura %s' % invoice.id)
    env.cr.commit()
  except Exception as e:
    invoice.message_post(body="No se pudo calcular el exchange de la factura %s debido %s" % (invoice.id, e))
log('Terminando la reconciliación para calculo de diferencial cambiario %s' % datetime.datetime.now())
