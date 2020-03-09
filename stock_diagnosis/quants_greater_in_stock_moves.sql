/*
This retrieves the products and their internal locations whose quantity
reported by their quants is greater than the sum of all incoming stock moves.

This is achieved by:
1) Retrieve product quantities by location according to quants
2) Retrieve incoming stock moves by location
3) Compare results of the previous steps, showing only those when 1) is greater
   than 2)
*/
WITH quant_quantity AS (
    SELECT  
        product_id,
        location_id,
        SUM(quantity)::NUMERIC AS sum_qty
    FROM
        stock_quant
    GROUP BY
        product_id,
        location_id
),
in_move_quantity AS (
    SELECT
        product_id,
        location_dest_id AS location_id,
        SUM(product_uom_qty)::NUMERIC AS sum_qty
    FROM
        stock_move
    WHERE
        location_id != location_dest_id
    GROUP BY
        product_id,
        location_dest_id
)
SELECT
    q.product_id,
    q.location_id,
    q.sum_qty AS qty_on_quants,
    m.sum_qty AS qty_on_incoming_moves,
    q.sum_qty - m.sum_qty AS difference
FROM
    quant_quantity AS q
INNER JOIN
    in_move_quantity AS m
    ON q.product_id = m.product_id
    AND q.location_id = m.location_id
INNER JOIN
    stock_location AS sl
    ON q.location_id = sl.id
WHERE
    q.sum_qty > m.sum_qty
    AND sl.usage = 'internal';
