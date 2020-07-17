/*
This retrieves the products and their internal locations whose quantity
reported by their quants is different from the sum of all their stock moves
(incoming moves - outgoing moves).

This is achieved by:
1) Retrieve product quantities by location according to quants
2) Retrieve incoming stock move lines by location
3) Retrieve outgoing stock move lines by location
4) Compare results of the previous steps, showing only those when
   (1) is  different from (2) - (3)

Note:
This applies only for products that have quants.
*/
WITH quant_quantity AS (
    SELECT  
        quant.product_id,
        quant.location_id,
        COALESCE(quant.lot_id, 0) AS lot_id,
        COALESCE(quant.package_id, 0) AS package_id,
        COALESCE(quant.owner_id, 0) AS owner_id,
        quant.company_id,
        SUM(quant.quantity)::NUMERIC AS sum_qty
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
),
in_move_quantity AS (
    SELECT
        sml.product_id,
        sml.location_dest_id AS location_id,
        COALESCE(sml.lot_id, 0) AS lot_id,
        COALESCE(sml.package_id, 0) AS package_id,
        COALESCE(sml.owner_id, 0) AS owner_id,
        sm.company_id,
        SUM(sml.qty_done)::NUMERIC AS sum_qty,
        COUNT(*) AS sml_count
    FROM
        stock_move AS sm
    INNER JOIN
        stock_move_line AS sml
        ON sm.id = sml.move_id
    INNER JOIN
        stock_location AS location
        ON sml.location_dest_id = location.id
    WHERE
        sml.location_id != sml.location_dest_id
        AND location.usage = 'internal'
        AND sml.state = 'done'
    GROUP BY
        sml.product_id,
        sml.location_dest_id,
        sml.lot_id,
        sml.package_id,
        sml.owner_id,
        sm.company_id
),
out_move_quantity AS (
    SELECT
        sml.product_id,
        sml.location_id,
        COALESCE(sml.lot_id, 0) AS lot_id,
        COALESCE(sml.package_id, 0) AS package_id,
        COALESCE(sml.owner_id, 0) AS owner_id,
        sm.company_id,
        SUM(qty_done)::NUMERIC AS sum_qty,
        COUNT(*) AS sml_count
    FROM
        stock_move AS sm
    INNER JOIN
        stock_move_line AS sml
        ON sm.id = sml.move_id
    INNER JOIN
        stock_location AS location
        ON sml.location_id = location.id
    WHERE
        sml.location_id != sml.location_dest_id
        AND location.usage = 'internal'
        AND sml.state = 'done'
    GROUP BY
        sml.product_id,
        sml.location_id,
        sml.lot_id,
        sml.package_id,
        sml.owner_id,
        sm.company_id
)
SELECT
    product_id,
    location_id,
    lot_id,
    package_id,
    owner_id,
    company_id,
    q.sum_qty AS qty_on_quants,
    COALESCE(m_in.sum_qty, 0.0) AS qty_on_incoming_moves,
    COALESCE(m_out.sum_qty, 0.0) AS qty_on_outgoing_moves,
    COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0) AS qty_on_all_moves,
    q.sum_qty - (COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0)) AS difference,
    COALESCE(m_in.sml_count, 0.0) + COALESCE(m_out.sml_count, 0.0) AS qty_of_sml
FROM
    quant_quantity AS q
LEFT OUTER JOIN
    in_move_quantity AS m_in
    USING(product_id, location_id, lot_id, package_id, owner_id, company_id)
LEFT OUTER JOIN
    out_move_quantity AS m_out
    USING(product_id, location_id, lot_id, package_id, owner_id, company_id)
WHERE
    q.sum_qty != COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0)
ORDER BY
    COALESCE(m_in.sml_count, 0) + COALESCE(m_out.sml_count, 0);
