import xml.etree.ElementTree as ET
# ruta = f"C:\\Gredow\\HORARIO LOS TOROS 2024-2025\\"
#
# nombre_archivo_fet = "HORARIO LOS TOROS 2024-2025.fet"

ruta = f"C:\\Gredow\\Liceo\\Horario\\2025-2026\\"
# ruta = f"C:\\Gredow\\Liceo\\Horario\\Liceo 2\\"

nombre_archivo_fet = "ANA ELPIDIA SANCHEZ 2025-2026.fet"


archivo_fet = ruta + nombre_archivo_fet

archivo_html = ruta + "carga_maestros.html"


tree = ET.parse(archivo_fet)
root = tree.getroot()

def get_all_teachers():
    teacher_list = []
    for teacher in root.find(".//Teachers_List").findall(".//Teacher"):
        teacher_list.append(teacher[0].text)
    return teacher_list

def get_all_students():
    subgroup_list = []
    for subgroup in root.find(".//Students_List").findall(".//Subgroup"):
        subgroup_list.append(subgroup[0].text)
    return subgroup_list

def get_activities():
    activities = {}
    for activity in root.findall(".//Activity"):
        teachers_list = []
        for teacher in activity.findall(".//Teacher"):
            teachers_list.append(teacher.text)
        cantidad = len(teachers_list)
        activities[int(activity[6+cantidad-1].text)] = {'activity_group_id':int(activity[7+cantidad-1].text),
                           'teachers':teachers_list, 'subject':activity[1+cantidad-1].text,
                            'students':activity[3+cantidad-1].text,'activity_tag':activity[2+cantidad-1].text,
                           'duration':int(activity[4+cantidad-1].text),'active':activity[8+cantidad-1].text}
    return activities

def get_restricciones_horas():
    lista_restricciones = {}
    activities = get_activities()
    for constraint in root.findall(".//ConstraintActivityPreferredStartingTimes"):
        activity_id = int(constraint[1].text)
        active = constraint[-2]
        activity_data = activities[activity_id]
        times = []
        for preferred_starting_time in constraint.findall(".//Preferred_Starting_Time"):
            times.append([preferred_starting_time[0].text,preferred_starting_time[1].text])
        dias_unicos = []
        for horario_item in times:
            dia = horario_item[0]
            if dia not in dias_unicos:
                dias_unicos.append(dia)
        clave_dias = 'O'
        if set(['Lunes', 'Martes', 'Miércoles', 'Jueves']).issubset(dias_unicos):
            if 'Viernes' not in dias_unicos:
                clave_dias = 'L-J'
            else:
                clave_dias = 'L-V'
        lista_restricciones[int(constraint[1].text)] = {**{'activity_id':activity_id}, **activity_data,
                                                        **{'dias':dias_unicos,'clave_dias':clave_dias},**{'active':active}}

    return lista_restricciones

def get_restricciones_by_subgroup():
    lista_restricciones = get_restricciones_horas()
    restricciones_dict = {}

    for students in get_all_students():
        restricciones_dict[students] = []

    for restricion in lista_restricciones:
        if lista_restricciones[restricion]['active'].text == 'true':
            restricciones_dict[lista_restricciones[restricion]['students']].append(
                {'subject':lista_restricciones[restricion]['subject'],
                 'teachers': lista_restricciones[restricion]['teachers'],
                 'duration': lista_restricciones[restricion]['duration'],
                 'clave_dias': lista_restricciones[restricion]['clave_dias'],
                 }
            )

    for students in get_all_students():
        restricciones_dict[students] = sorted(restricciones_dict[students], key=lambda x: (x['clave_dias'],x['subject']))


    return restricciones_dict

def get_restricciones_by_teacher():
    lista_restricciones = get_restricciones_horas()
    restricciones_dict = {}

    for teacher in get_all_teachers():
        restricciones_dict[teacher] = []

    for restricion in lista_restricciones:
        if lista_restricciones[restricion]['active'].text == 'true':
            for teacher in lista_restricciones[restricion]['teachers']:
                restricciones_dict[teacher].append(
                    {'subject':lista_restricciones[restricion]['subject'],
                     'students': lista_restricciones[restricion]['students'],
                     'duration': lista_restricciones[restricion]['duration'],
                     'clave_dias': lista_restricciones[restricion]['clave_dias'],
                     }
                )

    for teacher in get_all_teachers():
        restricciones_dict[teacher] = sorted(restricciones_dict[teacher], key=lambda x: (x['clave_dias'],x['students']))
    return restricciones_dict

def create_carga_maestros():
    teachers = {}

    for teacher in root.find(".//Teachers_List").findall(".//Teacher"):
        teachers[teacher[0].text] = []

    used_group_id = [0]
    # Recorrer cada elemento "Activity" en el XML
    for activity in root.findall(".//Activity"):
        group_id = int(activity.find(".//Activity_Group_Id").text)
        if group_id == 0 or group_id not in used_group_id:
            used_group_id.append(int(group_id))
            teacher_name = activity.find(".//Teacher").text
            subject = activity.find(".//Subject").text
            activity_tag = activity.find(".//Activity_Tag").text
            students = activity.find(".//Students").text
            total_duration = int(activity.find(".//Total_Duration").text)
            teachers[teacher_name].append({'subject': subject, 'activity_tag': activity_tag, 'students': students,
                                           'total_duration': total_duration})
            # print(group_id)

    # Crear una cadena HTML
    html = "<html>\n"
    html += "<head>\n"

    html += '<title>Liceo Ana Elpidia Sánchez</title>'
    html += '<link rel="stylesheet" media="all" href="estilo_carga_maestros.css" type="text/css" />'

    html += "</head>\n"
    html += "<body>\n"
    html += "<table>\n"
    html += "\t<tr>\n"
    html += "\t\t<th>Maestros</th>\n"
    html += "\t\t<th>Asignaturas</th>\n"
    html += "\t\t<th>Horas Totales</th>\n"
    html += "\t</tr>\n"

    for teacher, subjects in teachers.items():
        html += "\t<tr>\n"
        html += f"\t\t<td>{teacher}</td>\n"
        html += "\t\t<td>\n"
        html += "\t\t\t<ul>\n"
        horas = 0
        for subject in subjects:
            horas += subject['total_duration']
            subject_info = f"{subject['subject']}, {subject['activity_tag']}, {subject['students']}, {subject['total_duration']} horas"
            html += f"\t\t\t\t<li>{subject_info}</li>\n"
        html += "\t\t\t</ul>\n"
        html += "\t\t</td>\n"
        html += f"\t\t<td>{horas} Horas</td>\n"
        html += "\t</tr>\n"

    html += "</table>\n"
    html += "</body>\n"
    html += "</html>"

    with open(archivo_html, "w+") as f:
        f.writelines(html)



def format_duration(duration):
    return f'{duration} horas'

def get_html_detalle_restricciones():
    diccionario_subgroup = get_restricciones_by_subgroup()
    diccionario_teacher = get_restricciones_by_teacher()
    html = ''
    for teacher, materias in diccionario_subgroup.items():
        html += f'<h1>{teacher}</h1>'
        html += '<table border="1">'
        html += '<tr><th>Materia</th><th>Profesor</th><th>Duración</th><th>Días</th><th>Sum L-J</th><th>Sum L-V</th></tr>'
        sum_l_j = 0
        sum_l_v = 0

        for materia in materias:
            teacher = ', '.join(materia["teachers"])
            if materia["clave_dias"] == 'L-J':
                sum_l_j += materia["duration"]
            if materia["clave_dias"] == 'L-V':
                sum_l_v += materia["duration"]
            html += f'<tr><td>{materia["subject"]}</td><td>{teacher}</td><td>{format_duration(materia["duration"])}' \
                    f'</td><td>{materia["clave_dias"]}</td></td><td>{sum_l_j}</td><td>{sum_l_v}</td></tr>'
        html += '</table>'

    # Imprimir el HTML generado
    with open(ruta + 'restricciones-estudiantes.html', "w+") as f:
        f.writelines(html)

    html = ''
    for teacher, materias in diccionario_teacher.items():
        html += f'<h1>{teacher}</h1>'
        html += '<table border="1">'
        html += '<tr><th>Materia</th><th>Curso</th><th>Duración</th><th>Días</th><th>Sum L-J</th><th>Sum L-V</th></tr>'
        sum_l_j = 0
        sum_l_v = 0

        for materia in materias:
            if materia["clave_dias"] == 'L-J':
                sum_l_j += materia["duration"]
            if materia["clave_dias"] == 'L-V':
                sum_l_v += materia["duration"]
            html += f'<tr><td>{materia["subject"]}</td><td>{materia["students"]}</td><td>{format_duration(materia["duration"])}' \
                    f'</td><td>{materia["clave_dias"]}</td></td><td>{sum_l_j}</td><td>{sum_l_v}</td></tr>'
        html += '</table>'

    # Imprimir el HTML generado
    with open(ruta + 'restricciones-profesores.html', "w+") as f:
        f.writelines(html)