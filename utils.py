import os
import json
import subprocess
from jinja2 import Environment, FileSystemLoader

# Configuración global
PROBLEMAS_JSON = "problemas.json"
TEMPLATE_LATEX = "template.tex"
OUTPUT_PDF = "problemas_seleccionados.pdf"

class MathProblemManager:
    def __init__(self):
        self.problemas_seleccionados = []
        self.categorias = {}
        self.problemas = {}
        self.cargar_problemas()
        self.crear_template_si_no_existe()
        
    def cargar_problemas(self):
        """Carga los problemas desde el archivo JSON"""
        if not os.path.exists(PROBLEMAS_JSON):
            self.problemas = {}
            return
        
        try:
            with open(PROBLEMAS_JSON, 'r', encoding='utf-8') as f:
                self.problemas = json.load(f)
        except json.JSONDecodeError:
            self.problemas = {}
        except Exception as e:
            self.problemas = {}
            
        # Organizar problemas por categorías
        self.organizar_categorias()
    
    def organizar_categorias(self):
        """Organiza los problemas en una estructura de categorías"""
        self.categorias = {}
        
        for id_problema, datos in self.problemas.items():
            cat = datos.get('categoria', 'Sin Categoría')
            subcat = datos.get('subcategoria', 'Sin Subcategoría')
            tema = datos.get('tema', 'Sin Tema')
            
            if cat not in self.categorias:
                self.categorias[cat] = {}
            if subcat not in self.categorias[cat]:
                self.categorias[cat][subcat] = {}
            if tema not in self.categorias[cat][subcat]:
                self.categorias[cat][subcat][tema] = []
            
            self.categorias[cat][subcat][tema].append(id_problema)
    
    def guardar_problemas(self):
        """Guarda los problemas en el archivo JSON"""
        with open(PROBLEMAS_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.problemas, f, ensure_ascii=False, indent=4)
    
    def crear_template_si_no_existe(self):
        """Crea la plantilla LaTeX si no existe"""
        if not os.path.exists(TEMPLATE_LATEX):
            with open(TEMPLATE_LATEX, 'w', encoding='utf-8') as f:
                f.write(r"""\documentclass{article}
\usepackage[spanish]{babel}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{enumitem}

\geometry{a4paper, margin=2cm}

\title{\VAR{titulo}}
\date{\today}

\begin{document}
\maketitle

\section*{Problemas}
\begin{enumerate}[leftmargin=*]
\BLOCK{for problema in problemas}
  \item \textbf{ID: \VAR{problema['id']}} \\
  \VAR{problema['enunciado']}
  
  \vspace{1em}
\BLOCK{endfor}
\end{enumerate}

\BLOCK{if include_soluciones or include_respuestas}
\newpage
\section*{Soluciones y Respuestas}
\begin{enumerate}[leftmargin=*]
\BLOCK{for problema in problemas}
  \item \textbf{ID: \VAR{problema['id']}} \\
  \BLOCK{if include_soluciones and problema['solucion']}
  \textbf{Solución (procedimiento):} \\
  \VAR{problema['solucion']} \\
  \BLOCK{endif}
  
  \BLOCK{if include_respuestas and problema['respuesta']}
  \textbf{Respuesta final:} \\
  \VAR{problema['respuesta']}
  \BLOCK{endif}
  
  \vspace{1em}
\BLOCK{endfor}
\end{enumerate}
\BLOCK{endif}
\end{document}
""")
            return True
        return False
    
    def agregar_problema(self, categoria, subcategoria, tema, enunciado, solucion, respuesta):
        """Agrega un nuevo problema a la base de datos"""
        # Generar ID único
        base_id = f"{categoria}:{subcategoria}:{tema}"
        contador = 1
        nuevo_id = f"{base_id}:{contador:03d}"
        
        # Encontrar el próximo ID disponible
        while nuevo_id in self.problemas:
            contador += 1
            nuevo_id = f"{base_id}:{contador:03d}"
        
        # Agregar a la base de datos
        self.problemas[nuevo_id] = {
            "enunciado": enunciado.strip(),
            "solucion": solucion.strip(),
            "respuesta": respuesta.strip(),
            "categoria": categoria,
            "subcategoria": subcategoria,
            "tema": tema
        }
        
        self.guardar_problemas()
        self.organizar_categorias()
        return nuevo_id
    
    def editar_problema(self, id_problema, categoria, subcategoria, tema, enunciado, solucion, respuesta):
        """Edita un problema existente"""
        if id_problema not in self.problemas:
            return False
        
        # Actualizar datos
        self.problemas[id_problema] = {
            "enunciado": enunciado.strip(),
            "solucion": solucion.strip(),
            "respuesta": respuesta.strip(),
            "categoria": categoria,
            "subcategoria": subcategoria,
            "tema": tema
        }
        
        self.guardar_problemas()
        self.organizar_categorias()
        return True
    
    def eliminar_problema(self, id_problema):
        """Elimina un problema de la base de datos"""
        if id_problema in self.problemas:
            del self.problemas[id_problema]
            self.guardar_problemas()
            self.organizar_categorias()
            
            # Eliminar de seleccionados si está ahí
            self.problemas_seleccionados = [p for p in self.problemas_seleccionados if p['id'] != id_problema]
            return True
        return False
    
    def seleccionar_problema(self, id_problema):       
        """Selecciona o deselecciona un problema"""
        # Buscar si ya está seleccionado
        for i, problema in enumerate(self.problemas_seleccionados):
            if problema['id'] == id_problema:
                # Si ya está en la lista de seleccionados, lo removemos (deseleccionamos)
                self.problemas_seleccionados.pop(i)
                return False  # Se ha deseleccionado
    
        # Si no está, lo agregamos (seleccionamos)
        if id_problema in self.problemas:
            problema_data = self.problemas[id_problema]
            # Asegurarse de incluir todos los campos
            problema_completo = {
                "id": id_problema,
                "enunciado": problema_data['enunciado'],
                "solucion": problema_data['solucion'],
                "respuesta": problema_data['respuesta'],
                "categoria": problema_data['categoria'],
                "subcategoria": problema_data['subcategoria'],
                "tema": problema_data['tema']
            }
            self.problemas_seleccionados.append(problema_completo)
            return True  # Se ha seleccionado
        else:
            return False  # No se pudo seleccionar

    def generar_pdf(self, titulo="Problemas Seleccionados", include_soluciones=True, include_respuestas=True):
        """Genera un PDF con los problemas seleccionados"""
        if not self.problemas_seleccionados:
            return False
        
        try:
            # Configurar entorno Jinja2
            env = Environment(loader=FileSystemLoader('.'), 
                             block_start_string='\\BLOCK{', 
                             block_end_string='}', 
                             variable_start_string='\\VAR{', 
                             variable_end_string='}', 
                             comment_start_string='\\#{', 
                             comment_end_string='}', 
                             trim_blocks=True,
                             autoescape=False)
            
            # Cargar plantilla LaTeX
            template = env.get_template(TEMPLATE_LATEX)
            
            # Renderizar LaTeX con título personalizado
            latex_output = template.render(
                problemas=self.problemas_seleccionados,
                titulo=titulo,
                include_soluciones=include_soluciones,
                include_respuestas=include_respuestas
            )
            
            # Guardar archivo LaTeX
            with open('output.tex', 'w', encoding='utf-8') as f:
                f.write(latex_output)
            
            # Compilar a PDF
            process = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'output.tex'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                # Registrar error en logs
                print(f"Error en pdflatex: {process.stderr}")
                return False

            # Renombrar el PDF resultante
            if os.path.exists('output.pdf'):
                os.rename('output.pdf', OUTPUT_PDF)
            
            # Limpiar archivos temporales
            for ext in ['.aux', '.log', '.out']:
                temp_file = f'output{ext}'
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return True
        except Exception as e:
            print(f"Error al generar PDF: {str(e)}")
            return False
    
    def exportar_base_datos(self, archivo):
        """Exporta la base de datos a un archivo JSON"""
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(self.problemas, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error exportando base: {str(e)}")
            return False
    
    def importar_base_datos(self, archivo):
        """Importa una base de datos desde un archivo JSON"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                nuevos_problemas = json.load(f)
            
            # Combinar con la base existente
            for id_problema, datos in nuevos_problemas.items():
                if id_problema not in self.problemas:
                    self.problemas[id_problema] = datos
            
            self.guardar_problemas()
            self.organizar_categorias()
            return True
        except Exception as e:
            print(f"Error importando base: {str(e)}")
            return False
