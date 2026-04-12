# Agent OmniRetail

Asistente conversacional para soporte de e-commerce, orientado a responder consultas de clientes con datos locales, politicas documentales y reglas de seguridad explicitas.

El proyecto fue construido como base funcional para un reto tecnico de agentes: prioriza control de acceso, uso auditable de herramientas, recuperacion documental y separacion clara entre consultas publicas y sensibles.

## Que hace este agente

El agente puede:

- responder FAQs publicas
- recuperar respuestas desde documentos de politicas
- consultar productos, precio y stock
- responder montos de pedidos
- informar estado, tracking y envios
- validar garantia y devoluciones por pedido y producto
- exigir autenticacion antes de exponer datos sensibles
- bloquear intentos basicos de prompt injection

## Que tipo de asistente es

Este no es un chatbot social general. Esta orientado a atencion al cliente para e-commerce.

Eso significa que funciona mejor cuando el usuario consulta temas como:

- pedidos
- envios
- tracking
- garantias
- devoluciones
- politicas
- productos
- precios y stock

## Arquitectura general

### Core

- `core/agent.py`: orquestacion principal del agente.
- `core/router.py`: clasificacion de intencion.
- `core/entity_extractor.py`: extraccion de `dni`, `phone`, `order_id` y `product_id`.
- `core/session_context.py`: memoria conversacional, sesion autenticada y trazabilidad.
- `core/guards.py`: validaciones de seguridad.
- `core/anti_hallucination.py`: control de uso real de tools antes de responder.
- `core/policy_loader.py`: carga y segmentacion de politicas.
- `core/policy_response_builder.py`: construccion de respuestas documentales.
- `core/faq_responses.py`: respuestas rapidas para consultas publicas.
- `core/db.py`: conexion local a DuckDB.

### Tools

- `tools/auth_tools.py`: autenticacion por documento o telefono.
- `tools/order_tools.py`: montos, estado, tracking y envios.
- `tools/order_item_tools.py`: garantia y devoluciones por item.
- `tools/product_tools.py`: precio y stock de productos.
- `tools/policy_tools.py`: busqueda sobre documentos Markdown.
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
- `duckdb`
- `pydantic`
- `python-dotenv`

Para desarrollo y pruebas:

- `pytest`

## Instalacion local

Desde la raiz del proyecto:

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
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

### Politicas

Los documentos deben estar en `data/policies/`:

- `Politica de devoluciones.md`
- `Politica de garantia.md`
- `Politicas de envio.md`

## Uso rapido

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

Ese script incluye comandos utiles:

- `/help`
- `/examples`
- `/reset`
- `/exit`

### Prueba integral manual

```bash
python tests/test_full_flow_manual.py
```

### Prueba minima de contrato

```bash
python tests/test_create_agent_manual.py
```

## Como empezar una conversacion

El agente entiende mejor mensajes orientados a tarea, pero tambien puede arrancar con saludos o aperturas simples.

Ejemplos validos:

- `Hola`
- `Buenas`
- `Buenos dias`
- `Hola, necesito ayuda`
- `Quiero hacer una consulta`
- `Me puedes ayudar con un pedido`
- `Quiero informacion sobre un producto`

Despues de eso, las consultas mas naturales para el agente son:

- `Donde esta mi pedido 303`
- `Mi documento es 1181165722`
- `Y la guia`
- `Y el tracking`
- `Cuanto pague en ese pedido`
- `Cual es el precio del producto 5001`
- `Y el stock`
- `Puedo devolver el producto del pedido 303`

## Flujo esperado

### 1. Consulta publica

No requiere autenticacion.

Ejemplos:

- metodos de pago
- cobertura de envios
- atencion por WhatsApp
- precio y stock
- politicas generales

### 2. Consulta sensible

Si requiere autenticacion.

Ejemplos:

- estado del pedido
- tracking
- guia
- montos
- garantia de una compra
- devolucion de un producto comprado

### 3. Autenticacion

El agente acepta autenticacion por:

- documento
- telefono registrado

Una vez autenticado, puede reutilizar parte del contexto reciente para follow-ups cortos, siempre sin saltarse ownership ni controles de acceso.

## Contrato tecnico importante

El proyecto cumple con la base esperada por el reto:

- existe `core/agent.py`
- existe `core/session_context.py`
- `create_agent(streaming=False)` retorna un agente funcional
- el agente es invocable como `agent("texto")`
- la respuesta expone `.content` o funciona con `str(response)`
- se registra trazabilidad de tools
- se registra la sesion del cliente autenticado

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

- buena separacion entre consultas publicas y sensibles
- autenticacion obligatoria para pedidos
- trazabilidad de tool use
- recuperacion de politicas desde documentos
- memoria conversacional basica
- proteccion contra respuestas sensibles inventadas

## Limitaciones actuales

- todavia no es un chatbot social general
- el lenguaje muy coloquial o con errores extremos puede afectar el routing
- algunos follow-ups cortos siguen siendo sensibles al contexto previo
- la experiencia conversacional esta solida para demo tecnica, pero aun puede pulirse para uso real

## Documentacion adicional

- `docs/challenge_contract.md`
- `docs/data_model.md`
- `docs/final_checklist.md`
- `docs/routing_rules.md`

## Nota

El proyecto usa DuckDB en local para validacion y prototipado antes de una posible migracion a AWS.
