from flask import Flask, jsonify, render_template, request
import re

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.get("/")
def inicio():
    return render_template("index.html")


def responder_asistente(mensaje: str) -> str:
    """Respuestas informativas básicas; no reemplaza la orientación sanitaria."""
    texto = re.sub(r"\s+", " ", mensaje.lower()).strip()

    if any(p in texto for p in ("hola", "buenas", "buenos días", "buenas tardes")):
        return ("¡Hola! Soy el asistente informativo de Huanguelén Dona Vida. "
                "Puedo orientarte sobre donación de sangre, CPH y el registro de donantes.")
    if any(p in texto for p in ("cph", "progenitor", "médula ósea", "medula osea")):
        return ("Las células progenitoras hematopoyéticas (CPH) dan origen a los distintos "
                "componentes de la sangre. Se encuentran principalmente en la médula ósea y "
                "también pueden obtenerse de sangre periférica o de sangre de cordón umbilical.")
    if any(p in texto for p in ("registro", "inscrib", "anotar", "donante de cph")):
        return ("El Registro Nacional de Donantes de Células Progenitoras Hematopoyéticas "
                "permite buscar personas compatibles con pacientes que necesitan un trasplante. "
                "La inscripción y los pasos correspondientes se realizan por canales oficiales.")
    if any(p in texto for p in ("requisito", "edad", "peso", "puedo donar", "aptitud")):
        return ("Los requisitos para donar dependen de las normas vigentes y de la evaluación "
                "del equipo de salud. Consultá con un centro de donación habilitado para conocer "
                "si podés donar y recibir información actualizada.")
    if any(p in texto for p in ("sangre", "donar", "donación", "donacion", "transfusión", "transfusion")):
        return ("La donación voluntaria y habitual ayuda a mantener sangre disponible para "
                "quienes la necesitan. La evaluación y la extracción se realizan en un centro "
                "habilitado por personal capacitado.")
    if any(p in texto for p in ("turno", "horario", "dónde", "donde", "lugar", "centro")):
        return ("Para conocer lugares, horarios y turnos disponibles, consultá los canales "
                "oficiales de salud de tu zona. Los datos pueden cambiar.")
    return ("Puedo orientarte sobre donación de sangre, células progenitoras hematopoyéticas "
            "(CPH) y el registro de donantes. Para consultas médicas personales, hablá con "
            "un profesional de salud o con un centro habilitado.")


@app.post("/api/chat")
def chat():
    datos = request.get_json(silent=True) or {}
    mensaje = datos.get("message", "")
    if not isinstance(mensaje, str) or not mensaje.strip():
        return jsonify(error="Escribí una consulta para continuar."), 400
    if len(mensaje) > 1000:
        return jsonify(error="La consulta es demasiado larga. Máximo: 1000 caracteres."), 400
    return jsonify(reply=responder_asistente(mensaje))


@app.get("/api/estado")
def estado():
    return jsonify(status="ok", aplicacion="Huanguelén Dona Vida")


if __name__ == "__main__":
    # Solo para desarrollo local. En producción, usar un servidor WSGI.
    app.run(host="127.0.0.1", port=5000, debug=True)
