"""Script to order the slower trigger deleting a record

You need to get the explain for DELETE command from database, a command similar to:

    psql {DB} -c "EXPLAIN (ANALYZE, VERBOSE, BUFFERS) DELETE FROM {table} WHERE id={id};" > /tmp/explain.txt


You will get a file with the following similar output:

                                                                QUERY PLAN
-------------------------------------------------------------------------------------------------------------
 Delete on public.res_users  (cost=0.42..4.44 rows=0 width=0) (actual time=19.027..19.027 rows=0 loops=1)
   Buffers: shared hit=4663 read=131 dirtied=1
   ->  Index Scan using res_users_pkey on public.res_users  (cost=0.42..4.44 rows=1 width=6) (actual time=0.062..0.065 rows=1 loops=1)
         Output: ctid
         Index Cond: (res_users.id = 168069)
         Buffers: shared hit=4
 Query Identifier: 8875770752059111101
 Planning:
   Buffers: shared hit=136 read=18
 Planning Time: 2.757 ms
 Trigger RI_ConstraintTrigger_a_4994357 for constraint account_account_tag_create_uid_fkey: time=0.361 calls=1
 Trigger RI_ConstraintTrigger_a_4994517 for constraint account_analytic_account_write_uid_fkey: time=0.116 calls=1
 Trigger RI_ConstraintTrigger_a_5005458 for constraint mail_message_create_uid_fkey: time=46852.864 calls=1
 Trigger RI_ConstraintTrigger_a_4994537 for constraint account_analytic_applicability_write_uid_fkey: time=0.064 calls=1
 Trigger RI_ConstraintTrigger_a_4994547 for constraint account_analytic_distribution_model_create_uid_fkey: time=0.280 calls=1
 Trigger RI_ConstraintTrigger_a_4994572 for constraint account_analytic_distribution_model_write_uid_fkey: time=0.055 calls=1
 Trigger RI_ConstraintTrigger_a_4994587 for constraint account_analytic_line_create_uid_fkey: time=24.703 calls=1
 Trigger RI_ConstraintTrigger_a_4994637 for constraint account_analytic_line_user_id_fkey: time=0.334 calls=1
 ...
  Execution Time: 331724.399 ms
(1597 rows)


Then you need to run this script using this file path

    psql_delete_analyze_order_by_time.py /tmp/explain.txt

The new output:

    Trigger RI_ConstraintTrigger_a_5005458 for constraint mail_message_create_uid_fkey: time=46852.864 calls=1
    Trigger RI_ConstraintTrigger_a_4994587 for constraint account_analytic_line_create_uid_fkey: time=24.703 calls=1
    Trigger RI_ConstraintTrigger_a_4994357 for constraint account_account_tag_create_uid_fkey: time=0.361 calls=1
    Trigger RI_ConstraintTrigger_a_4994637 for constraint account_analytic_line_user_id_fkey: time=0.334 calls=1
    Trigger RI_ConstraintTrigger_a_4994547 for constraint account_analytic_distribution_model_create_uid_fkey: time=0.280 calls=1
    Trigger RI_ConstraintTrigger_a_4994517 for constraint account_analytic_account_write_uid_fkey: time=0.116 calls=1
    Trigger RI_ConstraintTrigger_a_4994537 for constraint account_analytic_applicability_write_uid_fkey: time=0.064 calls=1
    Trigger RI_ConstraintTrigger_a_4994572 for constraint account_analytic_distribution_model_write_uid_fkey: time=0.055 calls=1
    QUERY PLAN
    -------------------------------------------------------------------------------------------------------------------------------------------
    Delete on public.res_users  (cost=0.42..4.44 rows=0 width=0) (actual time=19.027..19.027 rows=0 loops=1)
    Buffers: shared hit=4663 read=131 dirtied=1
    ->  Index Scan using res_users_pkey on public.res_users  (cost=0.42..4.44 rows=1 width=6) (actual time=0.062..0.065 rows=1 loops=1)
    Output: ctid
    Index Cond: (res_users.id = 168069)
    Buffers: shared hit=4
    Query Identifier: 8875770752059111101
    Planning:
    Buffers: shared hit=136 read=18
    Planning Time: 2.757 ms
    Execution Time: 331724.399 ms
    (1597 rows)

Notice the first line is the trigger where more time was spent
"""
# pylint: disable=print-used
import re
import sys


def extract_time(line):
    match = re.search(r"time=([0-9.]+) calls=([0-9]+)", line)
    return float(match.group(1)) if match else 0.0


def main(fname):
    with open(fname) as file_obj:
        for line in sorted(file_obj, key=extract_time, reverse=True):
            print(line.strip())


if __name__ == "__main__":
    main(sys.argv[1])
