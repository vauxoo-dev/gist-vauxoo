-- When the part of hostname into message_id not correspond with the current hostname
-- the received messages into Odoo are not associated with corresponding thread 
-- With this script we can to update hostname into message_id to keep the expected behavior
-- e.g.
-- message_id with old hostname 'vauxoo70'
-- <1415205837.104161977767944.602270230993340-openerp-2480-project.task@vauxoo70>
-- message_id after to execute script with new hostname
--<1415205837.104161977767944.602270230993340-openerp-2480-project.task@vauxoo70.vauxoo.com>


UPDATE mail_message
SET message_id = new_message_id
FROM (
	SELECT id, 
	   regexp_replace(message_id, '@.*>$', '@' || current_hostname || '>') AS new_message_id
	FROM mail_message
	INNER JOIN (
		SELECT TEXT(
		-- We need to change this value by the value of HostName
			'vauxoo70.vauxoo.com'
		) AS current_hostname
	    ) var 
	    ON 1=1
	 WHERE message_id NOT LIKE '%@' || current_hostname || '>' 
	   AND message_id <> 'True'
) subvw
WHERE mail_message.id = subvw.id
