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
