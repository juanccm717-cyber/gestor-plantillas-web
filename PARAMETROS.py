# --- LISTA DE CÓDIGOS PRESTACIONALES CATEGORIZADA Y ACTUALIZADA ---
CODIGOS_PRESTACIONALES_CATEGORIZADOS = [
    # (La lista larga de códigos prestacionales que ya tienes... no la repito aquí para brevedad)
    {"categoria": "POR ASIGNAR", "codigo": "301", "descripcion": "Cuidado Integral de salud del Niño"},
    # ... y así sucesivamente hasta el final.
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "114", "descripcion": "Sepelio para Adolescentes y Adultos"},
]

# --- DICCIONARIO DE ACTIVIDADES PREVENTIVAS ---
ACTIVIDADES_PREVENTIVAS_MAP = {
    "003": "003: Peso (Kg)", "004": "004: Talla (cm.)", "014": "014: IMC (kg/m2)", "015": "015: PAB (cm.)",
    "301": "301: P.A. (mmHg)", "400": "400: EEDP/TEPSI/TA", "019R": "019: Recién Nacido Prematuro",
    "020": "020: Bajo peso al nacer", "021": "021: Enfermedad Congénita/ Secuelas de nacimiento",
    "307": "307: Consejería Nutricional", "407": "407: Tamizaje de Salud Mental",
    "018A": "018: Valoración Clínica del Adulto Mayor (VACAM) anual",
    "401": "401: Evaluación Integral de Salud del joven o adulto anual (Eval. Joven y Adulto)",
    "013I": "013: Consejería Integral", "408": "408: Parto Vertical", "417": "417: Control Prenatal Reenfocado",
    "409": "409: Corte Tardío de Cordón (2 a 3 min)", "102": "102: Vacuna contra BCG", "117": "117: Vacuna contra DPT",
    "316": "316: Vacuna contra Antipolio Inactivada inyectable (IPV)", "313": "313: Vacuna contra Antipolio Oral (APO)",
    "317": "317: Vacuna contra Sarampión y Rubeola (SR)", "125": "125: Vacuna contra Sarampión, Paperas y Rubéola (SPR)",
    "411": "411: Vacuna contra la varicela", "315": "315: Vacuna contra la Hepatitis B en recién nacidos (HVB)",
    "403": "403: Vacuna contra la Hepatitis B (HVB) mayores de 5 años", "323": "323: Vacuna contra HIB / VPH",
    "127": "127: Vacuna contra Rotavirus", "324": "324: Vacuna Toxoide Diftotetano Pediátrico - DT",
    "325": "325: Vacuna contra DT Adultos", "412": "412: Vacuna dPta para gestante", "124": "124: Vacuna Pentavalente",
    "211": "211: Vacuna Anti Amarílica (AMA)", "126": "126: Vacuna contra Neumococo", "405": "405: Vacuna contra Influenza",
    "413": "413: Vacuna contra el Virus de la Hepatitis A (HVA)", "414": "414: HB.Glicosilada (mg/dL)",
    "415": "415: Dosaje de albúmina en orina (ug/mL)", "416": "416: Depuración de creatinina (mL/min)",
    "404": "404: Número de acompañantes de la Gestante o puérpera en casa materna",
    "300A": "300: CPN", "005E": "005: Edad Gestacional (Embarazo/RN en Semanas)",
    "010U": "010: Altura Uterina", "304": "304: Edad Gest RN (Semanas)",
    "305": "305: APGAR 1°", "306": "306: APGAR 5°", "209": "209: Control de Puerperio"
}

# --- RELACIÓN ENTRE CÓDIGO PRESTACIONAL Y ACTIVIDADES ---
RELACION_CODIGO_ACTIVIDADES = {
    "001": ["003", "004", "014", "015", "400"],
    "002": ["019R", "020", "021"],
    "005": ["307"],
    "022": ["407"],
    "903": ["018A"],
    "904": ["401"],
    "018": ["013I"],
    "054": ["408", "409"],
    "009": ["417", "003", "301", "005E", "010U", "013I"],
    "050": ["304", "305", "306", "003", "004", "315"],
    "010": ["209", "301", "013I"],
    "024": ["414", "415", "416"],
    "060": ["404"]
}
