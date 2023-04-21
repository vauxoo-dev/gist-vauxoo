import polib

# Load the .po file
filename = "es.po"
po = polib.pofile(filename)

# Iterate over each entry in the .po file
same_translation = []
for entry in po:
    # If the translated term is the same as the source term, save it for later
    if entry.msgid == entry.msgstr:
        same_translation.append(entry.msgid)

# Read content of .po file
with open(filename) as po_file:
    po_content = po_file.read()

# Clear translations when they match original term. This is not done by saving the original file because
# this is meant for old files where lines are not wrapped
for term in same_translation:
    # We need to escape double quotes
    term = term.replace('"', '\\"')
    # and to make newlines to break the string
    term = term.replace("\n", '\\n"\n"')
    po_content = po_content.replace(f'msgstr "{term}"', f'msgstr ""')

# Save the result
with open(filename, "w") as po_file:
    po_file.write(po_content)
