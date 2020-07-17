/*
This retrieves the products and their internal locations whose quantity
reported by their quants is greater than the sum of all logistic quantities
re ported by stock moves, in case the module `stock_cost_segmentation` is
installed [1].

This is achieved by:
1) Retrieve product quantities by location according to quants
2) Retrieve logistic quantities by location
3) Compare results of the previous steps, showing only those when 1) is
   different from 2)

[1] https://github.com/Vauxoo/addons-vauxoo/tree/11.0/stock_cost_segmentation
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
logistic_quantity AS (
    SELECT
        product_id,
        location_dest_id AS location_id,
        SUM(logistic_remaining_qty)::NUMERIC AS sum_qty
    FROM
        stock_move
    GROUP BY
        product_id,
        location_dest_id
)
SELECT
    q.product_id,
    q.location_id,
    q.sum_qty AS qty_on_quants,
    l.sum_qty AS logistic_qty_on_moves,
    q.sum_qty -     l.sum_qty AS difference
FROM
    quant_quantity AS q
INNER JOIN
    logistic_quantity AS l
    ON q.product_id = l.product_id
    AND q.location_id = l.location_id
INNER JOIN
    stock_location AS sl
    ON q.location_id = sl.id
WHERE
    q.sum_qty != l.sum_qty
    AND sl.usage = 'internal';
