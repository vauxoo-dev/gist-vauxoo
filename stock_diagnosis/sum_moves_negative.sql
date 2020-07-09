/*
Retrieve all products whose sum of all incoming - outgoing stock move lines
on all internal locations results on a negative quantity.
*/
WITH sml_quantity AS (
    SELECT
        product_id,
        company_id,
        SUM(qty_done) AS quantity,
        COUNT(*) AS qty_of_sml
    FROM
        (
            SELECT
                sml.product_id,
                sm.company_id,
                sml.qty_done
            FROM
                stock_move AS sm
            INNER JOIN
                stock_move_line AS sml
                ON sm.id = sml.move_id
            INNER JOIN
                stock_location AS src_location
                ON sml.location_id = src_location.id
            INNER JOIN
                stock_location AS dest_location
                ON sml.location_dest_id = dest_location.id
            WHERE
                sml.state = 'done'
                AND src_location.usage != 'internal'
                AND dest_location.usage = 'internal'
            UNION ALL
            SELECT
                sml.product_id,
                sm.company_id,
                -qty_done
            FROM
                stock_move AS sm
            INNER JOIN
                stock_move_line AS sml
                ON sm.id = sml.move_id
            INNER JOIN
                stock_location AS src_location
                ON sml.location_id = src_location.id
            INNER JOIN
                stock_location AS dest_location
                ON sml.location_dest_id = dest_location.id
            WHERE
                sml.state = 'done'
                AND src_location.usage = 'internal'
                AND dest_location.usage != 'internal'
        ) AS all_sml
    GROUP BY
        product_id,
        company_id
)
SELECT
    product_id,
    qty_of_sml
FROM
    sml_quantity
INNER JOIN
    product_product AS pp
    ON sml_quantity.product_id = pp.id
INNER JOIN
    product_template AS pt
    ON pp.product_tmpl_Id = pt.id
WHERE
    sml_quantity.quantity < 0.0
    AND pt.type = 'product'
ORDER BY
    qty_of_sml;
