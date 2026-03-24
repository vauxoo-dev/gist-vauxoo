"""
Script to output all views that don't whose file name doesn't match their model name.
"""

import re
from pathlib import Path

pattern = re.compile(
    r"<field name=['\"](?:model|res_model)['\"]>([^<]+)*</field>"
)

directories = ["view", "views", "wizard", "wizards"]
for directory in directories:
    for xml_path in sorted(Path(directory).rglob("*.xml")):
        lines = xml_path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            model_line = pattern.search(line)
            if not model_line:
                continue

            model = model_line.group(1)
            expected_filename = model.replace(".", "_") + "_views.xml"
            if xml_path.name != expected_filename:
                print(f"{xml_path.name}:{lineno}: model {model} should belong to the file {expected_filename}")
