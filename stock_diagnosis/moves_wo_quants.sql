/*
Retrieve all products whose sum of incoming moves - outgoing moves should
leave available quantities in stock, but thjere's no quant for them
*/
SELECT
    distinct sml.product_id
FROM (
    SELECT
        sml_in.product_id,
        sml_in.location_dest_id AS location_id,
        sm_in.company_id,
        sml_in.qty_done
    FROM
        stock_move_line AS sml_in
    INNER JOIN
        stock_move AS sm_in
        ON sml_in.move_id = sm_in.id
    WHERE
        sml_in.location_id != sml_in.location_dest_id
        AND sml_in.state = 'done'
    UNION
    SELECT
        sml_out.product_id,
        sml_out.location_id,
        sm_out.company_id,
        -sml_out.qty_done
    FROM
        stock_move_line AS sml_out
    INNER JOIN
        stock_move AS sm_out
        ON sml_out.move_id = sm_out.id
    )AS sml
INNER JOIN
    stock_location AS location
    ON sml.location_id = location.id
INNER JOIN
    product_product AS pp
    ON sml.product_id = pp.id
INNER JOIN
    product_template AS pt
    ON pp.product_tmpl_id = pt.id
LEFT OUTER JOIN
    stock_quant AS quant
    ON sml.product_id = quant.product_id
    AND sml.location_id = quant.location_id
    AND sml.company_id = quant.company_id
WHERE
    location.usage = 'internal'
    AND pt.type = 'product'
GROUP BY
    sml.product_id,
    sml.location_id,
    sml.company_id
HAVING
    SUM(sml.qty_done) != COALESCE(SUM(quant.quantity), 0.0);
