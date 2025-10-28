# ==============================================================================
#                           BLOQUE DE IMPORTACIONES (CORREGIDO)
# ==============================================================================

# --- Librerías Estándar de Python ---
import os
import re
from datetime import datetime, timedelta

# --- Librerías de Terceros (Instaladas) ---
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response, flash
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from fpdf import FPDF
import bcrypt

# ==============================================================================




# --- CONFIGURACIÓN DE LA BASE DE DATOS REAL (SUPABASE) ---
load_dotenv() # Carga las variables desde el archivo .env

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("La variable de entorno DATABASE_URL no está configurada.")
    
engine = create_engine(DATABASE_URL)
# ---------------------------------------------------------

# --- IMPORTACIÓN DE LISTAS ESTÁTICAS ---
# ==============================================================================
#  Este archivo contiene todas las listas de datos estáticos para la aplicación.
# ==============================================================================

# --- LISTA COMPLETA DE CÓDIGOS PRESTACIONALES ---
CODIGOS_PRESTACIONALES_CATEGORIZADOS = [
    {"categoria": "POR ASIGNAR", "codigo": "301", "descripcion": "Cuidado Integral de salud del Niño"},
    {"categoria": "POR ASIGNAR", "codigo": "302", "descripcion": "Cuidado Integral de salud del Adolescente"},
    {"categoria": "POR ASIGNAR", "codigo": "303", "descripcion": "Cuidado Integral de salud del Joven"},
    {"categoria": "POR ASIGNAR", "codigo": "304", "descripcion": "Cuidado Integral de salud del Adulto"},
    {"categoria": "POR ASIGNAR", "codigo": "305", "descripcion": "Cuidado Integral de salud del Adulto Mayor"},
    {"categoria": "POR ASIGNAR", "codigo": "306", "descripcion": "Cuidado Integral de salud Prenatal"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "002", "descripcion": "Control del recién nacido con menos de 2,500 gr, prematuro, con secuelas al nacer"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "029", "descripcion": "Tamizaje Neonatal"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "001", "descripcion": "Control de crecimiento y desarrollo en menores entre 0 - 4 años"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "118", "descripcion": "Control de crecimiento y desarrollo en menores entre 5 - 9 años"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "119", "descripcion": "Control de crecimiento y desarrollo en entre de 10 - 11 años"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "016", "descripcion": "Atención temprana para menores de 36 meses"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "007", "descripcion": "Suplemento de micronutrientes"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "005", "descripcion": "Consejería nutricional para niñas o niños en riesgo nutricional y desnutrición"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "008", "descripcion": "Profilaxis antiparasitaria"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "019", "descripcion": "Detección trastorno agudeza visual y ceguera"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "017", "descripcion": "Atención Integral del adolescente"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "020", "descripcion": "Salud Bucal"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "021", "descripcion": "Prevencion de caries"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "022", "descripcion": "Detección de problemas en Salud Mental"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "009", "descripcion": "Atención prenatal"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "010", "descripcion": "Atención del puerperio normal"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "011", "descripcion": "Exámenes de laboratorio completo de la gestante"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "023", "descripcion": "Deteccion precoz de cancer de prostata (PSA)"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "025", "descripcion": "Detección precoz de cancer de mama (Mamografía)"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "013", "descripcion": "Exámenes de ecografía obstétrica"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "015", "descripcion": "Diagnóstico del embarazo"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "024", "descripcion": "Detección precoz de cáncer cérvico-uterino"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "018", "descripcion": "Salud reproductiva (planificación familiar)"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "902", "descripcion": "Atención Preconcepcional"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "903", "descripcion": "Atenciòn Integral de Salud del Adulto Mayor"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "904", "descripcion": "Atención Integral de Salud del Joven y Adulto"},
    {"categoria": "ACTIVIDAD PREVENTIVA", "codigo": "911", "descripcion": "Instrucción de Higiene Oral y Asesoría nutricional para el control de enfermedades dentales"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "050", "descripcion": "Atención inmediata del recién nacido normal"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "051", "descripcion": "Internamiento del RN con patología no quirurgica"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "052", "descripcion": "Internamiento con intervención quirúrgica del RN"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "054", "descripcion": "Atención de parto vaginal"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "055", "descripcion": "Cesárea"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "906", "descripcion": "Consulta externa por profesionales no médicos ni odontólogos"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "056", "descripcion": "Consulta externa"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "057", "descripcion": "Obturación y curación dental simple"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "058", "descripcion": "Obturación y curación dental compuesta"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "059", "descripcion": "Extracción dental (exodoncia)"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "060", "descripcion": "Atención extramural urbana y periurbana (Visita domiciliaria)"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "075", "descripcion": "Atención extramural rural (Visita domiciliaria)"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "061", "descripcion": "Atención en tópico"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "062", "descripcion": "Atención por emergencia"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "063", "descripcion": "Atención por emergencia con observación"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "064", "descripcion": "Intervención medico-quirúrgica ambulatoria"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "065", "descripcion": "Internamiento en EESS sin intervención quirúrgica"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "066", "descripcion": "Internamiento con intervención quirúrgica menor"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "067", "descripcion": "Internamiento con intervención quirúrgica mayor"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "068", "descripcion": "Internamiento con Estancia en la Unidad de Cuidados Intensivos (UCI)"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "069", "descripcion": "Transfusión sanguínea o hemoderivados"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "070", "descripcion": "Atención odontológica especializada"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "027", "descripcion": "Tratamiento profilactico a niños expuestos al VIH"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "053", "descripcion": "Tratamiento de VIH-SIDA (0-19a)"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "074", "descripcion": "Prevención, detección y tratamiento de ITS en adolescentes, jóvenes, adultos y adultos mayores"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "S01", "descripcion": "(****) Complementario"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "026", "descripcion": "Tratamiento profiláctico para gestante positiva a prueba rápida/ELISA VIH"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "071", "descripcion": "Apoyo al diagnóstico"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "901", "descripcion": "Apoyo al Tratamiento"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "908", "descripcion": "Atención domiciliaria"},
    {"categoria": "ACTIVIDAD RECUPERATIVA", "codigo": "300", "descripcion": "Telemedicina"},
    {"categoria": "REHABILITACION", "codigo": "200", "descripcion": "Atención de rehabilitación"},
    {"categoria": "REHABILITACION", "codigo": "900", "descripcion": "Prótesis dental removible"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "111", "descripcion": "Asignación por Alimentación"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "117", "descripcion": "Traslado de Emergencia"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "112", "descripcion": "Sepelio para Óbito fetal (Muerte Intraútero)"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "116", "descripcion": "Sepelio para Recién Nacidos"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "113", "descripcion": "Sepelio para Niñas/os"},
    {"categoria": "PRESTACION ADMINISTRATIVA", "codigo": "114", "descripcion": "Sepelio para Adolescentes y Adultos"},
]

# --- MAPEO DE CÓDIGOS DE ACTIVIDAD A DESCRIPCIONES ---
# --- MAPEO DE CÓDIGOS DE ACTIVIDAD A DESCRIPCIONES ---
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


# --- MAPEO DE CÓDIGO PRESTACIONAL A CÓDIGOS DE ACTIVIDAD ---
RELACION_CODIGO_ACTIVIDADES = {
    '001': {'400', '019R', '020', '021', '307', '407', '102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '124', '211', '126', '405', '003', '004', '014', '015', '414', '415', '416', '120'}, 
    '002': {'400', '019R', '020', '021', '307', '407', '102', '117', '316', '313', '317', '125', '411', '315', '323', '127', '324', '325', '124', '211', '126', '405', '003', '004', '014', '015', '414', '415', '416', '120'}, 
    '118': {'400', '019R', '020', '021', '307', '407', '117', '316', '313', '317', '125', '411', '403', '127', '324', '124', '211', '126', '405', '003', '004', '014', '015', '414', '415', '416', '120'}, 
    '119': {'400', '019R', '020', '021', '307', '407', '117', '316', '313', '317', '125', '411', '403', '127', '324', '323', '124', '211', '126', '405', '003', '004', '014', '015', '414', '415', '416', '120'}, 
    '056': {'019R', '020', '021', '407', '102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '412', '124', '211', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '005E', '010U', '301'}, 
    '906': {'019R', '020', '021', '407', '102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '412', '124', '211', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '010U', '301'}, 
    '050': {'019R', '020', '021', '407', '102', '315', '003', '004', '014', '015', '414', '415', '416', '304', '305', '306'}, 
    '051': {'019R', '020', '021', '407', '102', '315', '003', '004', '014', '015', '414', '415', '416', '304', '305', '306'}, 
    '052': {'019R', '020', '021', '407', '102', '315', '003', '004', '014', '015', '414', '415', '416', '304', '305', '306', '301'}, 
    '064': {'019R', '020', '021', '407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '065': {'019R', '020', '021', '407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '066': {'019R', '020', '021', '407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '067': {'019R', '020', '021', '407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '068': {'019R', '020', '021', '407', '102', '315', '003', '004', '014', '015', '414', '415', '416', '304', '305', '306', '301'}, 
    '005': {'307', '407', '102', '117', '316', '313', '317', '125', '411', '403', '323', '127', '324', '325', '124', '211', '126', '405', '323', '413', '003', '004', '014', '015', '414', '415', '416'}, 
    '009': {'307', '407', '117', '324', '325', '412', '003', '004', '014', '015', '414', '415', '416', '300A', '010U', '301', '417'}, 
    '010': {'307', '407', '324', '325', '405', '323', '003', '004', '014', '015', '414', '415', '416', '010U', '209', '301'}, 
    '007': {'307', '407', '102', '117', '316', '313', '317', '125', '411', '315', '323', '127', '324', '325', '124', '211', '126', '405', '413', '003', '004', '014', '015', '414', '415', '416'}, 
    '017': {'407', '013I', '317', '411', '403', '324', '325', '412', '211', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '018': {'407', '018A', '317', '324', '325', '412', '405', '323', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '019': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '020': {'407', '003', '004', '014', '015', '414', '415', '416'}, 
    '021': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '023': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '024': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '074': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '008': {'407', '102', '117', '316', '313', '317', '125', '411', '403', '323', '324', '325', '124', '211', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '013': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '016': {'407', '102', '117', '316', '313', '317', '125', '411', '315', '323', '127', '324', '325', '124', '211', '126', '405', '413', '003', '004', '014', '015', '414', '415', '416'}, 
    '900': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '901': {'407', '003', '004', '014', '015', '414', '415', '416'}, 
    '902': {'407', '013I', '317', '403', '325', '412', '211', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '903': {'407', '018A', '013I', '317', '403', '325', '211', '126', '405', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '904': {'407', '401', '013I', '317', '403', '325', '412', '126', '405', '323', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '022': {'407', '411', '414', '415', '416'}, 
    '054': {'407', '408', '409', '003', '004', '014', '015', '414', '415', '416', '005E', '010U', '301'}, 
    '055': {'407', '409', '003', '004', '014', '015', '414', '415', '416', '005E', '010U', '301'}, 
    '028': {'102'}, 
    '060': {'102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '412', '124', '211', '126', '405', '323', '414', '415', '416'}, 
    '075': {'102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '412', '124', '211', '126', '405', '323', '414', '415', '416'}, 
    '061': {'102', '117', '316', '313', '317', '125', '411', '315', '403', '323', '127', '324', '325', '412', '124', '211', '126', '405', '323', '414', '415', '416'}, 
    '011': {'003', '004', '015', '414', '415', '416'}, 
    '026': {'003', '004', '014', '015', '414', '415', '416', '301'}, 
    '027': {'003', '004', '414', '415', '416'}, 
    '053': {'003', '004', '414', '415', '416', '301'}, 
    '062': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '063': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '070': {'407', '003', '004', '014', '015', '414', '415', '416', '301'}, 
    '911': {'003', '004', '414', '415', '416', '301'}, 
    '025': {'414', '415', '416'}, 
    '029': {'414', '415', '416'}, 
    '057': {'414', '415', '416'}, 
    '058': {'414', '415', '416'}, 
    '059': {'414', '415', '416'}, 
    '069': {'414', '415', '416'}, 
    '071': {'414', '415', '416'}, 
    '300': {'414', '415', '416'}, 
    '908': {'414', '415', '416'}, 
    '111': {'404'}, 
    '015': {'414', '415', '416'}, 
    'DEFAULT': {'003', '004', '014', '015', '301'}
}

# --- DATOS PARA LA GUÍA DE REFERENCIA DE ANEMIA (RC: 61) ---
DATOS_TABLA_ANEMIA = [
    # N° | EDAD | SEXO | CONDICIÓN | EDAD GEST. | RN PREMATURO | VALOR HB | ACCIÓN 01 | ACCIÓN 02
    ('1.1', '<=7d', 'A', 'NO APLICA', 'NO APLICA', 'SI', '> 13', 'Normal', 'No permite ingreso de "anemia"'),
    ('1.2', '<=7d', 'A', 'NO APLICA', 'NO APLICA', 'SI', '<= 13', 'Anemia', 'Permite ingreso de "anemia"'),
    ('1.3', '8d - 28d', 'A', 'NO APLICA', 'NO APLICA', 'SI', '> 10', 'Normal', 'No permite ingreso de "anemia"'),
    ('1.4', '8d - 28d', 'A', 'NO APLICA', 'NO APLICA', 'SI', '<= 10', 'Anemia', 'Permite ingreso de "anemia"'),
    ('1.5', '29d - <2m', 'A', 'NO APLICA', 'NO APLICA', 'SI', '> 8', 'Normal', 'No permite ingreso de "anemia"'),
    ('1.6', '29d - <2m', 'A', 'NO APLICA', 'NO APLICA', 'SI', '<= 8', 'Anemia', 'Permite ingreso de "anemia"'),
    ('2.1', '<2m', 'A', 'NO APLICA', 'NO APLICA', 'NO', '13.5 - 18.5', 'Normal', 'No permite ingreso de "anemia"'),
    ('2.2', '<2m', 'A', 'NO APLICA', 'NO APLICA', 'NO', '< 13.5', 'Anemia', 'Permite ingreso de "anemia"'),
    ('3.1', '2m - 5m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '9.5 - 13.5', 'Normal', 'No permite ingreso de "anemia"'),
    ('3.2', '2m - 5m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 9.5', 'Anemia', 'Permite ingreso de "anemia"'),
    ('4.1', '6m - 23m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '>= 10.5', 'Normal', 'No permite ingreso de "anemia"'),
    ('4.2', '6m - 23m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '9.5 - 10.4', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('4.3', '6m - 23m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '7.0 - 9.4', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('4.4', '6m - 23m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 7.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('5.1', '24m - 4a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '>= 11.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('5.2', '24m - 4a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '10.0 - 10.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('5.3', '24m - 4a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '7.0 - 9.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('5.4', '24m - 4a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 7.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('6.1', '5a - 11a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '>= 11.5', 'Normal', 'No permite ingreso de "anemia"'),
    ('6.2', '5a - 11a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '11.0 - 11.4', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('6.3', '5a - 11a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '8.0 - 10.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('6.4', '5a - 11a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 8.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('7.1', '12a - 14a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '>= 12.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('7.2', '12a - 14a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '11.0 - 11.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('7.3', '12a - 14a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '8.0 - 10.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('7.4', '12a - 14a11m29d', 'A', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 8.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('8.1', '>=15a', 'M', 'NO APLICA', 'NO APLICA', 'NO APLICA', '>= 13.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('8.2', '>=15a', 'M', 'NO APLICA', 'NO APLICA', 'NO APLICA', '11.0 - 12.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('8.3', '>=15a', 'M', 'NO APLICA', 'NO APLICA', 'NO APLICA', '8.0 - 10.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('8.4', '>=15a', 'M', 'NO APLICA', 'NO APLICA', 'NO APLICA', '< 8.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('9.1', '>=15a', 'F', 'NO GESTANTE/NO PUERPERA', 'NO APLICA', 'NO APLICA', '>= 12.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('9.2', '>=15a', 'F', 'NO GESTANTE/NO PUERPERA', 'NO APLICA', 'NO APLICA', '11.0 - 11.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('9.3', '>=15a', 'F', 'NO GESTANTE/NO PUERPERA', 'NO APLICA', 'NO APLICA', '8.0 - 10.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('9.4', '>=15a', 'F', 'NO GESTANTE/NO PUERPERA', 'NO APLICA', 'NO APLICA', '< 8.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('10.1', '>=9a', 'F', 'GESTANTE', 'EG <14', 'NO APLICA', '>= 11.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('10.2', '>=9a', 'F', 'GESTANTE', 'EG <14', 'NO APLICA', '10.0 - 10.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('10.3', '>=9a', 'F', 'GESTANTE', 'EG <14', 'NO APLICA', '7.0 - 9.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('10.4', '>=9a', 'F', 'GESTANTE', 'EG <14', 'NO APLICA', '< 7.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('10.5', '>=9a', 'F', 'GESTANTE', 'EG 14-28', 'NO APLICA', '>= 10.5', 'Normal', 'No permite ingreso de "anemia"'),
    ('10.6', '>=9a', 'F', 'GESTANTE', 'EG 14-28', 'NO APLICA', '9.5 - 10.4', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('10.7', '>=9a', 'F', 'GESTANTE', 'EG 14-28', 'NO APLICA', '7.0 - 9.4', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('10.8', '>=9a', 'F', 'GESTANTE', 'EG 14-28', 'NO APLICA', '< 7.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
    ('11.1', '>=9a', 'F', 'PUERPERA', 'NO APLICA', 'NO APLICA', '>= 12.0', 'Normal', 'No permite ingreso de "anemia"'),
    ('11.2', '>=9a', 'F', 'PUERPERA', 'NO APLICA', 'NO APLICA', '11.0 - 11.9', 'Anemia Leve', 'Permite ingreso de "anemia"'),
    ('11.3', '>=9a', 'F', 'PUERPERA', 'NO APLICA', 'NO APLICA', '8.0 - 10.9', 'Anemia Moderada', 'Permite ingreso de "anemia"'),
    ('11.4', '>=9a', 'F', 'PUERPERA', 'NO APLICA', 'NO APLICA', '< 8.0', 'Anemia Severa', 'Permite ingreso de "anemia"'),
]

# --- DATOS PARA LA GUÍA DE REFERENCIA DE CRECIMIENTO (PESO Y TALLA) ---
DATOS_PESO_TALLA = [
    # Categoría, Rango de Edad, Sexo, Rango de Peso (kg), Rango de Talla (cm), Notas
    ("Recién Nacido", "0 - 1 mes", "Ambos", "2.5 - 4.5 kg", "46 - 55 cm", "Peso y talla al nacer"),
    ("Bebés", "1 - 6 meses", "Ambos", "4.0 - 8.0 kg", "54 - 68 cm", "Rápido crecimiento"),
    ("Bebés", "6 - 12 meses", "Ambos", "7.0 - 10.5 kg", "65 - 78 cm", ""),
    ("Niños Pequeños", "1 - 2 años", "Ambos", "9.0 - 13.5 kg", "74 - 90 cm", ""),
    ("Niños Pequeños", "2 - 3 años", "Ambos", "11.0 - 16.0 kg", "85 - 100 cm", ""),
    ("Preescolar", "3 - 5 años", "Ambos", "13.0 - 20.0 kg", "95 - 110 cm", ""),
    ("Escolar", "6 - 8 años", "Ambos", "18.0 - 28.0 kg", "110 - 130 cm", ""),
    ("Escolar", "9 - 11 años", "Ambos", "26.0 - 40.0 kg", "125 - 145 cm", ""),
    ("Adolescentes", "12 - 14 años", "Masculino", "35.0 - 55.0 kg", "145 - 165 cm", "Varía mucho con la pubertad"),
    ("Adolescentes", "12 - 14 años", "Femenino", "35.0 - 52.0 kg", "147 - 163 cm", "Varía mucho con la pubertad"),
    ("Adolescentes", "15 - 17 años", "Masculino", "50.0 - 70.0 kg", "165 - 178 cm", ""),
    ("Adolescentes", "15 - 17 años", "Femenino", "48.0 - 65.0 kg", "155 - 170 cm", ""),
    ("Adultos", "18+ años", "Ambos", "Ver nota", "Ver nota", "El peso ideal depende de la talla (IMC 18.5-24.9)"),
]


# --- INICIO DE LA APLICACIÓN FLASK ---
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "llave-secreta-de-desarrollo")

# --- RUTAS DEL NÚCLEO (LOGIN, MENU, ETC.) ---
@app.route('/')
def home():
    return redirect(url_for('login'))

# --- RUTA DE LOGIN (MODIFICADA PARA USAR LA BASE DE DATOS) ---
# --- RUTA DE LOGIN (CON bcrypt) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            with engine.connect() as connection:
                sql_query = text("SELECT username, password_hash, role FROM usuarios WHERE LOWER(username) = LOWER(:username)")
                result = connection.execute(sql_query, {'username': username}).first()
                if result:
                    stored_hash_hex = result.password_hash
                    stored_hash_bytes = bytes.fromhex(stored_hash_hex)
                    password_bytes = password.encode('utf-8')
                    # VERIFICACIÓN CON BCRYPT
                    # ... (dentro de la función login)
                    if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                        # 3. Si la contraseña es correcta, iniciar sesión
                        session['username'] = result.username
                        session['role'] = result.role
    
                        # ==================================
                        # INICIO DE LA INSTRUMENTACIÓN (NUEVO)
                        # ==================================
                        try:
                            log_sql = text("INSERT INTO logs (username, action) VALUES (:username, 'login')")
                            connection.execute(log_sql, {'username': result.username})
                            connection.commit() # Asegurarse de que el log se guarde
                        except Exception as log_error:
                            # Si el log falla, no queremos que el login se interrumpa.
                            # Simplemente lo imprimimos en la consola del servidor para depuración.
                            print(f"Error al registrar el log de login: {log_error}")
                        # ==================================
                        # FIN DE LA INSTRUMENTACIÓN
                        # ==================================
                        return redirect(url_for('menu'))
                    # ...
                    else:
                        flash('Nombre de usuario o contraseña incorrectos.', 'danger')
                else:
                    flash('Nombre de usuario o contraseña incorrectos.', 'danger')
        except Exception as e:
            print(f"Error durante el login: {e}")
            flash('Ocurrió un error en el servidor.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('menu.html')

# --- RUTAS DE FORMULARIO Y APIs ---
@app.route('/plantillas')
def plantillas():
    if 'username' not in session: return redirect(url_for('login'))
    modo = request.args.get('modo', 'crear')
    plantilla_id = request.args.get('id', None)
    return render_template('plantillas.html', modo=modo, plantilla_id=plantilla_id)

@app.route('/search_codigos', methods=['GET'])
def search_codigos():
    if 'username' not in session: return jsonify({'suggestions': []}), 401
    query = request.args.get('query', '').strip()
    suggestions = [s for s in CODIGOS_PRESTACIONALES_CATEGORIZADOS if s['codigo'] == query]
    return jsonify({'suggestions': suggestions})

@app.route('/get_actividades_por_codigo/<codigo>', methods=['GET'])
def get_actividades_por_codigo(codigo):
    if 'username' not in session: return jsonify({'actividades': []}), 401
    codigos_actividad = RELACION_CODIGO_ACTIVIDADES.get(codigo, RELACION_CODIGO_ACTIVIDADES.get('DEFAULT', []))
    actividades_sugeridas = [{'codigo': c, 'descripcion': ACTIVIDADES_PREVENTIVAS_MAP.get(c, f'Desc no encontrada')} for c in sorted(list(codigos_actividad))]
    return jsonify({'actividades': actividades_sugeridas})

# --- RUTAS CRUD CONECTADAS A SUPABASE ---

@app.route('/get_registros', methods=['GET'])
def get_registros():
    if 'username' not in session: return jsonify({"error": "No autorizado"}), 401
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, tipo_atencion, codigo_prestacional FROM plantillas ORDER BY id ASC"))
        registros = [dict(row._mapping) for row in result]
        return jsonify(registros)

@app.route('/get_plantilla/<int:plantilla_id>', methods=['GET'])
def get_plantilla(plantilla_id):
    if 'username' not in session: return jsonify({"error": "No autorizado"}), 401
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        plantilla = result.first()
        if plantilla:
            return jsonify(dict(plantilla._mapping))
        else:
            return jsonify({"error": "Plantilla no encontrada"}), 404

@app.route('/delete_plantilla/<int:plantilla_id>', methods=['DELETE'])
def delete_plantilla(plantilla_id):
    if session.get('role') != 'administrador': return jsonify({'message': 'No autorizado.'}), 403
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        connection.commit()
        return jsonify({'message': f'Plantilla ID {plantilla_id} eliminada con éxito.'}), 200

@app.route('/guardar_plantilla', methods=['POST'])
def guardar_plantilla():
    if session.get('role') != 'administrador': return jsonify({'message': 'No autorizado.'}), 403
    
    data = request.json
    plantilla_id = data.get('plantilla_id')

    params = {
        "tipo_atencion": data.get("tipo_atencion"),
        "codigo_prestacional": data.get("codigo_prestacional"),
        "descripcion_prestacional": data.get("descripcion_prestacional"),
        "actividades_preventivas": data.get('actividades_preventivas', []),
        "diagnostico_principal": data.get("diagnostico_principal", []),
        "diagnosticos_excluyentes": data.get("diagnosticos_excluyentes", []),
        "diagnosticos_complementarios": data.get("diagnosticos_complementarios", []),
        "medicamentos_relacionados": data.get("medicamentos_relacionados", []),
        "insumos_relacionados": data.get("insumos_relacionados", []),
        "procedimientos_obligatorios": data.get("procedimientos_obligatorios", []),
        "procedimientos_excluyentes": data.get("procedimientos_excluyentes", []),
        "otros_procedimientos": data.get("otros_procedimientos", []),
        "observaciones": data.get("observaciones"),
    }

    with engine.connect() as connection:
        if plantilla_id:
            params['id'] = plantilla_id
            query = text("""
                UPDATE plantillas SET
                    tipo_atencion = :tipo_atencion, codigo_prestacional = :codigo_prestacional,
                    descripcion_prestacional = :descripcion_prestacional, actividades_preventivas = :actividades_preventivas,
                    diagnostico_principal = :diagnostico_principal, diagnosticos_excluyentes = :diagnosticos_excluyentes,
                    diagnosticos_complementarios = :diagnosticos_complementarios, medicamentos_relacionados = :medicamentos_relacionados,
                    insumos_relacionados = :insumos_relacionados, procedimientos_obligatorios = :procedimientos_obligatorios,
                    procedimientos_excluyentes = :procedimientos_excluyentes, otros_procedimientos = :otros_procedimientos,
                    observaciones = :observaciones
                WHERE id = :id
            """)
            connection.execute(query, params)
            connection.commit()
            return jsonify({'message': f'Plantilla ID {plantilla_id} actualizada con éxito.'}), 200
        else:
            query = text("""
                INSERT INTO plantillas (tipo_atencion, codigo_prestacional, descripcion_prestacional, actividades_preventivas, 
                                      diagnostico_principal, diagnosticos_excluyentes, diagnosticos_complementarios, 
                                      medicamentos_relacionados, insumos_relacionados, procedimientos_obligatorios, 
                                      procedimientos_excluyentes, otros_procedimientos, observaciones)
                VALUES (:tipo_atencion, :codigo_prestacional, :descripcion_prestacional, :actividades_preventivas, 
                        :diagnostico_principal, :diagnosticos_excluyentes, :diagnosticos_complementarios, 
                        :medicamentos_relacionados, :insumos_relacionados, :procedimientos_obligatorios, 
                        :procedimientos_excluyentes, :otros_procedimientos, :observaciones)
                RETURNING id
            """)
            result = connection.execute(query, params)
            new_id = result.scalar()
            connection.commit()
            return jsonify({'message': f'¡Éxito! Plantilla "{params["tipo_atencion"]}" guardada con ID: {new_id}'}), 201

@app.route('/ver_plantillas')
def ver_plantillas():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('ver_plantillas.html')

@app.route('/plantilla/<int:plantilla_id>')
def detalle_plantilla(plantilla_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    plantilla_data = None
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        plantilla_row = result.first()
        if plantilla_row:
            # Convertimos la fila de la BD a un diccionario para pasarlo a la plantilla
            plantilla_data = dict(plantilla_row._mapping)

    if plantilla_data:
        # Si encontramos la plantilla, la mostramos en una nueva página de detalles
        return render_template('detalle_plantilla.html', plantilla=plantilla_data)
    else:
        # Si no se encuentra una plantilla con ese ID, mostramos un error 404
        return "Plantilla no encontrada", 404

# --- RUTA DE DESCARGA PDF - VERSIÓN LIGERA FINAL ---
@app.route('/plantilla/<int:plantilla_id>/descargar_pdf')
def descargar_pdf_plantilla(plantilla_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # 1. Obtenemos los datos de la plantilla
    plantilla_data = None
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM plantillas WHERE id = :id"), {"id": plantilla_id})
        plantilla_row = result.first()
        if plantilla_row:
            plantilla_data = dict(plantilla_row._mapping)

    if not plantilla_data:
        return "Plantilla no encontrada", 404

    # 2. Creamos una clase PDF personalizada con fpdf2
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Detalle de Plantilla', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(230, 230, 230)
            self.cell(0, 8, title, 0, 1, 'L', True)
            self.ln(4)

        def chapter_body(self, content):
            self.set_font('Arial', '', 10)
            if isinstance(content, list):
                for item in content:
                    self.multi_cell(0, 5, f'- {item}')
                self.ln()
            else:
                self.multi_cell(0, 5, str(content)) # Usamos str() para seguridad
                self.ln()

    # 3. "Dibujamos" el PDF
    pdf = PDF()
    pdf.add_page()
    
    pdf.chapter_title('Información General')
    pdf.chapter_body(f"ID de Plantilla: {plantilla_data['id']}")
    pdf.chapter_body(f"Tipo de Atención: {plantilla_data['tipo_atencion']}")
    pdf.chapter_body(f"Código Prestacional: {plantilla_data['codigo_prestacional']}")
    pdf.chapter_body(f"Descripción: {plantilla_data['descripcion_prestacional']}")

    def display_section(title, data):
        if data and len(data) > 0:
            pdf.chapter_title(title)
            pdf.chapter_body(data)

    display_section('Actividades Preventivas', plantilla_data.get('actividades_preventivas'))
    display_section('Diagnóstico Principal', plantilla_data.get('diagnostico_principal'))
    # ... (el resto de las llamadas a display_section están bien) ...
    display_section('Otros Procedimientos', plantilla_data.get('otros_procedimientos'))
    
    # ==============================================================================
    # CORRECCIÓN 3 y 4: Lógica de limpieza DENTRO del 'if' y con el replace correcto
    # ==============================================================================
    if plantilla_data.get('observaciones'):
        pdf.chapter_title('Observaciones')
        
        texto_observaciones = plantilla_data.get('observaciones', '')
        if texto_observaciones:
            texto_observaciones = texto_observaciones.replace('<p>', '').replace('</p>', '\n')
            texto_observaciones = texto_observaciones.replace('<strong>', '').replace('</strong>', '')
            texto_observaciones = texto_observaciones.replace('<em>', '').replace('</em>', '')
            texto_observaciones = texto_observaciones.replace('<u>', '').replace('</u>', '')
            texto_observaciones = texto_observaciones.replace('<li>', '  - ').replace('</li>', '\n')
            texto_observaciones = texto_observaciones.replace('<ol>', '').replace('</ol>', '')
            texto_observaciones = texto_observaciones.replace('<ul>', '').replace('</ul>', '')
            texto_observaciones = texto_observaciones.replace('  ', '\n') # CORRECCIÓN 4
            texto_observaciones = re.sub('<[^<]+?>', '', texto_observaciones).strip()
        
        pdf.multi_cell(0, 5, texto_observaciones)

    # 4. Generamos el PDF y lo enviamos como respuesta
    pdf_output = pdf.output(dest='S')
    
    return Response(
        pdf_output,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="plantilla_{plantilla_id}.pdf"'}
    )

# --- RUTA PARA LA CALCULADORA DE IMC ---
@app.route('/calculadora_imc')
def calculadora_imc():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('calculadora_imc.html')

# --- RUTA PARA LA CALCULADORA GESTACIONAL ---

@app.route('/calculadora_gestacional')
def calculadora_gestacional():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('calculadora_gestacional.html')

# --- RUTA PARA LA PÁGINA DE REFERENCIA DE CÓDIGOS Y FECHAS ---
@app.route('/referencia_codigos')
def referencia_codigos():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Lógica para calcular las fechas
    hoy = datetime.now()
    fecha_optima = hoy - timedelta(days=7)
    fecha_regular = hoy - timedelta(days=30)
    fecha_no_optima = hoy - timedelta(days=45)

    # Formateamos las fechas para mostrarlas
    fechas = {
        "actual": hoy.strftime('%d/%m/%Y'),
        "optima": fecha_optima.strftime('%d/%m/%Y'),
        "regular": fecha_regular.strftime('%d/%m/%Y'),
        "no_optima": fecha_no_optima.strftime('%d/%m/%Y')
    }

    # Pasamos las fechas y la lista de códigos a la plantilla
    return render_template('referencia_codigos.html', fechas=fechas, codigos=CODIGOS_PRESTACIONALES_CATEGORIZADOS)

# --- RUTA PARA LA GUÍA DE REFERENCIA DE ANEMIA (RC: 61) ---
@app.route('/guia_anemia')
def guia_anemia():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Pasamos los datos de la tabla a la plantilla
    return render_template('guia_anemia.html', datos_anemia=DATOS_TABLA_ANEMIA)

# --- RUTA PARA LA GUÍA DE REFERENCIA DE CRECIMIENTO (PESO Y TALLA) ---
@app.route('/guia_peso_talla')
def guia_peso_talla():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Pasamos los datos de la tabla a la plantilla
    return render_template('guia_peso_talla.html', datos_tabla=DATOS_PESO_TALLA)

# --- RUTA PARA MOSTRAR LA PÁGINA DE BÚSQUEDA DE DIAGNÓSTICOS ---
# --- RUTA PARA MOSTRAR LA PÁGINA DE BÚSQUEDA HÍBRIDA DE DIAGNÓSTICOS ---
@app.route('/buscar_diagnosticos')
def buscar_diagnosticos():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('buscar_diagnosticos.html')

# --- API INTERNA PARA BÚSQUEDA ASÍNCRONA (RÁPIDA) ---
@app.route('/api/search_diagnosticos')
def search_diagnosticos():
    if 'username' not in session: return jsonify({'error': 'No autorizado'}), 401
    query = request.args.get('q', '')
    if len(query) < 3: return jsonify([])
    try:
        with engine.connect() as connection:
            sql_query = text("SELECT codigo, descripcion FROM diagnosticos WHERE codigo ILIKE :query OR descripcion ILIKE :query LIMIT 50;")
            result = connection.execute(sql_query, {'query': f'%{query}%'})
            return jsonify([dict(row._mapping) for row in result])
    except Exception as e:
        print(f"Error en búsqueda asíncrona: {e}")
        return jsonify({'error': 'Error en el servidor'}), 500

# --- API INTERNA PARA CARGAR TODOS LOS DIAGNÓSTICOS (COMPLETA) ---
@app.route('/api/get_all_diagnosticos')
def get_all_diagnosticos():
    if 'username' not in session: return jsonify({'error': 'No autorizado'}), 401
    try:
        with engine.connect() as connection:
            sql_query = text("SELECT codigo, descripcion FROM diagnosticos ORDER BY codigo;")
            result = connection.execute(sql_query)
            return jsonify([dict(row._mapping) for row in result])
    except Exception as e:
        print(f"Error al cargar todos los diagnósticos: {e}")
        return jsonify({'error': 'Error en el servidor'}), 500

# --- RUTA PARA LA GESTIÓN DE USUARIOS (SOLO ADMIN) ---
# --- RUTA PARA LA GESTIÓN DE USUARIOS (SOLO ADMIN) ---
@app.route('/admin/usuarios')
def gestionar_usuarios():
    if 'username' not in session or session.get('role') != 'administrador':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('menu'))

    try:
        with engine.connect() as connection:
            sql_query = text("SELECT id, username, role FROM usuarios ORDER BY username ASC")
            result = connection.execute(sql_query)
            lista_usuarios = [dict(row._mapping) for row in result]
    except Exception as e:
        print(f"Error al obtener la lista de usuarios: {e}")
        flash('Error al cargar la lista de usuarios.', 'danger')
        lista_usuarios = []

    return render_template('gestionar_usuarios.html', usuarios=lista_usuarios)

# --- API PARA AÑADIR UN NUEVO USUARIO ---
@app.route('/api/add_user', methods=['POST'])
def add_user():
    if 'username' not in session or session.get('role') != 'administrador':
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    data = request.json
    new_username = data.get('username')
    new_password = data.get('password')
    new_role = data.get('role')

    if not all([new_username, new_password, new_role]):
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos.'}), 400

    try:
        # Hashear la contraseña
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
        hashed_password_hex = hashed_password_bytes.hex()

        with engine.connect() as connection:
            # Verificar si el usuario ya existe
            check_sql = text("SELECT id FROM usuarios WHERE LOWER(username) = LOWER(:username)")
            existing_user = connection.execute(check_sql, {'username': new_username}).first()
            if existing_user:
                return jsonify({'success': False, 'message': f'El usuario "{new_username}" ya existe.'}), 409

            # Insertar nuevo usuario
            insert_sql = text("INSERT INTO usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)")
            connection.execute(insert_sql, {
                'username': new_username,
                'password_hash': hashed_password_hex,
                'role': new_role
            })
            connection.commit()
        
        return jsonify({'success': True, 'message': f'Usuario "{new_username}" creado con éxito.'}), 201

    except Exception as e:
        print(f"Error al añadir usuario: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor.'}), 500


# --- API PARA ELIMINAR UN USUARIO ---
@app.route('/api/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user():
    if 'username' not in session or session.get('role') != 'administrador':
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    # Evitar que el admin se elimine a sí mismo
    with engine.connect() as connection:
        user_to_delete = connection.execute(text("SELECT username FROM usuarios WHERE id = :id"), {'id': user_id}).scalar()
        if user_to_delete == session.get('username'):
            return jsonify({'success': False, 'message': 'No puedes eliminar tu propia cuenta de administrador.'}), 400

    try:
        with engine.connect() as connection:
            sql_query = text("DELETE FROM usuarios WHERE id = :id")
            connection.execute(sql_query, {'id': user_id})
            connection.commit()
        return jsonify({'success': True, 'message': 'Usuario eliminado con éxito.'}), 200
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor.'}), 500

# ==============================================================================
#                           RUTAS PARA EL DASHBOARD
# ==============================================================================

@app.route('/dashboard')
def dashboard():
    """Muestra la página principal del dashboard de métricas."""
    if session.get('role') != 'administrador':
        flash('Acceso denegado. Esta sección es solo para administradores.', 'danger')
        return redirect(url_for('menu'))
    
    return render_template('dashboard.html')


@app.route('/api/dashboard_data')
def dashboard_data():
    """Proporciona los datos agregados para el dashboard."""
    if session.get('role') != 'administrador':
        return jsonify({"error": "No autorizado"}), 403

    try:
        with engine.connect() as connection:
            # 1. Contar el total de logins
            logins_query = text("SELECT COUNT(*) FROM logs WHERE action = 'login'")
            total_logins = connection.execute(logins_query).scalar_one_or_none() or 0

            # Preparamos el diccionario de datos para enviar
            data = {
                "total_logins": total_logins
                # En el futuro añadiremos más datos aquí
            }
            
            return jsonify(data)

    except Exception as e:
        print(f"Error al generar datos del dashboard: {e}")
        return jsonify({"error": "Error interno al procesar los datos"}), 500


if __name__ == '__main__':
    app.run(debug=True)