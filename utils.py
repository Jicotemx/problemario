import os
import json
import subprocess
from jinja2 import Environment, FileSystemLoader

class MathProblemManager:
    # Mantén aquí todas las funciones de la clase original excepto:
    # - Las que interactúan con Tkinter
    # - cargar_problemas() y guardar_problemas() (ahora manejadas por GitHub)
    # - La función __init__ ahora no carga automáticamente los problemas
    
    def crear_template_si_no_existe(self):
        """Crea la plantilla LaTeX si no existe"""
        if not os.path.exists("template.tex"):
            with open("template.tex", 'w', encoding='utf-8') as f:
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

    # Mantén aquí el resto de las funciones (agregar_problema, editar_problema, etc.)
    # ... [El resto de tu código original de la clase MathProblemManager] ...

# Agrega esto al final de utils.py
class PrintOptionsDialog:
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Opciones de Impresión")
        self.geometry("300x200")
        self.resizable(False, False)
        self.result = None
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Seleccione qué desea incluir:").pack(pady=10)
        
        self.include_soluciones = tk.BooleanVar(value=True)
        self.include_respuestas = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(main_frame, text="Incluir soluciones (procedimientos)", 
                       variable=self.include_soluciones).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(main_frame, text="Incluir respuestas", 
                       variable=self.include_respuestas).pack(anchor=tk.W, pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def aceptar(self):
        self.result = {
            'include_soluciones': self.include_soluciones.get(),
            'include_respuestas': self.include_respuestas.get()
        }
        self.destroy()


