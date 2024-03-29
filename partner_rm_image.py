# If you want avoid creating new images you should avoid the following method:
# https://github.com/odoo/odoo/blob/ba23c9f354/odoo/addons/base/res/res_partner.py#L284-L310

# If you want to know how much bytes will be free after run the script
"""
SELECT count(*), pg_size_pretty(SUM(file_size))
FROM (
    SELECT checksum, MAX(file_size) AS size
         FROM ir_attachment
         WHERE res_model = 'res.partner'
           AND res_field IS NOT NULL
         GROUP BY checksum
         HAVING count(1) > (
             SELECT count(1)
             FROM res_partner
             WHERE parent_id IS NOT NULL
             GROUP BY parent_id
             ORDER BY count(1) DESC
             LIMIT 1)
) vw
INNER JOIN ir_attachment a
   ON a.checksum = vw.checksum
"""

# Odoo uses same image for children like parent
# So, it is checking what is the max image repeated
env.cr.execute("""
    SELECT count(1)
    FROM res_partner
    WHERE parent_id IS NOT NULL
    GROUP BY parent_id
    ORDER BY count(1) DESC
    LIMIT 1""")
max_img_repeated = env.cr.fetchone()[0] + 1

# Get all partner using duplicated images checksum from partner.image* fields
env.cr.execute("""
    SELECT DISTINCT ON (res_id) res_id AS partner_id
    FROM ir_attachment
    WHERE checksum IN (
        SELECT checksum
        FROM ir_attachment
        WHERE res_model = 'res.partner'
          AND res_field IS NOT NULL
        GROUP BY checksum, res_field
        HAVING count(1) > %s
    )
    """, (max_img_repeated,))

partner_ids = [partner_id[0] for partner_id in env.cr.fetchall()]
env['res.partner'].browse(partner_ids).write({'image': False})
