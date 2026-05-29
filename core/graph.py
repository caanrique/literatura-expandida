from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
import os
import subprocess
import tempfile
import traceback 
from datetime import datetime

# ================================
# CONFIGURACIÓN DE MODELOS
# ================================
USE_LLAMA_CLASSIFIER = os.getenv("USE_LLAMA_CLASSIFIER", "false").lower() == "true"

if USE_LLAMA_CLASSIFIER:
    print("🧠 Modo 3 MODELOS: Llama 3.1 (Clasificador) + Qwen (Trabajadores)")
    llm_classifier = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.1,
    num_ctx=1024
)
    llm_conceptual = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.3,
    num_ctx=1024
)
else:
    print("🧠 Modo 2 MODELOS: Qwen 2.5 (Clasificador + Conceptos) + Qwen Coder (Código)")
    llm_classifier = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434", temperature=0.1)
    llm_conceptual = llm_classifier

llm_coder = ChatOllama(
    model="qwen2.5-coder:7b",
    base_url="http://localhost:11434",
    temperature=0.1,
    num_ctx=1024  # ← Limitar contexto para ahorrar RAM
)

# ================================
# CONFIGURACIÓN DE AUTO-CORRECCIÓN
# ================================
MAX_ITERATIONS = 20  # Límite de intentos de corrección

# ================================
# ESTADO DEL GRAFO
# ================================
class State(TypedDict):
    messages: List[str]
    response: str
    model_used: str
    classifier_model: str
    iteration_count: int
    execution_success: bool
    error_traceback: Optional[str]
    code_file_path: Optional[str]
    project_name: str        # ← AGREGAR ESTO
    project_root: str        # ← AGREGAR ESTO

# ================================
# NODOS
# ================================
def classify_node(state: State):
    print(f"🧭 Clasificando... (iteración {state.get('iteration_count', 0)})")
    
    prompt = f"""Clasifica esta solicitud en UNA palabra: 'code', 'concept', o 'other'.
    Solicitud: {state['messages'][-1]}
    Respuesta (solo una palabra):"""
    
    response = llm_classifier.invoke(prompt)
    classification = response.content.strip().lower()
    
    classifier_name = "llama-3.1" if USE_LLAMA_CLASSIFIER else "qwen-2.5"
    print(f"✅ Clasificación: {classification} (usando {classifier_name})")
    
    return {
        "messages": state["messages"],
        "model_used": classification,
        "classifier_model": classifier_name,
        "iteration_count": state.get("iteration_count", 0),
        "execution_success": False,
        "error_traceback": None
    }

def generate_code_node(state: State):
    print("💻 Qwen Coder generando código...")
    
    # Si es una corrección, incluir el error anterior
    if state.get("error_traceback"):
        prompt = f"""Eres experto en Python. El siguiente código tiene un error.
        Corrígelo para que sea ejecutable sin errores.
        
        Código original:
        {state.get('response', '')}
        
        Error encontrado:
        {state.get('error_traceback', '')}
        
        Proporciona SOLO el código corregido, completo y ejecutable.
        Código:"""
    else:
        prompt = f"""Eres experto en Python. Genera código funcional y ejecutable.
        Solicitud: {state['messages'][-1]}
        
        Requisitos:
        - Código completo que se pueda ejecutar directamente
        - Incluye imports necesarios
        - Incluye ejemplos de uso si es apropiado
        - Sin explicaciones, solo código
        
        Código:"""
    
    response = llm_coder.invoke(prompt)
    code_content = response.content
    
    # Limpiar el código (quitar markdown si existe)
    if "```python" in code_content:
        code_content = code_content.split("```python")[-1].split("```")[0].strip()
    elif "```" in code_content:
        code_content = code_content.split("```")[-1].split("```")[0].strip()
    
    print(f"✅ Código generado: {len(code_content)} caracteres")
    
    return {
        "response": code_content,
        "model_used": "qwen-coder-7b",
        "classifier_model": state.get("classifier_model", "desconocido"),
        "iteration_count": state.get("iteration_count", 0),
        "execution_success": False,
        "error_traceback": None
    }

def execute_code_node(state: State):
    print("▶️ Ejecutando código en sandbox...")
    
    code = state.get("response", "")
    iteration = state.get("iteration_count", 0)
    project_name = state.get("project_name", "default")
    project_root = state.get("project_root", "")
    
    # ✅ Asegurar que project_root es una ruta absoluta
    if not project_root or project_root == "":
        # Fallback: usar la ruta desde donde se ejecuta Python
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Carpetas del proyecto (usando rutas absolutas)
    project_data_dir = os.path.abspath(os.path.join(project_root, 'projects', project_name, 'data'))
    output_dir = os.path.abspath(os.path.join(project_root, 'projects', project_name, 'output'))
    
    # Asegurar que las carpetas existen
    os.makedirs(project_data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear archivo temporal en la carpeta output del proyecto
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = os.path.abspath(os.path.join(output_dir, f"temp_exec_{timestamp}.py"))
    
    print(f"📂 Project root: {project_root}")
    print(f"📂 Data dir: {project_data_dir}")
    print(f"📂 Output dir: {output_dir}")
    print(f"📂 Temp file: {temp_file}")
    
    # Escribir el código en el archivo temporal
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    try:
        # Ejecutar CON LA CARPETA DATA COMO DIRECTORIO DE TRABAJO
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace',
            cwd=project_data_dir  # ← Se ejecuta en la carpeta data
        )
        
        if result.returncode == 0:
            print(f"✅ Ejecución exitosa (iteración {iteration + 1})")
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return {
                "execution_success": True,
                "error_traceback": None,
                "code_file_path": temp_file,
                "iteration_count": iteration
            }
        else:
            error_msg = f"STDERR:\n{result.stderr}\n\nSTDOUT:\n{result.stdout}"
            print(f"❌ Error en ejecución (iteración {iteration + 1}): {error_msg[:200]}...")
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return {
                "execution_success": False,
                "error_traceback": error_msg,
                "code_file_path": temp_file,
                "iteration_count": iteration
            }
    
    except subprocess.TimeoutExpired:
        error_msg = "Timeout: El código tardó más de 30 segundos en ejecutarse"
        print(f"⏱️ {error_msg}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return {
            "execution_success": False,
            "error_traceback": error_msg,
            "code_file_path": temp_file,
            "iteration_count": iteration
        }
    
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(f"❌ {error_msg}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return {
            "execution_success": False,
            "error_traceback": error_msg,
            "code_file_path": temp_file,
            "iteration_count": iteration
        }

def analyze_error_node(state: State):
    iteration = state.get("iteration_count", 0)
    
    if iteration >= MAX_ITERATIONS:
        print(f"⚠️ Límite de iteraciones alcanzado ({MAX_ITERATIONS})")
        return {
            "execution_success": False,
            "iteration_count": iteration,
            "needs_user_input": True
        }
    
    # Incrementar contador
    new_iteration = iteration + 1
    print(f"🔄 Intento de corrección {new_iteration}/{MAX_ITERATIONS}")
    
    return {
        "iteration_count": new_iteration,
        "execution_success": False
    }

def explain_concept_node(state: State):
    print("📚 Explicando concepto...")
    
    prompt = f"""Explica en español de forma clara y concisa.
    Pregunta: {state['messages'][-1]}
    
    Explicación:"""
    
    response = llm_conceptual.invoke(prompt)
    print(f"✅ Explicación generada: {len(response.content)} caracteres")
    
    return {
        "response": response.content,
        "model_used": "qwen-concept-7b",
        "classifier_model": state.get("classifier_model", "desconocido"),
        "iteration_count": state.get("iteration_count", 0),
        "execution_success": True,
        "error_traceback": None
    }

# ================================
# EDGES CONDICIONALES
# ================================
def route_after_classify(state: State):
    classification = state.get("model_used", "other")
    if "code" in classification:
        return "generate_code"
    elif "concept" in classification:
        return "explain_concept"
    else:
        return "explain_concept"

def route_after_execute(state: State):
    """Decide si el código funcionó o necesita corrección"""
    if state.get("execution_success", False):
        print("✅ Código ejecutable - Finalizando")
        return "end"
    else:
        iteration = state.get("iteration_count", 0)
        if iteration < MAX_ITERATIONS:
            print(f"🔄 Código con errores - Reintentando (intento {iteration + 1}/{MAX_ITERATIONS})")
            return "analyze_error"
        else:
            print(f"⚠️ Límite de iteraciones alcanzado - Requiere intervención humana")
            return "max_iterations_reached"

def route_after_analyze(state: State):
    """Después de analizar error, vuelve a generar código"""
    return "generate_code"

# ================================
# CONSTRUIR GRAFO
# ================================
workflow = StateGraph(State)

# Añadir nodos
workflow.add_node("classify", classify_node)
workflow.add_node("generate_code", generate_code_node)
workflow.add_node("execute_code", execute_code_node)
workflow.add_node("analyze_error", analyze_error_node)
workflow.add_node("explain_concept", explain_concept_node)

# Definir flujo
workflow.set_entry_point("classify")

# Después de clasificar
workflow.add_conditional_edges("classify", route_after_classify, {
    "generate_code": "generate_code",
    "explain_concept": "explain_concept"
})

# Después de generar código → ejecutar
workflow.add_edge("generate_code", "execute_code")

# Después de ejecutar → ¿éxito o error?
workflow.add_conditional_edges("execute_code", route_after_execute, {
    "end": END,
    "analyze_error": "analyze_error",
    "max_iterations_reached": END
})

# Después de analizar error → volver a generar código
workflow.add_edge("analyze_error", "generate_code")

# Concepto → fin
workflow.add_edge("explain_concept", END)

graph = workflow.compile()