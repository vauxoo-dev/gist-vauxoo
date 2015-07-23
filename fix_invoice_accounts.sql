SELECT ai.type, ai.id, ai.state, ai.residual, ai.account_id, aml.account_id
FROM account_invoice AS ai
INNER JOIN account_move AS am ON ai.move_id = am.id
INNER JOIN account_move_line AS aml ON aml.move_id = am.id
INNER JOIN account_account AS aa ON aml.account_id = aa.id
    WHERE ai.state = 'open'
    AND ai.residual = 0
    AND aa.type IN ('receivable', 'payable')
    AND ai.type IN ('in_invoice', 'out_invoice')
    ;
