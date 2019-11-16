sequences = env['ir.sequence'].sudo().search([('implementation', '=', 'no_gap'), '|', ('active', '=', False), ('active', '=', True)])
msg = "Sequences changes to Standard: %s" % (sequences.ids)
log(msg)
for item in sequences:
 # TODO: Get sequence name from exception: psycopg2.ProgrammingError: relation "ir_sequence_047" already exists
 #       For now it is computed manually since that it is used in server action where psycopg2.ProgrammingError exception is not available
 seq_name = "ir_sequence_%03d" % (item.id)
 env.cr.execute("DROP SEQUENCE IF EXISTS %s" % seq_name)
 if item.use_date_range:
   range_ids = {}
   for line in item.date_range_ids:
    range_ids[line.id] = line.number_next_actual
    seq_name = "ir_sequence_%03d_%03d" % (item.id, line.id)
    env.cr.execute("DROP SEQUENCE IF EXISTS %s" % seq_name)
   item.write({'implementation': 'standard'})
   for line in item.date_range_ids:
     line.write({'number_next_actual': range_ids[line.id]})
   continue
 item.write({'implementation': 'standard'})

