-- The following are just examples of what you could do at setup.
-- Obviously they are not going to work in general: you have to find out
-- the correct ids by playing around with psql
-- >> ONLY RUN THIS ON DEMO DATA! <<

-- 1. Example for record rules
-- Remove record rules with Read-Only Analyst and Own Areas Viewer
UPDATE ir_rule SET active=false WHERE id in (297,298,299,301,302,303);

-- 2. Example for cache
-- Sets all the views to non-cached to avoid -u's in development
UPDATE ir_ui_view SET cache_db=false;

-- 3. Example for groups
-- Adds Mitchell Admin to the groups:
--     Orphan Management Admin group
--     Can see invoice buttons
-- Removes him from:
--     Can not see actions
INSERT INTO res_groups_users_rel (gid, uid) VALUES
    (101, 2), (103, 2), (104, 2), (105, 2), (106, 2), (107, 2), (110, 2), (192, 2);
DELETE FROM res_groups_users_rel WHERE gid=111 and uid=2;

-- 4. Example of setting a password with TOTP
-- Sets the password of the portal user Joel Willis
-- username: portal
-- password: Vauxoo123!
-- totp:
--     import pyotp
--
--     totp = pyotp.TOTP('5GA7QXAFRWVB4MAYKGTXESSIZN7SOITQ')
--     totp.now()
UPDATE res_users SET password='$pbkdf2-sha512$600000$5fz/vxfC.F/rvReiNEYIYQ$pcpir31GgIVuf8XzywSh.ocWcoTSbGV/oxFvNmD5XNNW1kHn6h23pG7xAqxJMfedv2Z24CPGYgY7e1A7uOVVog',totp_secret='5GA7QXAFRWVB4MAYKGTXESSIZN7SOITQ' WHERE id=7;
