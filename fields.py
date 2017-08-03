diff --git openerp/fields.py openerp/fields.py
index cc8563510..025a4e12f 100644
--- openerp/fields.py
+++ openerp/fields.py
@@ -934,6 +934,8 @@ class Field(object):
                 self.compute_value(record)
             else:
                 recs = record._in_cache_without(self)
+                if len(recs) > PREFETCH_MAX:
+                    recs = recs[:PREFETCH_MAX] | record
                 self.compute_value(recs)
•
         else:
@@ -1914,5 +1916,5 @@ class Id(Field):
 # imported here to avoid dependency cycle issues
 from openerp import SUPERUSER_ID
 from .exceptions import Warning, AccessError, MissingError
-from .models import BaseModel, MAGIC_COLUMNS
+from .models import BaseModel, MAGIC_COLUMNS, PREFETCH_MAX
 from .osv import fields
