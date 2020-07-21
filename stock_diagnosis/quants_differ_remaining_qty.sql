/*
This retrieves the products whose quantity reported by their quants is
different from the sum of all remaining quantities reported by stock moves.

This is achieved by:
1) Retrieve product quantities according to quants
2) Retrieve remaining quantities
3) Compare results of the previous steps, showing only those when
  (1) is different from (2)
*/
WITH qty_available AS (
    SELECT
        quant.product_id,
        quant.company_id,
        SUM(quant.quantity)::NUMERIC AS quantity
    FROM
        stock_quant AS quant
    INNER JOIN
        stock_location AS location
        ON quant.location_id = location.id
    WHERE
        location.usage = 'internal'
    GROUP BY
        quant.product_id,
        quant.company_id
),
remaining_qty AS (
    SELECT
        product_id,
        company_id,
        SUM(remaining_qty)::NUMERIC AS quantity
    FROM
        stock_move
    where
        remaining_qty != 0.0
    GROUP BY
        product_id,
        company_id
)
SELECT
    product_id,
    company_id,
    qty_available.quantity AS qty_available,
    remaining_qty.quantity AS remaining_qty
FROM
    qty_available
FULL JOIN
    remaining_qty
    USING(product_id, company_id)
WHERE
    ROUND(COALESCE(qty_available.quantity, 0.0) - COALESCE(remaining_qty.quantity, 0.0), 2) != 0.0;
