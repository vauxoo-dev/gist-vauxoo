# Moves comes with l10n_mx_edi_cfdi_uuid empty because there is no filestore in
# the migration process, so it is required to apply this code as a server action

batch_size = None # None finds all occurrences. Change None to specific quantity if you are interested in batches (int)
env.cr.execute(
    """
    SELECT
        document.move_id
    FROM
        account_edi_document AS document
    INNER JOIN
        account_move AS move
        ON
            document.move_id = move.id
    WHERE
        move.state = 'posted'
        AND move.write_date < CURRENT_DATE
        AND move.l10n_mx_edi_cfdi_uuid IS NULL
    ORDER BY
        move.write_date
    LIMIT
        %s
    """,
    (batch_size,)
)

moves = env["account.move"].sudo().browse(x[0] for x in env.cr.fetchall())
if not moves:
    raise UserError("There are no moves to assign: %s" % len(moves))
move_ids = []
uuids = []
for move in moves:
    uuid = move._l10n_mx_edi_decode_cfdi().get("uuid")
    move_ids.append(move.id)
    uuids.append(uuid or '')

env.cr.execute(
    """
    WITH inserted_uuid AS (
        SELECT
            *
        FROM
            UNNEST(
                %s,
                %s
            ) AS arrays(move_id, l10n_mx_edi_cfdi_uuid)
    )
    UPDATE
        account_move AS move
    SET
        l10n_mx_edi_cfdi_uuid = NULLIF(iu.l10n_mx_edi_cfdi_uuid, ''),
        write_date = NOW() AT TIME ZONE 'utc',
        write_uid = 1
    FROM
        inserted_uuid AS iu
    WHERE
        move.id = iu.move_id
        AND move.l10n_mx_edi_cfdi_uuid IS NULL
    """,
    (move_ids, uuids),
)
