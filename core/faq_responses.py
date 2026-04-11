from __future__ import annotations

import unicodedata


def _normalize(text: str) -> str:
    raw = (text or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", raw)
    return "".join(
        char for char in normalized if not unicodedata.combining(char)
    )


def build_public_faq_response(user_message: str) -> str | None:
    text = _normalize(user_message)

    if not text:
        return None

    greeting_tokens = [
        "hola",
        "hola!",
        "holi",
        "buenas",
        "buenasss",
        "buenos dias",
        "buen dia",
        "buenas tardes",
        "buenas noches",
        "ey buenas",
        "hola parce",
        "hola compa",
        "hello",
        "hi",
        "hola, necesito ayuda",
        "hola necesito ayuda",
        "quiero hacer una consulta",
        "quiero consultar",
        "me puedes ayudar",
        "puedes ayudarme",
        "me colaboras",
        "me colaboras porfa",
        "me ayudas",
        "hola parce me ayudas",
        "quiero info rapidita",
        "ando buscando ayuda",
        "tengo una duda",
        "tengo una preguntica",
        "tengo una consulta",
        "quiero informacion",
        "quisiera informacion",
        "necesito ayuda",
        "buen dia, me regalas info",
    ]

    if any(token in text for token in greeting_tokens):
        return (
            "Hola, soy el asistente de OmniRetail. "
            "Puedo ayudarte con pedidos, envios, garantias, devoluciones, "
            "politicas, precios y stock. ¿Que necesitas consultar?"
        )

    if any(token in text for token in ["pago", "pagos", "metodos de pago"]):
        return (
            "Puedes consultar metodos de pago disponibles para compras en OmniRetail. "
            "En esta version base, la ruta publica de pagos ya quedo habilitada correctamente."
        )

    if any(token in text for token in ["whatsapp", "atencion", "canales de atencion"]):
        return (
            "OmniRetail cuenta con canales de atencion para soporte al cliente. "
            "Tambien puedes gestionar pedidos desde tu cuenta en la plataforma."
        )

    if any(
        token in text
        for token in ["cobertura", "envio", "envios a todo colombia", "hacen env", "todo colombia"]
    ):
        return (
            "Realizamos envios a todo Colombia. "
            "Los tiempos varian segun la ubicacion y las condiciones logisticas."
        )

    if any(
        token in text
        for token in ["tiempo de entrega", "cuanto tarda", "dias habiles", "tarda el env", "tarda"]
    ):
        return (
            "Los tiempos de entrega dependen de la zona. "
            "Si quieres, tambien puedes preguntarme por politicas de envio para darte mas detalle."
        )

    if any(token in text for token in ["informacion general", "informacion", "general", "quiero info"]):
        return (
            "Puedo ayudarte con informacion publica sobre pagos, atencion, cobertura y tiempos generales. "
            "Si necesitas algo mas especifico, dime el tema."
        )

    return None
