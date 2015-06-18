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
