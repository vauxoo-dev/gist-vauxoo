"""
Upload a database backup to odoo to be migrated, via sftp
"""

import json
import os
import requests
import sys

# Script parameters
BASE_URL = "https://upgrade.odoo.com"
ENTERPRISE_CODE = "M120123123-abcd"
EMAIL = " lgonzalez@vauxoo.com"
TARGET_VERSION = "13.0"
DB_FILENAME = "vauxoo120_mig.sql.gz"
IS_FOR_TESTING = True

# Read SSH public keys
ssh_keys_path = os.path.expanduser("~/.ssh/id_rsa.pub")
with open(ssh_keys_path) as keys_file:
    ssh_keys = keys_file.read().strip()

# Create an Odoo request for uploading the BD
create_url = "%s/database/v1/create" % BASE_URL
url_params = {
    "contract": ENTERPRISE_CODE,
    "target": TARGET_VERSION,
    "email": EMAIL,
    "filename": DB_FILENAME,
    "aim": "test" if IS_FOR_TESTING else "production",
}
print("Creating the request")
response = requests.get(create_url, url_params)
response.raise_for_status()
json_response = response.json()
if json_response.get('failures'):
    sys.exit(json_response['failures'])

# Request access to connect via sftp
request_access_sftp_url = "%s/database/v1/request_sftp_access" % BASE_URL
key = json_response['request']['key']
request_id = json_response['request']['id']
url_params = {"key": key, "request": request_id}
file_params = {"ssh_keys": ssh_keys}
print("Requesting SFTP access")
response = requests.post(request_access_sftp_url, url_params, files=file_params)
response.raise_for_status()
json_response = response.json()
if json_response.get('failures'):
    sys.exit(json_response['failures'])

# Upload file via sftp
ssh_options = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
sftp_cmd = json_response['request']['sample_command'].replace(
    'sftp ', 'sftp -b - %s ' % ssh_options)
sftp_cmd = "echo 'progress\nput %s %s' | %s" % (DB_FILENAME, DB_FILENAME, sftp_cmd)
print("Uploading dump file using:\n%s" % sftp_cmd)
os.system(sftp_cmd)

# Ask Odoo to process the database
process_url = "%s/database/v1/process" % BASE_URL
url_params = {"key": key, "request": request_id}
print("Asking to start the migration process")
response = requests.get(process_url, url_params)
response.raise_for_status()
json_response = response.json()
if json_response.get('failures'):
    sys.exit(json_response['failures'])

# Print result
status_url = "%s/database/v1/status" % BASE_URL
response = requests.get(status_url, url_params)
response_pretty = json.dumps(json_response, indent=4)
print("Migration request has been sent\nReceived result: %s" % response_pretty)
