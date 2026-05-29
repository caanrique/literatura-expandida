# ================================
# IMPORTS Y CONFIGURACIÓN DE RUTAS
# ================================
import streamlit as st
import sys
import os
from datetime import datetime
import subprocess
import json
import shutil

# Obtener la ruta absoluta del proyecto (la carpeta local-assistant)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Agregar la raíz al sys.path SI no está ya
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Debug: imprimir rutas para verificar
#print(f"📂 Project root: {project_root}")
#print(f"📂 Core path expected: {os.path.join(project_root, 'core')}")
#print(f"📂 Core exists: {os.path.exists(os.path.join(project_root, 'core'))}")

# Ahora sí importar el grafo
from core.graph import graph

# ================================
# FUNCIONES AUXILIARES
# ================================
def get_projects_list():
    """Obtiene lista de proyectos existentes"""
    projects_dir = os.path.join(project_root, 'projects')
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir)
        return []
    
    projects = [d for d in os.listdir(projects_dir) 
                if os.path.isdir(os.path.join(projects_dir, d))]
    return sorted(projects)

def create_new_project(project_name):
    """Crea un nuevo proyecto con sus carpetas"""
    if not project_name or project_name.strip() == "":
        return False, "El nombre no puede estar vacío"
    
    # Sanitizar nombre (solo letras, números, guiones)
    project_name = "".join(c for c in project_name if c.isalnum() or c in "-_").strip()
    
    if not project_name:
        return False, "Nombre inválido"
    
    projects_dir = os.path.join(project_root, 'projects')
    project_path = os.path.join(projects_dir, project_name)
    
    if os.path.exists(project_path):
        return False, f"El proyecto '{project_name}' ya existe"
    
    # Crear carpetas
    os.makedirs(os.path.join(project_path, 'output'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'history'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'data'), exist_ok=True)  # ← NUEVA: para archivos de datos
    
    # Crear archivo de historial vacío
    history_file = os.path.join(project_path, 'history', 'history.json')
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump({"conversations": []}, f, indent=2, ensure_ascii=False)
    
    # Crear config del proyecto
    config_file = os.path.join(project_path, 'config.json')
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({
            "name": project_name,
            "created": datetime.now().isoformat(),
            "description": ""
        }, f, indent=2, ensure_ascii=False)
    
    return True, f"Proyecto '{project_name}' creado exitosamente"

def load_project_history(project_name):
    """Carga el historial de un proyecto"""
    history_file = os.path.join(project_root, 'projects', project_name, 'history', 'history.json')
    if not os.path.exists(history_file):
        return {"conversations": []}
    
    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_to_history(project_name, prompt, response, classifier_model, executor_model, iterations=0):
    """Guarda una interacción en el historial del proyecto"""
    history_file = os.path.join(project_root, 'projects', project_name, 'history', 'history.json')
    
    # Cargar historial existente
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {"conversations": []}
    
    # Agregar nueva interacción
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "classifier_model": classifier_model,
        "executor_model": executor_model,
        "iterations": iterations
    }
    history["conversations"].append(new_entry)
    
    # Guardar (mantener últimos 50 para no hacerlo muy pesado)
    history["conversations"] = history["conversations"][-50:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_recent_files(project_name, folder='output', limit=10):
    """Obtiene archivos recientes de una carpeta del proyecto"""
    folder_path = os.path.join(project_root, 'projects', project_name, folder)
    if not os.path.exists(folder_path):
        return []
    
    files = sorted(os.listdir(folder_path), reverse=True)[:limit]
    return files

def get_all_project_files(project_name):
    """Obtiene TODOS los archivos de la carpeta data del proyecto"""
    data_dir = os.path.join(project_root, 'projects', project_name, 'data')
    if not os.path.exists(data_dir):
        return []
    
    files = []
    for f in os.listdir(data_dir):
        file_path = os.path.join(data_dir, f)
        if os.path.isfile(file_path):
            files.append({
                "name": f,
                "size": os.path.getsize(file_path),
                "path": file_path
            })
    return sorted(files, key=lambda x: x["name"])

def delete_project_file(project_name, filename):
    """Elimina un archivo de la carpeta data"""
    file_path = os.path.join(project_root, 'projects', project_name, 'data', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True, f"Archivo '{filename}' eliminado"
    return False, "Archivo no encontrado"

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="🧠 Asistente Local Qwen",
    page_icon="🤖",
    layout="wide"
)

# ================================
# ESTADO DE SESIÓN
# ================================
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None
if 'project_history' not in st.session_state:
    st.session_state.project_history = {"conversations": []}
if 'available_files_context' not in st.session_state:
    st.session_state.available_files_context = ""
if 'just_executed' not in st.session_state:  # ← AGREGAR ESTO
    st.session_state.just_executed = False
if 'last_prompt' not in st.session_state:  # ← NUEVO: guardar último prompt
    st.session_state.last_prompt = ""
if 'last_result' not in st.session_state:  # ← NUEVO: guardar último resultado
    st.session_state.last_result = None
if 'continue_count' not in st.session_state:  # ← NUEVO: contador de continuaciones
    st.session_state.continue_count = 0

# ================================
# BARRA LATERAL
# ================================
with st.sidebar:
    st.title("⚙️ Configuración")
    
    # ================================
    # GESTIÓN DE PROYECTOS 🎯
    # ================================
    st.subheader("📁 Gestión de Proyectos")
    
    # Obtener proyectos existentes
    projects = get_projects_list()
    
    # Selector de proyecto
    selected_project = st.selectbox(
        "Seleccionar proyecto:",
        options=[""] + projects,
        format_func=lambda x: "─ Crear nuevo proyecto ─" if x == "" else f"📁 {x}",
        index=0 if st.session_state.selected_project is None else (projects.index(st.session_state.selected_project) + 1 if st.session_state.selected_project in projects else 0)
    )
    
    # Debug: guardar y mostrar el valor seleccionado
    if selected_project and selected_project != "":
        st.session_state.selected_project = selected_project
        print(f"🔍 Dropdown: usuario seleccionó '{selected_project}'")

    # Indicador visual si no hay proyecto seleccionado
    if not st.session_state.selected_project:
        st.warning("⚠️ Selecciona un proyecto para continuar")

    # Si selecciona "Crear nuevo"
    if selected_project == "":
        st.markdown("---")
        new_project_name = st.text_input("Nombre del nuevo proyecto:")
        if st.button("📁 Crear Proyecto", use_container_width=True):
            success, message = create_new_project(new_project_name)
            if success:
                st.success(f"✅ {message}")
                st.rerun()  # Recargar para mostrar el nuevo proyecto
            else:
                st.error(f"❌ {message}")
    else:
        # Proyecto seleccionado
        st.session_state.selected_project = selected_project
        st.success(f"✅ Proyecto activo: **{selected_project}**")
        
        # Botón para abrir carpeta en explorador
        if st.button("📂 Abrir carpeta en Explorador", use_container_width=True):
            project_path = os.path.join(project_root, 'projects', selected_project)
            subprocess.run(['explorer', project_path])
        
        # Mostrar estadísticas del proyecto
        history = load_project_history(selected_project)
        num_conversations = len(history.get("conversations", []))
        files = get_recent_files(selected_project)
        data_files = get_all_project_files(selected_project)
        
        st.markdown("---")
        st.markdown(f"**📊 Estadísticas:**")
        st.markdown(f"- 💬 Conversaciones: `{num_conversations}`")
        st.markdown(f"- 📁 Archivos generados: `{len(files)}`")
        st.markdown(f"- 📎 Archivos de datos: `{len(data_files)}`")
    
    st.markdown("---")
    
    # ================================
    # SWITCH DE MODELOS
    # ================================
    st.subheader("🔄 Arquitectura")
    use_llama = st.toggle(
        "Usar Llama 3.1 como clasificador",
        value=False,
        help="Activa para usar 3 modelos (Llama clasifica, Qwen ejecuta). Desactiva para 2 modelos (Qwen hace todo)."
    )
    
    # Guardar en variable de entorno para que graph.py lo lea
    os.environ["USE_LLAMA_CLASSIFIER"] = "true" if use_llama else "false"
    
    # Mostrar estado actual
    if use_llama:
        st.success("✅ Modo 3 MODELOS activo")
        st.markdown("- 🧭 **Llama 3.1 8B**: Clasificador")
        st.markdown("- 💻 **Qwen Coder 7B**: Código")
        st.markdown("- 📚 **Qwen 2.5 7B**: Conceptos")
    else:
        st.info("ℹ️ Modo 2 MODELOS activo")
        st.markdown("- 🧭📚 **Qwen 2.5 7B**: Clasificador + Conceptos")
        st.markdown("- 💻 **Qwen Coder 7B**: Código")
    
    st.markdown("---")
    
    # Modelos instalados
    st.subheader("📦 Modelos en Ollama")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        st.code(result.stdout, language="text")
    except Exception as e:
        st.warning(f"No se pudo consultar Ollama: {e}")
    
    st.markdown("---")
    st.info("🔒 100% Local - Sin nube - Sin cuentas")

# ================================
# ÁREA PRINCIPAL
# ================================
st.title("🧠 Asistente Local con LangGraph + Qwen")
st.markdown("### Tu IA personal para código y conceptos, corriendo en tu hardware")
st.markdown("---")

# Verificar si hay proyecto seleccionado
if st.session_state.selected_project is None:
    st.warning("⚠️ **Selecciona o crea un proyecto en la barra lateral para comenzar**")
    st.info("💡 Consejo: Crea un proyecto por cada idea o sistema que estés desarrollando. Así mantienes el orden y el contexto separado.")
else:
    # Cargar historial del proyecto seleccionado
    st.session_state.project_history = load_project_history(st.session_state.selected_project)
    
    # ================================
    # SECCIÓN DE ARCHIVOS DE DATOS 📎
    # ================================
    st.subheader("📎 Archivos de Datos del Proyecto")
    
    data_files = get_all_project_files(st.session_state.selected_project)
    
    col_file1, col_file2 = st.columns([2, 1])
    
    with col_file1:
        # Upload de archivos
        uploaded_files = st.file_uploader(
            "Subir archivos al proyecto (CSV, TXT, JSON, etc.)",
            type=['csv', 'txt', 'json', 'xlsx', 'xml', 'pdf'],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        if uploaded_files:
            data_dir = os.path.join(project_root, 'projects', st.session_state.selected_project, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                file_path = os.path.join(data_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                st.success(f"✅ Archivo '{uploaded_file.name}' subido ({uploaded_file.size} bytes)")
            
            st.rerun()
    
    with col_file2:
        # Lista de archivos disponibles
        if data_files:
            st.markdown("**📂 Archivos disponibles:**")
            for file_info in data_files:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"📄 `{file_info['name']}` ({file_info['size']:,} bytes)")
                with col_b:
                    if st.button("🗑️", key=f"delete_{file_info['name']}"):
                        success, msg = delete_project_file(st.session_state.selected_project, file_info['name'])
                        if success:
                            st.success(f"✅ {msg}")
                            st.rerun()
        else:
            st.info("📭 No hay archivos de datos aún")
    
    # Construir contexto de archivos para el prompt
    if data_files:
        files_list = ", ".join([f["name"] for f in data_files])
        st.session_state.available_files_context = f"\n\nArchivos disponibles en la carpeta del proyecto: {files_list}"
        st.info(f"💡 El modelo puede usar estos archivos: `{files_list}`")
    else:
        st.session_state.available_files_context = ""
    
    st.markdown("---")
    
    # Mostrar historial reciente (expandible)
    with st.expander(f"📜 Historial de conversaciones ({len(st.session_state.project_history.get('conversations', []))})"):
        conversations = st.session_state.project_history.get("conversations", [])
        if conversations:
            for i, conv in enumerate(reversed(conversations[-10:])):  # Últimas 10
                with st.container():
                    st.markdown(f"**{i+1}. {conv.get('timestamp', 'N/A')}**")
                    st.markdown(f"🧭 Clasificador: `{conv.get('classifier_model', 'N/A')}` | 🤖 Ejecutor: `{conv.get('executor_model', 'N/A')}` | 🔄 Iteraciones: `{conv.get('iterations', 0)}`")
                    st.markdown(f"**Prompt:** {conv.get('prompt', 'N/A')[:200]}...")
                    st.markdown("---")
        else:
            st.info("No hay conversaciones aún. ¡Inicia tu primera solicitud!")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Tu solicitud")
        user_prompt = st.text_area(
            "Escribe lo que necesitas:",
            height=150,
            placeholder="Ej: Lee el archivo 'datos.csv' y calcula el promedio de la columna 'valor'"
        )
        
        # Añadir contexto de archivos al prompt si hay archivos
        if st.session_state.available_files_context:
            st.info(f"📎 **Contexto de archivos añadido automáticamente:** El modelo sabrá qué archivos puede usar.")
    
    with col2:
        st.subheader("📁 Archivos generados")
        files = get_recent_files(st.session_state.selected_project)
        if files:
            for f in files:
                st.markdown(f"- 📄 `{f}`")
        else:
            st.info("No hay archivos generados aún. ¡Ejecuta tu primera solicitud!")
    
    # Botón de ejecutar

# Botón de ejecutar
if st.button("🚀 Ejecutar Grafo", type="primary", use_container_width=True):
    
    # ✅ Manejo de continuación desde botón "7 iteraciones más"
    if st.session_state.get("continue_count", 0) > 0 and st.session_state.get("last_prompt", ""):
        user_prompt = st.session_state.last_prompt
        st.info(f"🔄 **Continuación #{st.session_state.continue_count}** con el prompt anterior")
    
    # ✅ VALIDACIÓN: Proyecto seleccionado
    if not st.session_state.selected_project or st.session_state.selected_project == "":
        st.error("⚠️ **Primero selecciona o crea un proyecto en la barra lateral**")
        st.info("💡 Usa el dropdown 'Seleccionar proyecto:' para elegir un proyecto existente o crear uno nuevo.")
    
    elif not user_prompt:
        st.warning("⚠️ Por favor escribe una solicitud")
    
    else:
        with st.spinner("🤖 El grafo está pensando..."):
            try:
                # Forzar recarga del módulo graph para que tome el nuevo valor del switch
                import importlib
                import core.graph as graph_module
                importlib.reload(graph_module)
                
                # Añadir contexto de archivos al prompt
                full_prompt = user_prompt + st.session_state.available_files_context
                
                # 🔍 DEBUG: Ver qué proyecto está seleccionado
                print(f"🔍 DEBUG: selected_project = '{st.session_state.selected_project}'")
                print(f"🔍 DEBUG: type = {type(st.session_state.selected_project)}")

                # Ejecutar
                result = graph_module.graph.invoke({
                    "messages": [full_prompt],
                    "project_name": st.session_state.selected_project if st.session_state.selected_project else "default",
                    "project_root": project_root
                })
                
                # Mostrar resultado
                st.success("✅ ¡Completado!")
                
                # Métricas del grafo
                col_meta1, col_meta2, col_meta3 = st.columns(3)
                with col_meta1:
                    st.metric("🤖 Modelo ejecutor", result.get("model_used", "desconocido"))
                with col_meta2:
                    st.metric("🧭 Modelo clasificador", result.get("classifier_model", "desconocido"))
                with col_meta3:
                    st.metric("🔄 Iteraciones", result.get("iteration_count", 0))
                
                # Mostrar respuesta
                if "response" in result:
                    st.markdown("### 📝 Resultado:")
                    
                    # Detectar si es código o texto
                    if "```python" in result["response"] or "def " in result["response"] or "import " in result["response"]:
                        st.code(result["response"], language="python")
                    else:
                        st.write(result["response"])
                    
                    # Guardar archivo versionado
                    output_dir = os.path.join(project_root, 'projects', st.session_state.selected_project, 'output')
                    os.makedirs(output_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"main_v{timestamp}.py"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("# Generado por LangGraph + Qwen Local\n")
                        f.write(f"# Proyecto: {st.session_state.selected_project}\n")
                        # Cada línea del prompt como comentario separado ✅ INDENTACIÓN CORREGIDA
                        for line in user_prompt.split('\n'):
                            f.write(f"# Prompt: {line}\n")
                        f.write(f"# Modelo clasificador: {result.get('classifier_model', 'desconocido')}\n")
                        f.write(f"# Modelo ejecutor: {result.get('model_used', 'desconocido')}\n")
                        f.write(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"# Iteraciones de corrección: {result.get('iteration_count', 0)}\n")
                        f.write(f"# Switch Llama: {use_llama}\n")
                        f.write(f"# Ejecución exitosa: {result.get('execution_success', False)}\n\n")
                        f.write(result["response"])
                    
                    st.info(f"💾 Guardado en: `{filepath}`")
                    
                    # Guardar en historial
                    save_to_history(
                        st.session_state.selected_project,
                        user_prompt,
                        result["response"],
                        result.get("classifier_model", "desconocido"),
                        result.get("model_used", "desconocido"),
                        result.get("iteration_count", 0)
                    )
                    
                    # Resetear contador de continuación después de guardar exitosamente
                    if st.session_state.get("continue_count", 0) > 0:
                        st.session_state.continue_count = 0
                        st.session_state.last_prompt = ""
                        st.session_state.last_result = None
                    
                    st.session_state.just_executed = True
                    st.success("✅ Ejecución completada. El historial se actualizará en la próxima interacción.")

                else:
                    st.warning("⚠️ No se generó respuesta")
                
                # ✅ VERIFICAR LÍMITE DE ITERACIONES (DENTRO DEL TRY) ✅
                if result and result.get("iteration_count", 0) >= 20:
                    st.warning("⚠️ **Se alcanzó el límite de 20 iteraciones**")
                    st.info("💡 El sistema intentó corregir el código 20 veces pero no logró una ejecución exitosa.")
                    
                    # Mostrar el último código generado
                    if result.get("response"):
                        st.markdown("### 📝 Último código generado:")
                        st.code(result["response"], language="python")
                    
                    # Botón para continuar con 7 iteraciones más
                    st.markdown("---")
                    col_cont1, col_cont2 = st.columns(2)
                    
                    with col_cont1:
                        if st.button("🔄 Continuar con 7 iteraciones más", type="primary", use_container_width=True):
                            st.session_state.continue_count += 1
                            st.session_state.last_prompt = user_prompt
                            st.session_state.last_result = result
                            st.rerun()
                    
                    with col_cont2:
                        if st.button("⚠️ Detener y guardar", use_container_width=True):
                            st.info("💡 Puedes ajustar tu prompt e intentar de nuevo con más detalles.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Ver detalles del error"):
                    st.code(str(e), language="text")