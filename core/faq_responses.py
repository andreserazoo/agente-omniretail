from __future__ import annotations

import unicodedata


def _normalize(text: str) -> str:
    raw = " ".join((text or "").strip().lower().split())
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
        "hello",
        "hi",
        "hola parce",
        "hola compa",
        "hola necesito ayuda",
        "hola, necesito ayuda",
        "quiero hacer una consulta",
        "quiero consultar",
        "me puedes ayudar",
        "puedes ayudarme",
        "me colaboras",
        "me colaboras porfa",
        "me ayudas",
        "ando buscando ayuda",
        "tengo una duda",
        "tengo una preguntica",
        "tengo una consulta",
        "quiero informacion",
        "quisiera informacion",
        "necesito ayuda",
        "buen dia me regalas info",
    ]

    if any(token in text for token in greeting_tokens):
        return (
            "Hola, soy el asistente de OmniRetail. "
            "Puedo ayudarte con pedidos, envios, garantias, devoluciones, "
            "politicas, precios y stock. ¿Que necesitas consultar?"
        )

    if any(token in text for token in ["gracias", "muchas gracias", "mil gracias", "vale gracias", "ok gracias"]):
        return "Con gusto. Si quieres, puedo seguir ayudandote con pedidos, productos, politicas, garantias o devoluciones."

    if any(token in text for token in ["ok", "vale", "listo", "entendido", "perfecto"]):
        return "Perfecto. Si quieres continuar, dime si necesitas revisar un pedido, un producto o alguna politica."

    if any(
        token in text
        for token in [
            "pago",
            "pagos",
            "metodos de pago",
            "metodo de pago",
            "formas de pago",
            "medios de pago",
            "como puedo pagar",
            "como se puede pagar",
            "con que puedo pagar",
            "cuales son los metodos de pago",
        ]
    ):
        return (
            "OmniRetail maneja medios de pago habilitados al momento de la compra. "
            "Si quieres, puedo orientarte sobre metodos de pago y condiciones generales."
        )

    if any(
        token in text
        for token in [
            "whatsapp",
            "atencion",
            "canales de atencion",
            "servicio al cliente",
            "soporte",
            "asesor",
            "ayuda por whatsapp",
        ]
    ):
        return (
            "OmniRetail cuenta con canales de atencion para soporte al cliente. "
            "Tambien puedes gestionar pedidos desde tu cuenta en la plataforma."
        )

    if any(
        token in text
        for token in [
            "cobertura",
            "envios a todo colombia",
            "hacen envios",
            "todo colombia",
            "zona rural",
            "zonas rurales",
            "area rural",
            "areas rurales",
            "cobertura rural",
            "llegan a zonas rurales",
            "envian a zonas rurales",
        ]
    ):
        return (
            "La cobertura depende de la ubicacion. "
            "En zonas rurales el envio puede estar sujeto a disponibilidad logistica y a tiempos de entrega mayores."
        )

    if any(
        token in text
        for token in [
            "tiempo de entrega",
            "cuanto tarda",
            "dias habiles",
            "tarda el envio",
            "tarda",
            "no llega en el tiempo estimado",
            "no llego en el tiempo estimado",
            "mi pedido no llega a tiempo",
            "mi pedido esta demorado",
            "mi pedido se demoro",
            "pedido retrasado",
            "pedido demorado",
        ]
    ):
        return (
            "Los tiempos de entrega dependen de la zona y del estado logistico del pedido. "
            "Si el pedido es tuyo, tambien puedo ayudarte a revisarlo despues de verificar tu identidad."
        )

    if any(
        token in text
        for token in [
            "producto llego incompleto",
            "producto vino incompleto",
            "me llego incompleto",
            "llego incompleto",
            "faltan piezas",
            "faltan accesorios",
            "vino sin accesorios",
        ]
    ):
        return (
            "Si el producto llego incompleto, debes reportarlo cuanto antes con el detalle de lo faltante y el estado del paquete. "
            "Si quieres, tambien puedo orientarte con la politica aplicable."
        )

    if any(
        token in text
        for token in [
            "rechazar el paquete",
            "rechazar paquete",
            "rechazar el pedido",
            "rechazar en la puerta",
            "rechazarlo en la puerta",
            "no recibir el paquete",
            "no recibir el pedido",
        ]
    ):
        return (
            "En algunos casos es posible rechazar el paquete al momento de la entrega, pero eso depende del estado del pedido y de la novedad reportada. "
            "Si quieres, puedo orientarte con la politica de envios o devoluciones."
        )

    if any(
        token in text
        for token in [
            "celular se mojo",
            "telefono se mojo",
            "se me mojo el celular",
            "se me mojo el telefono",
            "mojo el celular",
            "se mojo",
            "mojo",
            "celular moj",
            "telefono moj",
            "daño por agua",
            "dano por agua",
            "danos por agua",
        ]
    ):
        return (
            "Los danos por agua suelen estar sujetos a exclusiones de garantia en productos electronicos. "
            "Si quieres, puedo buscar la politica de garantia relacionada."
        )

    if any(
        token in text
        for token in [
            "cuanto tiempo tengo para reclamar garantia",
            "tiempo tengo para reclamar garantia",
            "garantia en electronica",
            "garantia de electronica",
            "garantia para electronica",
            "vigencia de garantia en electronica",
            "reclamar garantia en electronica",
        ]
    ):
        return (
            "El tiempo de garantia en electronica depende de la categoria y del producto especifico. "
            "Si quieres, puedo ayudarte con la politica de garantia para darte mas detalle."
        )

    if any(
        token in text
        for token in [
            "tecnico no era autorizado",
            "tecnico no autorizado",
            "reparado por tecnico no autorizado",
            "reparo un tecnico no autorizado",
            "servicio tecnico no autorizado",
            "tecnico que reparo",
            "no era autorizado",
        ]
    ):
        return (
            "Si un producto fue intervenido por un tecnico no autorizado, la garantia puede verse afectada segun la politica aplicable. "
            "Si quieres, puedo ayudarte a revisar esa politica."
        )

    if any(
        token in text
        for token in [
            "producto de belleza abierto",
            "devolver producto de belleza abierto",
            "producto abierto de belleza",
            "cosmetico abierto",
            "producto de cuidado personal abierto",
        ]
    ):
        return (
            "Los productos de belleza o cuidado personal abiertos suelen tener restricciones de devolucion por higiene y seguridad. "
            "Si quieres, puedo buscar la politica de devoluciones relacionada."
        )

    if any(
        token in text
        for token in [
            "cancelar un pedido que ya fue despachado",
            "cancelar pedido despachado",
            "pedido ya fue despachado",
            "pedido ya despachado",
            "cancelar despues del despacho",
        ]
    ):
        return (
            "Cuando un pedido ya fue despachado, normalmente aplican restricciones para cancelacion inmediata. "
            "Si quieres, puedo orientarte con la politica de envio o devolucion."
        )

    if any(
        token in text
        for token in [
            "informacion general",
            "informacion",
            "general",
            "quiero info",
        ]
    ):
        return (
            "Puedo ayudarte con informacion publica sobre pagos, atencion, cobertura y tiempos generales. "
            "Si necesitas algo mas especifico, dime el tema."
        )

    return None
