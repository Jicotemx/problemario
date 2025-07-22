import os
import json
import base64
import requests
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from utils import MathProblemManager
from jinja2 import Environment, FileSystemLoader
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io

import sys
import subprocess
import setuptools

import logging
logging.basicConfig(level=logging.INFO)

@app.before_first_request
def startup():
    app.logger.info("Aplicación iniciada correctamente")
    app.logger.info(f"Versión de Flask: {flask.__version__}")

@app.route('/healthz')
def health_check():
    return "OK", 200




@app.route('/check')
def check():
    return f"""
    Setuptools version: {setuptools.__version__}<br>
    Python version: {sys.version}
    """



# Verificar e instalar dependencias faltantes
try:
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib==3.7.1"])

try:
    import jinja2
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2==3.1.2"])


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuración de GitHub
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')  # Formato: usuario/repo
GITHUB_BRANCH = os.environ.get('GITHUB_BRANCH', 'main')

# Archivos en GitHub
PROBLEMAS_JSON = "problemas.json"
TEMPLATE_LATEX = "template.tex"
OUTPUT_PDF = "problemas_seleccionados.pdf"

manager = MathProblemManager()

def cargar_datos_desde_github():
    """Carga problemas.json desde GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PROBLEMAS_JSON}?ref={GITHUB_BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()['content']
        decoded = base64.b64decode(content).decode('utf-8')
        return json.loads(decoded)
    except:
        return {}

def guardar_datos_en_github(data):
    """Guarda problemas.json en GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PROBLEMAS_JSON}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Obtener SHA del archivo actual
    current = requests.get(url, headers=headers).json()
    sha = current.get('sha', '')
    
    encoded = base64.b64encode(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    
    payload = {
        "message": "Actualización desde Gestor de Problemas",
        "content": encoded,
        "branch": GITHUB_BRANCH,
        "sha": sha if sha else None
    }
    
    response = requests.put(url, headers=headers, json=payload)
    return response.status_code == 200 or response.status_code == 201

def descargar_archivo_github(archivo):
    """Descarga un archivo desde GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{archivo}?ref={GITHUB_BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()['content']
        return base64.b64decode(content).decode('utf-8')
    except:
        return ""

# Inicializar manager con datos de GitHub
manager.problemas = cargar_datos_desde_github()
manager.organizar_categorias()

# Crear template si no existe
if not manager.crear_template_si_no_existe():
    template_content = descargar_archivo_github(TEMPLATE_LATEX)
    if template_content:
        with open(TEMPLATE_LATEX, 'w', encoding='utf-8') as f:
            f.write(template_content)

@app.route('/')
def index():
    """Página principal"""
    stats = {
        'total_problemas': len(manager.problemas),
        'seleccionados': len(manager.problemas_seleccionados),
        'categorias': len(manager.categorias),
        'subcategorias': sum(len(sub) for sub in manager.categorias.values()),
        'temas': sum(len(temas) for cat in manager.categorias.values() for sub in cat.values() for temas in sub.values())
    }
    return render_template('index.html', stats=stats)

@app.route('/agregar_problema', methods=['GET', 'POST'])
def agregar_problema():
    """Agregar nuevo problema"""
    if request.method == 'POST':
        categoria = request.form['categoria']
        subcategoria = request.form['subcategoria']
        tema = request.form['tema']
        enunciado = request.form['enunciado']
        solucion = request.form['solucion']
        respuesta = request.form['respuesta']
        
        nuevo_id = manager.agregar_problema(categoria, subcategoria, tema, enunciado, solucion, respuesta)
        if nuevo_id:
            # Guardar en GitHub
            guardar_datos_en_github(manager.problemas)
            return redirect(url_for('index'))
    
    # Obtener categorías para el formulario
    categorias = sorted(manager.categorias.keys())
    return render_template('agregar.html', categorias=categorias)

@app.route('/seleccionar_problemas')
def seleccionar_problemas():
    """Seleccionar problemas para PDF"""
    categoria = request.args.get('categoria', '')
    subcategoria = request.args.get('subcategoria', '')
    tema = request.args.get('tema', '')
    busqueda = request.args.get('busqueda', '')
    
    # Filtrar problemas
    if busqueda:
        problemas_filtrados = []
        for id_problema, problema in manager.problemas.items():
            if (busqueda.lower() in id_problema.lower() or
                busqueda.lower() in problema['enunciado'].lower() or
                busqueda.lower() in problema['solucion'].lower() or
                busqueda.lower() in problema['respuesta'].lower()):
                problemas_filtrados.append((id_problema, problema))
    elif categoria and subcategoria and tema:
        problemas_ids = manager.categorias.get(categoria, {}).get(subcategoria, {}).get(tema, [])
        problemas_filtrados = [(id_p, manager.problemas[id_p]) for id_p in problemas_ids]
    else:
        problemas_filtrados = list(manager.problemas.items())
    
    # Organizar datos para vista
    problemas_data = []
    for id_problema, problema in problemas_filtrados:
        seleccionado = any(p['id'] == id_problema for p in manager.problemas_seleccionados)
        problemas_data.append({
            'id': id_problema,
            'enunciado': problema['enunciado'][:100] + '...' if len(problema['enunciado']) > 100 else problema['enunciado'],
            'seleccionado': seleccionado,
            'categoria': problema['categoria'],
            'subcategoria': problema['subcategoria'],
            'tema': problema['tema']
        })
    
    return render_template('seleccionar.html', 
                          problemas=problemas_data,
                          categorias=sorted(manager.categorias.keys()),
                          categoria_actual=categoria,
                          subcategoria_actual=subcategoria,
                          tema_actual=tema,
                          busqueda=busqueda)

@app.route('/toggle_seleccion/<id_problema>')
def toggle_seleccion(id_problema):
    """Alternar selección de problema"""
    manager.seleccionar_problema(id_problema)
    return redirect(url_for('seleccionar_problemas',
                           categoria=request.args.get('categoria', ''),
                           subcategoria=request.args.get('subcategoria', ''),
                           tema=request.args.get('tema', ''),
                           busqueda=request.args.get('busqueda', '')))

@app.route('/generar_pdf', methods=['POST'])
def generar_pdf():
    """Generar PDF con problemas seleccionados"""
    titulo = request.form.get('titulo', 'Problemas Seleccionados')
    include_soluciones = 'include_soluciones' in request.form
    include_respuestas = 'include_respuestas' in request.form
    
    if manager.generar_pdf(titulo, include_soluciones, include_respuestas):
        return send_file(OUTPUT_PDF, as_attachment=True)
    return "Error al generar PDF", 500

@app.route('/exportar_base')
def exportar_base():
    """Exportar base de datos"""
    return send_file(
        io.BytesIO(json.dumps(manager.problemas, indent=4, ensure_ascii=False).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name='problemas_exportados.json'
    )

@app.route('/importar_base', methods=['POST'])
def importar_base():
    """Importar base de datos"""
    if 'file' not in request.files:
        return "No se seleccionó archivo", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nombre de archivo inválido", 400
    
    try:
        nuevos_problemas = json.load(file)
        for id_problema, datos in nuevos_problemas.items():
            if id_problema not in manager.problemas:
                manager.problemas[id_problema] = datos
        
        manager.organizar_categorias()
        guardar_datos_en_github(manager.problemas)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Error al importar: {str(e)}", 500

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        print(f"Error starting app: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
