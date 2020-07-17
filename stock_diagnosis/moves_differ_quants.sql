/*
Retrieve all products whose sum of incoming moves - outgoing moves differs
from the quantities reported by quants
*/
WITH sml_quantity AS (
    SELECT
        all_sml.product_id,
        all_sml.location_id,
        COALESCE(all_sml.lot_id, 0) AS lot_id,
        COALESCE(all_sml.package_id, 0) AS package_id,
        COALESCE(all_sml.owner_id, 0) AS owner_id,
        all_sml.company_id,
        SUM(all_sml.qty_done) AS quantity
    FROM
        (
            SELECT
                sml_in.product_id,
                sml_in.location_dest_id AS location_id,
                sml_in.lot_id,
                sml_in.package_id,
                sml_in.owner_id,
                sm_in.company_id,
                sml_in.qty_done
            FROM
                stock_move_line AS sml_in
            INNER JOIN
                stock_move AS sm_in
                ON sml_in.move_id = sm_in.id
            WHERE
                sml_in.state = 'done'
            UNION ALL
            SELECT
                sml_out.product_id,
                sml_out.location_id,
                sml_out.lot_id,
                sml_out.package_id,
                sml_out.owner_id,
                sm_out.company_id,
                -sml_out.qty_done
            FROM
                stock_move_line AS sml_out
            INNER JOIN
                stock_move AS sm_out
                ON sml_out.move_id = sm_out.id
            WHERE
                sml_out.state = 'done'
        ) AS all_sml
    INNER JOIN
        stock_location AS location
        ON all_sml.location_id = location.id
    WHERE
        location.usage = 'internal'
    GROUP BY
        all_sml.product_id,
        all_sml.location_id,
        all_sml.lot_id,
        all_sml.package_id,
        all_sml.owner_id,
        all_sml.company_id
),
quant_quantity AS (
    SELECT
        quant.product_id,
        quant.location_id,
        COALESCE(quant.lot_id, 0) AS lot_id,
        COALESCE(quant.package_id, 0) AS package_id,
        COALESCE(quant.owner_id, 0) AS owner_id,
        quant.company_id,
        SUM(quant.quantity) AS quantity
    FROM
        stock_quant AS quant
    INNER JOIN
        stock_location AS location
        ON quant.location_id = location.id
    WHERE
        location.usage = 'internal'
    GROUP BY
        quant.product_id,
        quant.location_id,
        quant.lot_id,
        quant.package_id,
        quant.owner_id,
        quant.company_id
)
SELECT DISTINCT
    sml_quantity.product_id
FROM
    sml_quantity
LEFT OUTER JOIN
    quant_quantity
    ON sml_quantity.product_id = quant_quantity.product_id
    AND sml_quantity.location_id = quant_quantity.location_id
    AND sml_quantity.lot_id = quant_quantity.lot_id
    AND sml_quantity.package_id = quant_quantity.package_id
    AND sml_quantity.owner_id = quant_quantity.owner_id
    AND sml_quantity.company_id = quant_quantity.company_id
WHERE
    sml_quantity.quantity != COALESCE(quant_quantity.quantity, 0.0);
