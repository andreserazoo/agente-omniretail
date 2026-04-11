# Agent OmniRetail

Asistente conversacional para soporte de e-commerce, orientado a responder consultas de clientes con datos locales, políticas documentales y reglas de seguridad explícitas.

El proyecto fue construido como base funcional para un reto técnico de agentes: prioriza control de acceso, uso auditable de herramientas, recuperación documental y separación clara entre consultas públicas y sensibles.

## Qué hace este agente

El agente puede:

- responder FAQs públicas
- recuperar respuestas desde documentos de políticas
- consultar productos, precio y stock
- responder montos de pedidos
- informar estado, tracking y envíos
- validar garantía y devoluciones por pedido y producto
- exigir autenticación antes de exponer datos sensibles
- bloquear intentos básicos de prompt injection

## Qué tipo de asistente es

Este no es un chatbot social general. Está orientado a atención al cliente para e-commerce.

Eso significa que funciona mejor cuando el usuario consulta temas como:

- pedidos
- envíos
- tracking
- garantías
- devoluciones
- políticas
- productos
- precios y stock

## Arquitectura general

### Core

- `core/agent.py`: orquestación principal del agente.
- `core/router.py`: clasificación de intención.
- `core/entity_extractor.py`: extracción de `dni`, `phone`, `order_id` y `product_id`.
- `core/session_context.py`: memoria conversacional, sesión autenticada y trazabilidad.
- `core/guards.py`: validaciones de seguridad.
- `core/anti_hallucination.py`: control de uso real de tools antes de responder.
- `core/policy_loader.py`: carga y segmentación de políticas.
- `core/policy_response_builder.py`: construcción de respuestas documentales.
- `core/faq_responses.py`: respuestas rápidas para consultas públicas.
- `core/db.py`: conexión local a DuckDB.

### Tools

- `tools/auth_tools.py`: autenticación por documento o teléfono.
- `tools/order_tools.py`: montos, estado, tracking y envíos.
- `tools/order_item_tools.py`: garantía y devoluciones por ítem.
- `tools/product_tools.py`: precio y stock de productos.
- `tools/policy_tools.py`: búsqueda sobre documentos Markdown.
- `tools/query_helpers.py`: helpers de consulta sobre DuckDB.

## Estructura del proyecto

```text
agent-omniretail/
  core/
  tools/
  data/
    raw/
    policies/
  docs/
  tests/
  config/
  README.md
```

## Requisitos

- Python 3.11+
- DuckDB

Dependencias principales:

- `boto3`
- `pytest`
- `duckdb`
- `pydantic`
- `python-dotenv`

## Instalación local

Desde la raíz del proyecto:

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Datos esperados

### CSV

Los archivos tabulares deben estar en `data/raw/`:

- `customers.csv`
- `customer_emails.csv`
- `addresses.csv`
- `cards.csv`
- `categories.csv`
- `brands.csv`
- `products.csv`
- `stock.csv`
- `promotions.csv`
- `orders.csv`
- `order_items.csv`
- `shipments.csv`
- `tracking.csv`

### Políticas

Los documentos deben estar en `data/policies/`:

- `Política de devoluciones.md`
- `Política de garantía.md`
- `Políticas de envío.md`

## Uso rápido

### Crear el agente

```python
from core.agent import create_agent

agent = create_agent()
response = agent("Hola")

print(response.content)
print(str(response))
```

### Script interactivo manual

Para probar el agente desde consola:

```bash
python tests/test_chat_manual.py
```

Ese script incluye comandos útiles:

- `/help`
- `/examples`
- `/reset`
- `/exit`

### Prueba integral manual

```bash
python tests/test_full_flow_manual.py
```

### Prueba mínima de contrato

```bash
python tests/test_create_agent_manual.py
```

## Cómo empezar una conversación

El agente entiende mejor mensajes orientados a tarea, pero también puede arrancar con saludos o aperturas simples.

Ejemplos válidos:

- `Hola`
- `Buenas`
- `Buenos dias`
- `Hola, necesito ayuda`
- `Quiero hacer una consulta`
- `Me puedes ayudar con un pedido`
- `Quiero informacion sobre un producto`

Después de eso, las consultas más naturales para el agente son:

- `¿Dónde está mi pedido 303?`
- `Mi documento es 1181165722`
- `¿Y la guía?`
- `¿Y el tracking?`
- `¿Cuánto pagué en ese pedido?`
- `¿Cuál es el precio del producto 5001?`
- `¿Y el stock?`
- `¿Puedo devolver el producto del pedido 303?`

## Flujo esperado

### 1. Consulta pública

No requiere autenticación.

Ejemplos:

- métodos de pago
- cobertura de envíos
- atención por WhatsApp
- precio y stock
- políticas generales

### 2. Consulta sensible

Sí requiere autenticación.

Ejemplos:

- estado del pedido
- tracking
- guía
- montos
- garantía de una compra
- devolución de un producto comprado

### 3. Autenticación

El agente acepta autenticación por:

- documento
- teléfono registrado

Una vez autenticado, puede reutilizar parte del contexto reciente para follow-ups cortos, siempre sin saltarse ownership ni controles de acceso.

## Contrato técnico importante

El proyecto cumple con la base esperada por el reto:

- existe `core/agent.py`
- existe `core/session_context.py`
- `create_agent(streaming=False)` retorna un agente funcional
- el agente es invocable como `agent("texto")`
- la respuesta expone `.content` o funciona con `str(response)`
- se registra trazabilidad de tools
- se registra la sesión del cliente autenticado

## Pruebas recomendadas

Pruebas principales:

- `python tests/test_create_agent_manual.py`
- `python tests/test_tools_manual.py`
- `python tests/test_router_entities_manual.py`
- `python tests/test_faq_manual.py`
- `python tests/test_policy_answer_manual.py`
- `python tests/test_guards_manual.py`
- `python tests/test_full_flow_manual.py`

Pruebas adicionales:

- `python tests/test_chat_manual.py`
- `python tests/test_memory_manual.py`
- `python tests/test_edge_cases_manual.py`
- `pytest -q`

## Fortalezas actuales

- buena separación entre consultas públicas y sensibles
- autenticación obligatoria para pedidos
- trazabilidad de tool use
- recuperación de políticas desde documentos
- memoria conversacional básica
- protección contra respuestas sensibles inventadas

## Limitaciones actuales

- todavía no es un chatbot social general
- el lenguaje muy coloquial o con errores extremos puede afectar el routing
- algunos follow-ups cortos siguen siendo sensibles al contexto previo
- la experiencia conversacional está sólida para demo técnica, pero aún puede pulirse para uso real

## Documentación adicional

- `docs/challenge_contract.md`
- `docs/data_model.md`
- `docs/final_checklist.md`
- `docs/routing_rules.md`

## Nota

El proyecto usa DuckDB en local para validación y prototipado antes de una posible migración a AWS.
