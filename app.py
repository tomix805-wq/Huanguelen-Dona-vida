from flask import (
    Flask, jsonify, render_template, request,
    session, redirect, url_for
)
import re
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timezone

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
    conexion = conectar_db()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pagina TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


def registrar_visita(pagina):
    conexion = conectar_db()

    fecha = datetime.now(timezone.utc).isoformat()

    conexion.execute(
        """
        INSERT INTO visitas (pagina, fecha)
        VALUES (?, ?)
        """,
        (pagina, fecha)
    )

    conexion.commit()
    conexion.close()


# Inicializar base de datos
inicializar_db()


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.get("/")
def inicio():
    registrar_visita("inicio")
    return render_template("index.html")


# ==========================================
# ASISTENTE INFORMATIVO LOCAL
# SIN INTELIGENCIA ARTIFICIAL
# ==========================================

def responder_asistente(mensaje: str) -> str:

    texto = re.sub(r"\s+", " ", mensaje.lower()).strip()

    if any(p in texto for p in (
        "hola", "buenas", "buenos días",
        "buenas tardes"
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
        "requisito", "edad", "peso",
        "puedo donar", "aptitud"
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
        "turno", "horario", "dónde",
        "donde", "lugar", "centro"
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

    return jsonify(
        reply=responder_asistente(mensaje)
    )


# ==========================================
# API DE ESTADÍSTICAS
# ==========================================

@app.get("/api/estadisticas")
def estadisticas():

    conexion = conectar_db()

    total_visitas = conexion.execute("""
        SELECT COUNT(*) AS total
        FROM visitas
    """).fetchone()["total"]

    visitas_inicio = conexion.execute("""
        SELECT COUNT(*) AS total
        FROM visitas
        WHERE pagina = ?
    """, ("inicio",)).fetchone()["total"]

    conexion.close()

    return jsonify({
        "total_visitas": total_visitas,
        "visitas_inicio": visitas_inicio
    })


# ==========================================
# ESTADO DEL SERVIDOR
# ==========================================

@app.get("/api/estado")
def estado():

    return jsonify(
        status="ok",
        aplicacion="Huanguelén Dona Vida",
        base_datos="conectada"
    )


# ==========================================
# ACCESO AL PANEL DE ADMINISTRACIÓN
# ==========================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

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
def admin_panel():

    if not session.get("administrador"):
        return redirect(url_for("admin_login"))

    conexion = conectar_db()

    total_visitas = conexion.execute("""
        SELECT COUNT(*) AS total
        FROM visitas
    """).fetchone()["total"]

    visitas_dia = conexion.execute("""
        SELECT DATE(fecha) AS dia, COUNT(*) AS total
        FROM visitas
        WHERE DATE(fecha) >= DATE('now', '-6 days')
        GROUP BY DATE(fecha)
        ORDER BY dia ASC
    """).fetchall()

    conexion.close()

    max_visitas = max(
        [fila["total"] for fila in visitas_dia],
        default=1
    )

    return render_template(
        "admin.html",
        total_visitas=total_visitas,
        visitas_dia=visitas_dia,
        max_visitas=max_visitas
    )


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
