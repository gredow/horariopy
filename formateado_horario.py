import io

import numpy as np;
import codecs

# ruta_salvado = 'C:\\Gredow\\HORARIO LOS TOROS 2024-2025\\'
# ruta_raw = r'C:\Users\User\fet-results\timetables\HORARIO LOS TOROS 2024-2025-single'
#
nombre_centro = 'Liceo Ana Elpidia Sánchez'

ruta_salvado = 'C:\\Gredow\\Liceo\\Horario\\2025-2026\\'
ruta_raw = r'C:\Users\User\fet-results\timetables\ANA ELPIDIA SANCHEZ 2025-2026-single'

# ruta_salvado = 'C:\\Gredow\\Documentos centro\\Horario Blady\\HORARIO LOS TOROS 2025-2026\\'
# ruta_raw = r'C:\Users\User\fet-results\timetables\HORARIO LOS TOROS 2025-2026-single'

# nombre_centro = 'Liceo Los Toros'

destino_estudiantes = 'estudiantes.html'
destino_profesores = 'profesores.html'

nombres_profesores=[
"Eddy Wilson Díaz Sánchez",
"Miguelina Díaz",
"Franny Reyemic Ramirez De Fernández",
"Johanna Altagracia Pujols de Feliz",
"Leandro Díaz Díaz",
"Navidad Del Jesús Sánchez Sánchez",
"Romilia Féliz Morón",
"Prof. Inglés",
"Mario Moreno Pérez Paula",
"Prof. Informática",
"Darlenny Custodio",
"Eridania Marte",
"Rosa Naut",
"César Méndez Beltré",
"Geraldo Sánchez Cuevas",
"Arnaldo Andrés Agramonte Carrasco",
"Mirely Geraldo",
"Prof. Francés Tercero",
"Profe. Educación Física",
"Elsa Jonmari Tejeda",
"Luz Maria",
"Emelin Stephany Santana Concepción",
"Yadiela Féliz",
"Rosa María Sención",
"Prof. Inglés",
"Smarlin Ramírez",
"Miulca Janogui Peguero Barreiro",
"Prof. Matemática",
"Luchy Margarita De la Cruz",
"Rosmerys Lebrón García",
"Anny Sugeidy Rossó Hernández",
"Jacinto Féliz",
"DEISI MILAGROS PIMENTEL",
"MIRELLA DE LEÓN",
"MARY E. ESCALANTE",
"MELANIA ESCALANTE",
"JORGE ERADYS MINYETI",
"MAESTRO EN PROYECTO",
"LUISAS ZAYAS",
"MERALIS ESCALANTE",
"ANDREA MAÑÓN",
"DOMINGA DE LEÓN",
"DOMINGA FÉLIZ",
"CAROLINA",
"HUMBERTO CÉSPEDES",
"ELADIO DE LEÓN",
"CARMEN MEJÍA",
"ROLANDO MÉNDEZ",
"ANEUDY FÉLIZ",
"GEORGINA RODRÍGUEZ",
"MANUELA REYES MÉNDEZ",
"BLADIMIL PEREZ",
"MAESTRO MATEMÁTICA X",
"YENIFER DANIELISA JIMENEZ QUEZADA",
"YOKAIRA MARISOL AGRAMONTE PUJOLS",
"EUNICE PÉREZ FIGUEREO",
"CINTHIA ELIZABETH PINEDA AYBAR",
"YISSETT ESMERALDA MARTINEZ TAPIA",
"PROF. EDUCACIÓN FISICA",
"PROF. FRANCÉS",
"PROF. TALLERES 1",
"PROF. TALLERES 2",
"MARÍA NICAURIS MÉNDEZ",
]

def replace_brake(miarray, hora, texto):
    p = [i for i, item in enumerate(miarray) if hora in item]
    for m in p:
        for i in range(1, 6):
            miarray[m + i] = miarray[m + i].replace('-X-', texto);

def dividir2(archivo, nombre, ruta_salvado,nombre_css,tipo):
    f = io.open(archivo, encoding='utf-8')
    lineas = f.readlines()
    if tipo == 'p':
        for i,linea in enumerate(lineas):
            if('teacher line0' in linea):
                for profesor in nombres_profesores:
                    if(profesor in linea):
                        lineas[i] = lineas[i].replace(profesor, '').replace(f'<div class="teacher line0"><span class="t_9" onmouseover="highlight(\'t_9\')"></span>, <span class="t_19" onmouseover="highlight(\'t_19\')"></span></div>','')
                        # print(lineas[i])

    g = ''.join(lineas)

    index = [idx for idx, s in enumerate(lineas) if 'Horario generado con ' in s][0]
    texto_generacion = lineas[index]


    if tipo == 'e':
        for profesor in nombres_profesores:
            g = g.replace(profesor,'')

    g = g.replace('NORMAL', '').replace('SALIDA','<BR>SALIDA').replace('TALLER','<BR>TALLER')\
        .replace(nombre_css,'styles.css').replace(r'<p class="back"><a href="#top">Volver al principio</a></p>','')\
        .replace('</table>','</table> salto777')\
        .replace(texto_generacion,'')\
        .replace(f'<caption>'+nombre_centro+'</caption>','')

    g = g.replace("03:15","03:15<br>04:00")
    g = g.replace("02:30","02:30<br>03:15")
    g = g.replace("02:15","02:15<br>02:30")
    g = g.replace("01:30","01:30<br>02:15")
    g = g.replace("14:45","14:45<br>01:30")
    g = g.replace("12:45","12:45<br>01:30")
    g = g.replace("11:45","11:45<br>12:45")
    g = g.replace("11:00","11:00<br>11:45")
    g = g.replace("10:15","10:15<br>11:00")
    g = g.replace("09:45","09:45<br>10:15")
    g = g.replace("09:00","09:00<br>09:45")
    g = g.replace("08:15","08:15<br>09:00")

    a = np.array(g.split('\n'))

    # Cambiar las -X- de las paradas
    replace_brake(a, '9:45', 'RECREO')
    replace_brake(a, '11:45', 'ALMUERZO')
    replace_brake(a, '2:15', 'RECESO')

    # Dividir celdas
    j = [i for i, item in enumerate(a) if 'rowspan="2"' in item]
    k = [i for i, item in enumerate(a) if '<!-- span -->' in item]
    n = 0
    for m in j:
        if a[m - 1] != '      <thead>':
            a[m] = a[m].replace('rowspan="2"', '')
            a[k[n]] = a[m]
        n = n + 1

    # Convertir el array a string
    z = '\n'.join(a)

    # Salvar a archivo
    archivo_gurdar = ruta_salvado + nombre
    with open(archivo_gurdar, 'w', encoding='utf-8') as text_file:
        text_file.write(z);

inicial_nombre = ""
corte = ruta_raw.split("\\")
count = len(corte)
if("-multi" in ruta_raw):
    inicial_nombre = corte[len(corte) - 3].replace("-multi", "")
    b = corte[count -3]
    a = ruta_raw.split("\\")
    print(inicial_nombre)
else:
    inicial_nombre = corte[-1].replace("-single", "")

estilo = inicial_nombre + "_stylesheet.css"

# raw_estudiante =  r'D:\Liceo\Horarios 2021-2022\mayo 2022\estudiantesraw.html'
# raw_profesores = r'D:\Liceo\Horarios 2021-2022\mayo 2022\profesoresraw.html'
raw_estudiante =  ruta_raw +"\\" + inicial_nombre + "_subgroups_days_horizontal.html"
raw_profesores = ruta_raw +"\\" + inicial_nombre + "_teachers_days_horizontal.html"

a = 'C:\\Users\\eliec\\fet-results\\timetables\\AES-2021-2022 mayo 2022-single\\AES-2021-2022 mayo 2022_teachers_days_horizontal.html'
a = 'C:\\Users\\eliec\\fet-results\\timetables\\AES-2021-2022 mayo 2022-single\\AES-2021-2022 mayo 2022-single_subgroups_days_horizontal.html'



dividir2(raw_estudiante, destino_estudiantes, ruta_salvado,estilo,tipo='e')
dividir2(raw_profesores, destino_profesores, ruta_salvado,estilo,tipo='p')