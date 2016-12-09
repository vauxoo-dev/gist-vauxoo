-- Check that the auth_signup_reset_password parameter is enabled
UPDATE base_config_settings SET auth_signup_reset_password=true WHERE id=(
    SELECT MAX(id) FROM base_config_settings
);
INSERT into base_config_settings(auth_signup_reset_password)
    SELECT true WHERE NOT EXISTS (SELECT 1 FROM base_config_settings);

-- Create a token for the administrator to reset password
UPDATE res_partner
    SET signup_type='reset',
        signup_token='rsvabcdefghijykalklk',
        signup_expiration=to_timestamp('20200411','YYYYMMDD')
    WHERE id = (SELECT partner_id FROM res_users WHERE id=1);
-- Now login to reset the administrator password
\echo 'http://my.odoo.server:port/web/reset_password?token=rsvabcdefghijykalklk&login=admin'
