# pylint: disable=print-used

"""Get the 'CREATE INDEX...' sentences combining all the COLUMNS
related in a WHERE query

If you have a slow query using

    SELECT ...
    FROM table
    WHERE column1 ...
      AND column2 ...
      AND column3 ...

And you do not know what index will work best for these different columns
you can try creating all the combinations for all them

So, after creating all these indexes you can get the PSQL ANALYZE in order
to know what index was already used instead of testing one-by-one
"""

import itertools

TABLE = "ir_property"
COLUMNS = ["res_id", "company_id", "fields_id"]
INDEX_START = 100

combinations = []
for i in range(1, len(COLUMNS) + 1):
    combinations.extend(itertools.combinations(COLUMNS, i))

permutations = set(itertools.permutations(COLUMNS))

comb_perm = set(combinations) | permutations
drop_indexes = []
for num, item in enumerate(sorted(comb_perm)):
    index_name = f"borrar{num + INDEX_START}"
    print(f"\nCREATE INDEX {index_name} ON {TABLE} ({', '.join(item)});")
    print(f"REINDEX INDEX {index_name}; -- if autovacuum is off")
    drop_indexes.append(f"DROP INDEX {index_name};")

NL = "\n"
print(f"\n-- Run after testing\n{NL.join(drop_indexes)}")
