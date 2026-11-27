
from flask import (
    Flask, jsonify, render_template, request,
    session, redirect, url_for
)
import re
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timezone
from functools import wraps

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "clave-local-solo-desarrollo"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "CAMBIAR-ESTA-CLAVE"
)

CARPETA_PROYECTO = Path(__file__).resolve().parent
BASE_DATOS = CARPETA_PROYECTO / "huanguelen.db"


# ==========================================
# BASE DE DATOS SQLITE
# ==========================================

def conectar_db():
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    with conectar_db() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS visitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pagina TEXT NOT NULL,
                fecha TEXT NOT NULL
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL
            )
        """)


def registrar_visita(pagina):
    with conectar_db() as conexion:
        conexion.execute(
            """
            INSERT INTO visitas (pagina, fecha)
            VALUES (?, ?)
            """,
            (pagina, datetime.now(timezone.utc).isoformat())
        )


inicializar_db()


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def administrador_requerido(funcion):
    @wraps(funcion)
    def decorada(*args, **kwargs):
        if not session.get("administrador"):
            return redirect(url_for("admin_login"))
        return funcion(*args, **kwargs)
    return decorada


def validar_fecha_hora(fecha, hora):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        datetime.strptime(hora, "%H:%M")
        return True
    except (ValueError, TypeError):
        return False


def obtener_actividades():
    with conectar_db() as conexion:
        return conexion.execute("""
            SELECT id, titulo, descripcion, fecha, hora
            FROM actividades
            ORDER BY fecha ASC, hora ASC
        """).fetchall()


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.get("/")
def inicio():
    registrar_visita("inicio")
    return render_template("index.html")


# ==========================================
# ASISTENTE INFORMATIVO LOCAL
# ==========================================

def responder_asistente(mensaje: str) -> str:
    texto = re.sub(r"\s+", " ", mensaje.lower()).strip()

    if any(p in texto for p in (
        "hola", "buenas", "buenos días", "buenas tardes"
    )):
        return (
            "¡Hola! Soy el asistente informativo de "
            "Huanguelén Dona Vida. Puedo orientarte sobre "
            "donación de sangre, CPH y el registro de donantes."
        )

    if any(p in texto for p in (
        "cph", "progenitor", "médula ósea", "medula osea"
    )):
        return (
            "Las células progenitoras hematopoyéticas (CPH) "
            "dan origen a los distintos componentes de la sangre. "
            "Se encuentran principalmente en la médula ósea y "
            "también pueden obtenerse de sangre periférica o "
            "de sangre de cordón umbilical."
        )

    if any(p in texto for p in (
        "registro", "inscrib", "anotar", "donante de cph"
    )):
        return (
            "El Registro Nacional de Donantes de Células "
            "Progenitoras Hematopoyéticas permite buscar personas "
            "compatibles con pacientes que necesitan un trasplante. "
            "La inscripción y los pasos correspondientes se "
            "realizan por canales oficiales."
        )

    if any(p in texto for p in (
        "requisito", "edad", "peso", "puedo donar", "aptitud"
    )):
        return (
            "Los requisitos para donar dependen de las normas "
            "vigentes y de la evaluación del equipo de salud. "
            "Consultá con un centro de donación habilitado para "
            "conocer si podés donar y recibir información actualizada."
        )

    if any(p in texto for p in (
        "sangre", "donar", "donación", "donacion",
        "transfusión", "transfusion"
    )):
        return (
            "La donación voluntaria y habitual ayuda a mantener "
            "sangre disponible para quienes la necesitan. "
            "La evaluación y la extracción se realizan en un "
            "centro habilitado por personal capacitado."
        )

    if any(p in texto for p in (
        "turno", "horario", "dónde", "donde", "lugar", "centro"
    )):
        return (
            "Para conocer lugares, horarios y turnos disponibles, "
            "consultá los canales oficiales de salud de tu zona. "
            "Los datos pueden cambiar."
        )

    return (
        "Puedo orientarte sobre donación de sangre, células "
        "progenitoras hematopoyéticas (CPH) y el registro de "
        "donantes. Para consultas médicas personales, hablá con "
        "un profesional de salud o con un centro habilitado."
    )


# ==========================================
# API DEL ASISTENTE
# ==========================================

@app.post("/api/chat")
def chat():
    datos = request.get_json(silent=True) or {}
    mensaje = datos.get("message", "")

    if not isinstance(mensaje, str) or not mensaje.strip():
        return jsonify(
            error="Escribí una consulta para continuar."
        ), 400

    if len(mensaje) > 1000:
        return jsonify(
            error="La consulta es demasiado larga. Máximo: 1000 caracteres."
        ), 400

    return jsonify(reply=responder_asistente(mensaje))


# ==========================================
# API DE ESTADÍSTICAS
# ==========================================

@app.get("/api/estadisticas")
def estadisticas():
    with conectar_db() as conexion:
        total_visitas = conexion.execute("""
            SELECT COUNT(*) AS total FROM visitas
        """).fetchone()["total"]

        visitas_inicio = conexion.execute("""
            SELECT COUNT(*) AS total
            FROM visitas
            WHERE pagina = ?
        """, ("inicio",)).fetchone()["total"]

    return jsonify({
        "total_visitas": total_visitas,
        "visitas_inicio": visitas_inicio
    })


# ==========================================
# API DE ACTIVIDADES PÚBLICAS
# ==========================================

@app.get("/api/actividades")
def api_actividades():
    actividades = obtener_actividades()

    return jsonify([
        {
            "id": actividad["id"],
            "titulo": actividad["titulo"],
            "descripcion": actividad["descripcion"],
            "fecha": actividad["fecha"],
            "hora": actividad["hora"]
        }
        for actividad in actividades
    ])


# ==========================================
# ESTADO DEL SERVIDOR
# ==========================================

@app.get("/api/estado")
def estado():
    try:
        with conectar_db() as conexion:
            conexion.execute("SELECT 1")

        return jsonify(
            status="ok",
            aplicacion="Huanguelén Dona Vida",
            base_datos="conectada"
        )
    except sqlite3.Error:
        return jsonify(
            status="error",
            aplicacion="Huanguelén Dona Vida",
            base_datos="desconectada"
        ), 500


# ==========================================
# ACCESO AL PANEL DE ADMINISTRACIÓN
# ==========================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("administrador"):
        return redirect(url_for("admin_panel"))

    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["administrador"] = True
            return redirect(url_for("admin_panel"))

        return render_template(
            "admin_login.html",
            error="Contraseña incorrecta. Intentá nuevamente."
        )

    return render_template("admin_login.html")


# ==========================================
# PANEL DE ADMINISTRACIÓN
# ==========================================

@app.get("/admin")
@administrador_requerido
def admin_panel():
    with conectar_db() as conexion:
        total_visitas = conexion.execute("""
            SELECT COUNT(*) AS total FROM visitas
        """).fetchone()["total"]

        visitas_dia = conexion.execute("""
            SELECT DATE(fecha) AS dia, COUNT(*) AS total
            FROM visitas
            WHERE DATE(fecha) >= DATE('now', '-6 days')
            GROUP BY DATE(fecha)
            ORDER BY dia ASC
        """).fetchall()

        actividades = conexion.execute("""
            SELECT id, titulo, descripcion, fecha, hora
            FROM actividades
            ORDER BY fecha ASC, hora ASC
        """).fetchall()

    max_visitas = max(
        [fila["total"] for fila in visitas_dia],
        default=1
    )

    return render_template(
        "admin.html",
        total_visitas=total_visitas,
        visitas_dia=visitas_dia,
        max_visitas=max_visitas,
        actividades=actividades
    )


# ==========================================
# CREAR ACTIVIDAD
# ==========================================

@app.post("/admin/actividades/crear")
@administrador_requerido
def crear_actividad():
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    fecha = request.form.get("fecha", "").strip()
    hora = request.form.get("hora", "").strip()

    if not titulo or len(titulo) > 120:
        return redirect(url_for(
            "admin_panel",
            error="El título es obligatorio y debe tener hasta 120 caracteres."
        ))

    if len(descripcion) > 1000:
        return redirect(url_for(
            "admin_panel",
            error="La descripción no puede superar los 1000 caracteres."
        ))

    if not validar_fecha_hora(fecha, hora):
        return redirect(url_for(
            "admin_panel",
            error="La fecha o la hora no son válidas."
        ))

    with conectar_db() as conexion:
        conexion.execute("""
            INSERT INTO actividades (titulo, descripcion, fecha, hora)
            VALUES (?, ?, ?, ?)
        """, (titulo, descripcion, fecha, hora))

    return redirect(url_for("admin_panel", mensaje="Actividad creada."))


# ==========================================
# EDITAR ACTIVIDAD
# ==========================================

@app.post("/admin/actividades/<int:actividad_id>/editar")
@administrador_requerido
def editar_actividad(actividad_id):
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    fecha = request.form.get("fecha", "").strip()
    hora = request.form.get("hora", "").strip()

    if (
        not titulo
        or len(titulo) > 120
        or len(descripcion) > 1000
        or not validar_fecha_hora(fecha, hora)
    ):
        return redirect(url_for(
            "admin_panel",
            error="Revisá los datos de la actividad."
        ))

    with conectar_db() as conexion:
        resultado = conexion.execute("""
            UPDATE actividades
            SET titulo = ?, descripcion = ?, fecha = ?, hora = ?
            WHERE id = ?
        """, (titulo, descripcion, fecha, hora, actividad_id))

    if resultado.rowcount == 0:
        return redirect(url_for(
            "admin_panel",
            error="No se encontró esa actividad."
        ))

    return redirect(url_for("admin_panel", mensaje="Actividad actualizada."))


# ==========================================
# ELIMINAR ACTIVIDAD
# ==========================================

@app.post("/admin/actividades/<int:actividad_id>/eliminar")
@administrador_requerido
def eliminar_actividad(actividad_id):
    with conectar_db() as conexion:
        resultado = conexion.execute("""
            DELETE FROM actividades WHERE id = ?
        """, (actividad_id,))

    if resultado.rowcount == 0:
        return redirect(url_for(
            "admin_panel",
            error="No se encontró esa actividad."
        ))

    return redirect(url_for("admin_panel", mensaje="Actividad eliminada."))


# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ==========================================
# INICIAR APLICACIÓN
# ==========================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
