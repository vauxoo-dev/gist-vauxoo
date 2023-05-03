import os
import subprocess
from openpyxl import Workbook

# Cambiar el directorio a donde se encuentra el repositorio
repo_path = "/Users/moylop260/odoo/villagroup"
os.chdir(repo_path)

# Fecha de inicio y fin del ciclo
start_date = "2022-01-01"
end_date = "2023-05-01"
branch = 15.0

# Convertir las fechas a formato de Git
start_date_git = f"{start_date} 00:00:00"
end_date_git = f"{end_date} 23:59:59"

# Crear el libro de Excel y la hoja de resumen
workbook = Workbook()
summary_sheet = workbook.active
summary_sheet.title = "Resumen"
summary_sheet.append(["Fecha", "Líneas de código"])

# Realizar el ciclo para cada mes
current_date = start_date
while current_date < end_date:
    print(" ".join(["git", "rev-list", "-n", "1", f'--before="{current_date}"', f'{branch}']))
    result = subprocess.run(["git", "rev-list", "-n", "1", f'--before="{current_date}"', f'{branch}'], capture_output=True, text=True)
    git_sha = result.stdout.strip().split("\n")[0]
    print(f"git sha: {git_sha}")

    # Checkout del repositorio en la fecha actual
    # print(" ".join(["git", "reset", "--hard", f"{git_sha}"]))
    # subprocess.run(["git", "reset", "--hard", f"{git_sha}"])
    subprocess.run(["git", "checkout", f"{git_sha}"])


    # Ejecutar el comando para obtener el cloc
    result = subprocess.run(["cloc", "--csv", "--vcs=git", "--by-file", "."], capture_output=True, text=True)
    # Guardar el resultado en una hoja de Excel
    sheet_name = f"{current_date[:7]}"
    sheet = workbook.create_sheet(title=sheet_name)

    header = result.stdout.strip().split("\n")[5]
    sheet.append(header.split(","))
    for line in result.stdout.strip().split("\n")[6:]:
        sheet.append(line.split(","))

    # Actualizar la fecha actual al siguiente mes
    year, month, day = map(int, current_date.split("-"))
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    current_date = f"{year:04}-{month:02}-{day:02}"

# Guardar el libro de Excel
workbook.save("/tmp/cloc_results.xlsx")
