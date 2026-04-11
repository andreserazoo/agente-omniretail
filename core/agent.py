from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import unicodedata

from core.anti_hallucination import (
    build_missing_tool_response,
    has_required_tool_usage_since,
)
from core.entity_extractor import extract_entities
from core.faq_responses import build_public_faq_response
from core.formatters import (
    format_currency_cop,
    format_delivery_method,
    format_short_text,
    format_status_label,
    format_value,
)
from core.guards import evaluate_security_guards
from core.policy_response_builder import build_policy_answer
from core.router import decide_route
from core.session_context import (
    add_conversation_message,
    get_context_value,
    get_session_customer,
    get_tool_trace_length,
    has_verified_customer,
    reset_session,
    set_context_value,
)
from tools.auth_tools import verify_customer_by_dni, verify_customer_by_phone
from tools.customer_tools import list_customer_orders
from tools.order_item_tools import get_order_item_by_product, list_order_items
from tools.order_tools import (
    get_order_amounts,
    get_order_shipments,
    get_order_status,
    get_order_tracking_history,
    order_belongs_to_customer,
)
from tools.policy_tools import search_policy_sections
from tools.product_tools import get_product_price, get_product_stock


@dataclass
class AgentResponse:
    content: str

    def __str__(self) -> str:
        return self.content


class OmniRetailAgent:
    def __init__(self, streaming: bool = False) -> None:
        self.streaming = streaming

    def __call__(self, user_message: str) -> AgentResponse:
        return self.invoke(user_message)

    def invoke(self, user_message: Any) -> AgentResponse:
        normalized_message = self._normalize_user_message(user_message)
        add_conversation_message("user", normalized_message)

        guard = evaluate_security_guards(normalized_message)
        if guard.blocked:
            final_text = guard.response or "No puedo procesar esa solicitud."
            add_conversation_message("assistant", final_text)
            return AgentResponse(content=final_text)

        entities = extract_entities(normalized_message)
        route = decide_route(normalized_message)

        if route.intent != "unknown":
            set_context_value("last_intent", route.intent)
        if entities.order_id:
            set_context_value("last_order_id", entities.order_id)
        if entities.product_id:
            set_context_value("last_product_id", entities.product_id)

        auth_text = self._try_inline_authentication(entities, normalized_message)
        if auth_text:
            add_conversation_message("assistant", auth_text)
            return AgentResponse(content=auth_text)

        trace_start_index = get_tool_trace_length()
        final_text = self._handle_route(
            normalized_message,
            route,
            entities,
            trace_start_index,
        )

        add_conversation_message("assistant", final_text)
        return AgentResponse(content=final_text)

    def reset_memory(self) -> None:
        reset_session()

    def _normalize_user_message(self, user_message: Any) -> str:
        if user_message is None:
            return ""
        if isinstance(user_message, str):
            return user_message.strip()
        return str(user_message).strip()

    def _try_inline_authentication(self, entities, original_message: str) -> str | None:
        lowered = self._normalize_lookup_text(original_message)
        awaiting_auth = bool(get_context_value("awaiting_auth"))

        explicit_auth_signal = any(
            token in lowered
            for token in [
                "mi documento",
                "mi cédula",
                "mi cedula",
                "mi dni",
                "mi teléfono",
                "mi telefono",
                "mi número",
                "mi numero",
                "mi doc",
                "mi identificacion",
                "documento",
                "identificacion",
                "doc",
                "cedula",
                "cc",
                "mi cc",
                "mi celular",
                "mi cel",
                "documento es",
                "doc es",
                "cedula es",
                "identificacion es",
                "mi cel es",
                "mi celular es",
                "telefono es",
                "teléfono es",
                "celular es",
                "numero es",
                "claro es",
                "aqui esta",
                "te lo paso",
                "te la paso",
                "es este",
                "es esta",
                "seria",
            ]
        )

        if entities.dni and (explicit_auth_signal or awaiting_auth):
            auth_result = verify_customer_by_dni(entities.dni)
            if auth_result.ok:
                name = self._build_display_name_from_customer(auth_result.data)
                set_context_value("awaiting_auth", False)
                return (
                    f"Identidad verificada correctamente para {name}. "
                    "Ya puedes consultarme sobre tu pedido."
                )
            return "No pude verificar tu identidad con ese documento."

        if entities.phone and (explicit_auth_signal or awaiting_auth):
            auth_result = verify_customer_by_phone(entities.phone)
            if auth_result.ok:
                name = self._build_display_name_from_customer(auth_result.data)
                set_context_value("awaiting_auth", False)
                return (
                    f"Identidad verificada correctamente para {name}. "
                    "Ya puedes consultarme sobre tu pedido."
                )
            return "No pude verificar tu identidad con ese teléfono."

        return None

    def _handle_route(self, user_message: str, route, entities, trace_start_index: int) -> str:
        if not user_message:
            return (
                "Hola, soy el asistente de OmniRetail. "
                "Puedo ayudarte con políticas, productos y pedidos."
            )

        lowered = self._normalize_lookup_text(user_message)

        if route.intent == "faq_public":
            return self._handle_faq_public(user_message)

        if route.intent == "policy_question":
            return self._handle_policy_question(user_message)

        if route.intent == "product_price_stock":
            return self._handle_product_public(entities)

        if route.intent == "order_amount":
            return self._handle_order_amount(entities, trace_start_index)

        if route.intent == "warranty_check":
            return self._handle_warranty_request(entities, trace_start_index)

        if route.intent == "return_request":
            return self._handle_return_request(entities, trace_start_index)

        if route.intent in {"order_status_history", "policy_specific_order_case"}:
            return self._handle_order_status_sensitive(
                user_message,
                entities,
                trace_start_index,
            )

        # Short follow-up turns can rely on recent intent/context.
        last_intent = get_context_value("last_intent")
        if last_intent == "order_status_history" and any(
            token in lowered for token in ["tracking", "track", "trak", "guia", "gui", "envio", "transport"]
        ):
            return self._handle_order_status_sensitive(
                user_message,
                entities,
                trace_start_index,
            )

        if last_intent == "product_price_stock" and "stock" in lowered:
            return self._handle_product_public(entities)

        if self._looks_like_order_followup(lowered):
            return self._handle_order_status_sensitive(
                user_message,
                entities,
                trace_start_index,
            )

        if self._looks_like_order_overview_request(lowered):
            return self._handle_order_status_sensitive(
                user_message,
                entities,
                trace_start_index,
            )

        if self._looks_like_amount_followup(lowered):
            return self._handle_order_amount(entities, trace_start_index)

        if self._looks_like_list_orders_request(lowered):
            return self._handle_list_customer_orders()

        faq_response = build_public_faq_response(user_message)
        if faq_response:
            return faq_response

        return self._build_helpful_fallback()

    def _handle_faq_public(self, user_message: str) -> str:
        faq_response = build_public_faq_response(user_message)
        if faq_response:
            return faq_response

        return "Tu consulta parece ser pública y ya fue clasificada correctamente."

    def _handle_policy_question(self, user_message: str) -> str:
        policy_result = search_policy_sections(user_message)

        if not policy_result.ok:
            return "No encontré una sección de política suficientemente relevante para tu consulta."

        return build_policy_answer(policy_result.data)

    def _handle_product_public(self, entities) -> str:
        product_id = self._resolve_scoped_product_id(entities)

        if not product_id:
            return "Para consultar precio o stock, indícame el product_id del producto que quieres revisar."

        set_context_value("last_product_id", str(product_id))
        price_result = get_product_price(product_id)
        stock_result = get_product_stock(product_id)

        if not price_result.ok and not stock_result.ok:
            return f"No encontré información del producto {product_id}."

        parts: list[str] = [f"Producto consultado: {product_id}."]

        if price_result.ok:
            data = price_result.data
            parts.append(
                f"Nombre: {format_short_text(data.get('name'))}. "
                f"Precio: {format_currency_cop(data.get('price'))}. "
                f"Marca: {format_short_text(data.get('brand_name'))}. "
                f"Categoría: {format_short_text(data.get('category_name'))}."
            )

        if stock_result.ok:
            data = stock_result.data
            parts.append(
                f"Stock disponible: {format_value(data.get('available_qty'))}. "
                f"Ubicación: {format_short_text(data.get('warehouse_location'))}."
            )

        return " ".join(parts)

    def _handle_order_amount(self, entities, trace_start_index: int) -> str:
        auth_gate = self._ensure_authenticated()
        if auth_gate:
            return auth_gate

        customer = get_session_customer()
        customer_id = str(customer["customer_id"])

        order_id = self._resolve_order_id(entities)
        if not order_id:
            return self._ask_for_order_id(customer_id)

        ownership = order_belongs_to_customer(order_id, customer_id)
        if not ownership.ok:
            if ownership.error == "Pedido no encontrado":
                return f"No encontré el pedido {order_id}."
            return "No pude validar la pertenencia de ese pedido."

        if not ownership.data.get("belongs"):
            return "Ese pedido no pertenece al cliente autenticado."

        order_result = get_order_amounts(order_id)
        if not order_result.ok:
            return f"No encontré el pedido {order_id}."

        data = order_result.data
        if not has_required_tool_usage_since(
            trace_start_index,
            {"order_belongs_to_customer", "get_order_amounts"},
        ):
            return build_missing_tool_response()

        return (
            f"Pedido {format_value(data.get('order_id'))}: "
            f"subtotal {format_currency_cop(data.get('subtotal'))}, "
            f"envío {format_currency_cop(data.get('shipping_cost'))}, "
            f"IVA {format_currency_cop(data.get('tax'))}, "
            f"total {format_currency_cop(data.get('total_amount'))}."
        )

    def _handle_order_status_sensitive(
        self,
        user_message: str,
        entities,
        trace_start_index: int,
    ) -> str:
        auth_gate = self._ensure_authenticated()
        if auth_gate:
            return auth_gate

        customer = get_session_customer()
        customer_id = str(customer["customer_id"])

        order_id = self._resolve_order_id(entities)
        if not order_id:
            return self._ask_for_order_id(customer_id)

        ownership = order_belongs_to_customer(order_id, customer_id)
        if not ownership.ok:
            if ownership.error == "Pedido no encontrado":
                return f"No encontré el pedido {order_id}."
            return "No pude validar la pertenencia de ese pedido."

        if not ownership.data.get("belongs"):
            return "Ese pedido no pertenece al cliente autenticado."

        lowered = self._normalize_lookup_text(user_message)

        asks_status = any(
            token in lowered
            for token in [
                "donde",
                "onde",
                "estado",
                "que paso",
                "pasao",
                "en camino",
                "entregado",
                "cancelado",
            ]
        )
        asks_tracking = any(
            token in lowered
            for token in ["tracking", "track", "trak", "trakinn", "historial", "evento", "ruta", "movimiento"]
        )
        asks_shipping = any(
            token in lowered
            for token in ["guia", "transportadora", "envio", "entrega", "gui"]
        )

        if asks_tracking:
            return self._build_tracking_response(order_id, trace_start_index)

        if asks_shipping:
            return self._build_shipments_response(order_id, trace_start_index)

        if not asks_status:
            return self._build_order_overview_response(order_id)

        status_result = get_order_status(order_id)
        if not status_result.ok:
            return f"No encontré el pedido {order_id}."

        data = status_result.data
        if not has_required_tool_usage_since(
            trace_start_index,
            {"order_belongs_to_customer", "get_order_status"},
        ):
            return build_missing_tool_response()

        return (
            f"El pedido {format_value(data.get('order_id'))} tiene estado actual "
            f"'{format_status_label(data.get('status'))}'. "
            f"Método de entrega: {format_delivery_method(data.get('delivery_method'))}."
        )

    def _build_order_overview_response(self, order_id: str) -> str:
        status_result = get_order_status(order_id)
        amounts_result = get_order_amounts(order_id)
        shipments_result = get_order_shipments(order_id)
        tracking_result = get_order_tracking_history(order_id)
        items_result = list_order_items(order_id)

        if not status_result.ok:
            return f"No encontré el pedido {order_id}."

        status_data = status_result.data
        lines: list[str] = [f"Resumen del pedido {format_value(order_id)}"]

        if items_result.ok:
            items = items_result.data.get("items", [])
            if items:
                lines.append("")
                lines.append("Productos:")
                for item in items[:3]:
                    lines.append(
                        "- "
                        f"{item.get('product_id')}: {format_short_text(item.get('product_name'))} | "
                        f"cantidad {format_value(item.get('qty'))} | "
                        f"estado {format_status_label(item.get('item_status'))}"
                    )
                if len(items) > 3:
                    lines.append(f"- y {len(items) - 3} producto(s) más")

        lines.append("")
        lines.append("Estado:")
        lines.append(
            "- "
            f"actual: {format_status_label(status_data.get('status'))} | "
            f"método de entrega: {format_delivery_method(status_data.get('delivery_method'))}"
        )

        if shipments_result.ok:
            shipments = shipments_result.data.get("shipments", [])
            if shipments:
                shipment = shipments[0]
                lines.append("")
                lines.append("Envío:")
                lines.append(
                    "- "
                    f"transportadora: {format_short_text(shipment.get('carrier'))} | "
                    f"guía: {format_short_text(shipment.get('tracking_number'))} | "
                    f"estado logístico: {format_status_label(shipment.get('shipment_status'))}"
                )

        if tracking_result.ok:
            events = tracking_result.data.get("events", [])
            if events:
                last_event = events[-1]
                lines.append("")
                lines.append("Tracking:")
                lines.append(
                    "- "
                    f"{len(events)} evento(s) | "
                    f"último: {format_status_label(last_event.get('status'))} en "
                    f"{format_value(last_event.get('timestamp'))}"
                )

        if amounts_result.ok:
            data = amounts_result.data
            lines.append("")
            lines.append("Montos:")
            lines.append(
                "- "
                f"subtotal: {format_currency_cop(data.get('subtotal'))} | "
                f"envío: {format_currency_cop(data.get('shipping_cost'))} | "
                f"IVA: {format_currency_cop(data.get('tax'))} | "
                f"total: {format_currency_cop(data.get('total_amount'))}"
            )

        lines.append("")
        lines.append(
            "Si quieres, también puedo darte el detalle individual de guía, tracking, montos, garantía o devolución."
        )

        return "\n".join(lines)

    def _handle_warranty_request(self, entities, trace_start_index: int) -> str:
        auth_gate = self._ensure_authenticated()
        if auth_gate:
            return auth_gate

        customer = get_session_customer()
        customer_id = str(customer["customer_id"])
        order_id = self._resolve_order_id(entities)

        if not order_id:
            return self._ask_for_order_id(customer_id)

        ownership = order_belongs_to_customer(order_id, customer_id)
        if not ownership.ok:
            if ownership.error == "Pedido no encontrado":
                return f"No encontré el pedido {order_id}."
            return "No pude validar la pertenencia de ese pedido."

        if not ownership.data.get("belongs"):
            return "Ese pedido no pertenece al cliente autenticado."

        product_id = self._resolve_scoped_product_id(entities)

        if product_id:
            item_result = get_order_item_by_product(order_id, product_id)
            if not item_result.ok:
                return "No encontré ese producto dentro del pedido."

            item = item_result.data
            if not has_required_tool_usage_since(
                trace_start_index,
                {"get_order_item_by_product"},
            ):
                return build_missing_tool_response()

            return (
                f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                f"garantía hasta {format_value(item.get('warranty_expires_at'))}. "
                f"Estado del ítem: {format_status_label(item.get('item_status'))}."
            )

        items_result = list_order_items(order_id)
        if not items_result.ok:
            return f"No encontré ítems para el pedido {order_id}."

        items = items_result.data.get("items", [])
        if len(items) == 1:
            item = items[0]
            if not has_required_tool_usage_since(
                trace_start_index,
                {"list_order_items"},
            ):
                return build_missing_tool_response()

            set_context_value("last_product_id", str(item.get("product_id")))
            return (
                f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                f"garantía hasta {format_value(item.get('warranty_expires_at'))}. "
                f"Estado del ítem: {format_status_label(item.get('item_status'))}."
            )

        visible = [
            f"{item.get('product_id')} ({item.get('product_name')})"
            for item in items[:5]
        ]
        return (
            "Tu pedido tiene varios productos. "
            f"Indícame el product_id del que quieres revisar. Algunos productos encontrados: {', '.join(visible)}."
        )

    def _handle_return_request(self, entities, trace_start_index: int) -> str:
        auth_gate = self._ensure_authenticated()
        if auth_gate:
            return auth_gate

        customer = get_session_customer()
        customer_id = str(customer["customer_id"])
        order_id = self._resolve_order_id(entities)

        if not order_id:
            return self._ask_for_order_id(customer_id)

        ownership = order_belongs_to_customer(order_id, customer_id)
        if not ownership.ok:
            if ownership.error == "Pedido no encontrado":
                return f"No encontré el pedido {order_id}."
            return "No pude validar la pertenencia de ese pedido."

        if not ownership.data.get("belongs"):
            return "Ese pedido no pertenece al cliente autenticado."

        product_id = self._resolve_scoped_product_id(entities)

        if product_id:
            item_result = get_order_item_by_product(order_id, product_id)
            if not item_result.ok:
                return "No encontré ese producto dentro del pedido."

            item = item_result.data
            if not has_required_tool_usage_since(
                trace_start_index,
                {"get_order_item_by_product"},
            ):
                return build_missing_tool_response()

            if item.get("is_final_sale") or item.get("return_days") == 0:
                return (
                    f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                    "no tiene derecho a devolución porque es venta final o tiene 0 días de devolución."
                )

            return (
                f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                f"fecha límite de devolución {format_value(item.get('return_deadline'))}. "
                f"Estado del ítem: {format_status_label(item.get('item_status'))}."
            )

        items_result = list_order_items(order_id)
        if not items_result.ok:
            return f"No encontré ítems para el pedido {order_id}."

        items = items_result.data.get("items", [])
        if len(items) == 1:
            item = items[0]
            if not has_required_tool_usage_since(
                trace_start_index,
                {"list_order_items"},
            ):
                return build_missing_tool_response()

            set_context_value("last_product_id", str(item.get("product_id")))
            if item.get("is_final_sale") or item.get("return_days") == 0:
                return (
                    f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                    "no tiene derecho a devolución porque es venta final o tiene 0 días de devolución."
                )

            return (
                f"Producto {format_short_text(item.get('product_name'))} del pedido {format_value(order_id)}: "
                f"fecha límite de devolución {format_value(item.get('return_deadline'))}. "
                f"Estado del ítem: {format_status_label(item.get('item_status'))}."
            )

        visible = [
            f"{item.get('product_id')} ({item.get('product_name')})"
            for item in items[:5]
        ]
        return (
            "Tu pedido tiene varios productos. "
            f"Indícame el product_id del que quieres revisar. Algunos productos encontrados: {', '.join(visible)}."
        )

    def _build_tracking_response(self, order_id: str, trace_start_index: int) -> str:
        tracking_result = get_order_tracking_history(order_id)
        if not tracking_result.ok:
            return f"No encontré historial de tracking para el pedido {order_id}."

        events = tracking_result.data.get("events", [])
        if not events:
            return f"No encontré historial de tracking para el pedido {order_id}."

        first_event = events[0]
        last_event = events[-1]
        if not has_required_tool_usage_since(
            trace_start_index,
            {"get_order_tracking_history"},
        ):
            return build_missing_tool_response()

        return (
            f"Encontré {len(events)} eventos de tracking para el pedido {format_value(order_id)}. "
            f"Primer evento: {format_status_label(first_event.get('status'))} en {format_value(first_event.get('timestamp'))}. "
            f"Último evento: {format_status_label(last_event.get('status'))} en {format_value(last_event.get('timestamp'))}."
        )

    def _build_shipments_response(self, order_id: str, trace_start_index: int) -> str:
        shipments_result = get_order_shipments(order_id)
        if not shipments_result.ok:
            return f"No encontré información de envío para el pedido {order_id}."

        shipments = shipments_result.data.get("shipments", [])
        if not shipments:
            return f"No encontré información de envío para el pedido {order_id}."

        first_shipment = shipments[0]
        if not has_required_tool_usage_since(
            trace_start_index,
            {"get_order_shipments"},
        ):
            return build_missing_tool_response()

        return (
            f"Pedido {format_value(order_id)}: "
            f"transportadora {format_short_text(first_shipment.get('carrier'))}, "
            f"guía {format_short_text(first_shipment.get('tracking_number'))}, "
            f"estado logístico {format_status_label(first_shipment.get('shipment_status'))}, "
            f"entrega estimada {format_value(first_shipment.get('estimated_delivery_date'))}."
        )

    def _ensure_authenticated(self) -> str | None:
        if not has_verified_customer():
            set_context_value("awaiting_auth", True)
            return self._build_auth_prompt()
        return None

    def _handle_list_customer_orders(self) -> str:
        auth_gate = self._ensure_authenticated()
        if auth_gate:
            return auth_gate

        customer = get_session_customer()
        customer_id = str(customer["customer_id"])
        orders_result = list_customer_orders(customer_id)

        if not orders_result.ok:
            return "Tu identidad ya fue verificada, pero no encontré pedidos asociados."

        orders = orders_result.data.get("orders", [])
        if not orders:
            return "Tu identidad ya fue verificada, pero no encontré pedidos asociados."

        visible_orders = []
        for order in orders[:5]:
            order_id = order.get("order_id")
            status = format_status_label(order.get("status"))
            visible_orders.append(f"{order_id} ({status})")

        if len(orders) == 1:
            only_order = orders[0]
            order_id = str(only_order.get("order_id"))
            set_context_value("last_order_id", order_id)
            return (
                f"Tienes 1 pedido asociado: {order_id} "
                f"con estado {format_status_label(only_order.get('status'))}."
            )

        return (
            f"Encontré {len(orders)} pedidos asociados a tu cuenta. "
            f"Algunos son: {', '.join(visible_orders)}. "
            "Si quieres, dime cuál pedido deseas revisar."
        )

    def _ask_for_order_id(self, customer_id: str) -> str:
        orders_result = list_customer_orders(customer_id)

        if not orders_result.ok:
            return "Tu identidad ya fue verificada, pero no encontré pedidos asociados."

        orders = orders_result.data.get("orders", [])
        if len(orders) == 1:
            only_order = orders[0]
            return (
                f"Tu identidad ya fue verificada. Veo un pedido asociado: {only_order.get('order_id')}. "
                "Escríbeme nuevamente incluyendo ese número de pedido para continuar."
            )

        visible_orders = [str(order.get("order_id")) for order in orders[:5]]
        return (
            "Tu identidad ya fue verificada. "
            f"Indícame cuál pedido deseas consultar. Algunos pedidos encontrados: {', '.join(visible_orders)}."
        )

    def _resolve_order_id(self, entities) -> str | None:
        order_id = entities.order_id or get_context_value("last_order_id")
        if order_id:
            return order_id

        customer = get_session_customer()
        if not customer:
            return None

        customer_id = str(customer["customer_id"])
        orders_result = list_customer_orders(customer_id)
        if not orders_result.ok:
            return None

        orders = orders_result.data.get("orders", [])
        if len(orders) == 1:
            inferred_order_id = str(orders[0].get("order_id"))
            set_context_value("last_order_id", inferred_order_id)
            return inferred_order_id

        return None

    def _resolve_product_id(self, entities) -> str | None:
        return entities.product_id or get_context_value("last_product_id")

    def _resolve_scoped_product_id(self, entities) -> str | None:
        if entities.product_id:
            return entities.product_id

        # If the user explicitly provided a new order_id but not a product_id,
        # do not reuse a stale product from a previous unrelated turn.
        if entities.order_id:
            return None

        return get_context_value("last_product_id")

    def _build_display_name_from_customer(self, data: dict[str, Any]) -> str:
        return " ".join(
            part.strip()
            for part in [
                str(data.get("name", "") or ""),
                str(data.get("last_name1", "") or ""),
                str(data.get("last_name2", "") or ""),
            ]
            if part and part.strip()
        ).strip() or f"Cliente {data.get('customer_id')}"

    def _normalize_lookup_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", (text or "").strip().lower())
        return "".join(char for char in normalized if not unicodedata.combining(char))

    def _looks_like_order_followup(self, lowered: str) -> bool:
        if not (get_context_value("last_order_id") or has_verified_customer()):
            return False
        return any(
            token in lowered
            for token in [
                "y la guia",
                "y el tracking",
                "tracking",
                "track",
                "trak",
                "trakinn",
                "guia",
                "guia de ese",
                "y la guia de ese",
                "de ese pedido",
                "de una",
            ]
        )

    def _looks_like_order_overview_request(self, lowered: str) -> bool:
        return any(
            token in lowered
            for token in [
                "informacion del pedido",
                "informacion de mi pedido",
                "informacion sobre el pedido",
                "detalle del pedido",
                "detalle de mi pedido",
                "resumen del pedido",
                "resumen de mi pedido",
                "quiero saber del pedido",
                "dame info del pedido",
                "ver pedido",
                "revisar pedido",
                "mostrar pedido",
            ]
        )

    def _looks_like_amount_followup(self, lowered: str) -> bool:
        if not (get_context_value("last_order_id") or has_verified_customer()):
            return False
        return any(
            token in lowered
            for token in [
                "cuanto pague",
                "cuanto page",
                "cuanto pag",
                "iva",
                "subtotal",
                "total",
                "por ese",
                "ese pedido",
            ]
        )

    def _looks_like_list_orders_request(self, lowered: str) -> bool:
        return any(
            token in lowered
            for token in [
                "que pedidos tengo",
                "cuales son mis pedidos",
                "cuales pedidos tengo",
                "cuales son mis compras",
                "que compras tengo",
                "mis pedidos",
                "mis compras",
                "quiero ver mis pedidos",
                "muestrame mis pedidos",
                "mostrar mis pedidos",
                "ver mis pedidos",
                "listame mis pedidos",
                "listar mis pedidos",
                "quiero saber que pedidos tengo",
                "mostrarme mis compras",
            ]
        )

    def _build_auth_prompt(self) -> str:
        return (
            "Para ayudarte con informacion sensible de pedidos, primero debo verificar tu identidad. "
            "Por favor comparte tu numero de documento o tu telefono registrado."
        )

    def _build_helpful_fallback(self) -> str:
        return (
            "No entendí del todo tu mensaje, pero puedo ayudarte con estas consultas:\n"
            "- estado, guía o tracking de un pedido\n"
            "- total, IVA o monto pagado\n"
            "- precio y stock de un producto\n"
            "- garantías y devoluciones\n"
            "- políticas de envío, garantía o devolución\n"
            "Ejemplos:\n"
            "- Dónde está mi pedido 303\n"
            "- Cuál es el precio del producto 5001\n"
            "- Puedo devolver un producto en promoción"
        )


def create_agent(streaming: bool = False) -> OmniRetailAgent:
    return OmniRetailAgent(streaming=streaming)
