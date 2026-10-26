from bs4 import BeautifulSoup

# file = "C:\\Gredow\\Liceo\\Horario\\2024-2025\\profesores.html"
#
# file_salida = "C:\\Gredow\\Liceo\\Horario\\2024-2025\\profesores_modificado.html"

file = "C:\\Gredow\\Liceo\\Horario\\2025-2026\\profesores.html"
file_salida = "C:\\Gredow\\Liceo\\Horario\\2025-2026\\profesores_modificado.html"


# Abrir el archivo HTML original
with open(file, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Encontrar todas las tablas
tables = soup.find_all('table')

# Iterar sobre las tablas
for table in tables:
    # Tratar de encontrar tbody, si no lo encuentra, usar la tabla directamente
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
    else:
        rows = table.find_all('tr')

    # Variable para asegurar que se reemplaza la primera "---" en la última columna con "Reunión con Padres"
    replaced_meeting = False
    # Contador para alternar entre "Planificación" y "Trabajo de Registro"
    alternator = 0

    # Iterar sobre las filas
    for row in rows:
        cells = row.find_all('td')  # Buscar todas las celdas de cada fila

        # Iterar sobre las celdas
        for i, cell in enumerate(cells):
            if cell.text.strip() == "---" or cell.text.strip() == "-x-":  # Si el contenido de la celda es "---"
                # Verificar si estamos en la última columna y no se ha reemplazado ya por "Reunión con Padres"
                if i == len(cells) - 1 and not replaced_meeting:
                    cell.string = "Reunión con Padres"
                    replaced_meeting = True
                else:
                    # Alternar entre "Planificación" y "Trabajo de Registro"
                    if alternator % 2 == 0:
                        cell.string = "Planificación"
                    else:
                        cell.string = "Trabajo de Registro"
                    alternator += 1

# Guardar el archivo HTML modificado
with open(file_salida, 'w', encoding='utf-8') as f:
    f.write(str(soup))

print("Archivo HTML modificado generado exitosamente.")

