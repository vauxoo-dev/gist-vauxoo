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
        product_id,
        location_id,
        COALESCE(lot_id, 0) AS lot_id,
        COALESCE(package_id, 0) AS package_id,
        COALESCE(owner_id, 0) AS owner_id,
        company_id,
        SUM(quantity)::NUMERIC AS sum_qty
    FROM
        stock_quant
    GROUP BY
        product_id,
        location_id,
        lot_id,
        package_id,
        owner_id,
        company_id
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
    WHERE
        sml.location_id != sml.location_dest_id
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
    WHERE
        sml.location_id != sml.location_dest_id
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
    q.product_id,
    q.location_id,
    q.lot_id,
    q.package_id,
    q.owner_id,
    q.company_id,
    q.sum_qty AS qty_on_quants,
    COALESCE(m_in.sum_qty, 0.0) AS qty_on_incoming_moves,
    COALESCE(m_out.sum_qty, 0.0) AS qty_on_outgoing_moves,
    COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0) AS qty_on_all_moves,
    q.sum_qty - (COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0)) AS difference,
    COALESCE(m_in.sml_count, 0.0) + COALESCE(m_out.sml_count, 0.0) AS qty_of_sml
FROM
    quant_quantity AS q
INNER JOIN
    stock_location AS sl
    ON q.location_id = sl.id
LEFT OUTER JOIN
    in_move_quantity AS m_in
    ON q.product_id = m_in.product_id
    AND q.location_id = m_in.location_id
    AND q.lot_id = m_in.lot_id
    AND q.package_id = m_in.package_id
    AND q.owner_id = m_in.owner_id
    AND q.company_id = m_in.company_id
LEFT OUTER JOIN
    out_move_quantity AS m_out
    ON q.product_id = m_out.product_id
    AND q.location_id = m_out.location_id
    AND q.lot_id= m_out.lot_id
    AND q.package_id = m_out.package_id
    AND q.owner_id = m_out.owner_id
    AND q.company_id = m_out.company_id
WHERE
    q.sum_qty != COALESCE(m_in.sum_qty, 0.0) - COALESCE(m_out.sum_qty, 0.0)
    AND sl.usage = 'internal'
ORDER BY
    COALESCE(m_in.sml_count, 0) + COALESCE(m_out.sml_count, 0);
