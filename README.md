# Agent OmniRetail

Asistente conversacional para soporte de e-commerce, diseñado para responder consultas de clientes con reglas de seguridad explícitas, uso auditable de herramientas, recuperación documental y memoria conversacional útil.

El proyecto funciona en dos modos:

- **Local**, para desarrollo, pruebas y validación del flujo.
- **AWS**, para exponer el agente mediante API y persistir datos de sesión.

## Alcance del agente

El agente puede atender:

- FAQs públicas
- políticas de devolución, garantía y envío
- precio y stock de productos
- montos de pedidos
- estado, tracking y guía
- garantía y devoluciones por pedido y producto

También puede:

- exigir autenticación antes de exponer datos sensibles
- validar ownership de pedidos
- bloquear intentos básicos de prompt injection
- mantener memoria útil entre turnos

## Casos de uso principales

Ejemplos de consultas públicas:

- `¿Qué métodos de pago manejan?`
- `¿Hacen envíos a zonas rurales?`
- `¿Cuál es el precio del producto 5001?`
- `¿Puedo devolver un producto en promoción?`

Ejemplos de consultas sensibles:

- `¿Dónde está mi pedido?`
- `¿Cuál es la guía del pedido 28?`
- `¿Cuánto pagué en mi pedido?`
- `¿Mi producto del pedido 28 aún tiene garantía?`

Ejemplos de autenticación:

- `Mi documento es 878545512`
- `Mi teléfono es 3161809190`

## Arquitectura actual

### Núcleo de aplicación

- [core/agent.py](c:\Users\user\Desktop\agent-omniretail\core\agent.py): orquestación principal del agente
- [core/router.py](c:\Users\user\Desktop\agent-omniretail\core\router.py): clasificación de intención
- [core/entity_extractor.py](c:\Users\user\Desktop\agent-omniretail\core\entity_extractor.py): extracción de `dni`, `phone`, `order_id` y `product_id`
- [core/session_context.py](c:\Users\user\Desktop\agent-omniretail\core\session_context.py): memoria conversacional y snapshot de sesión
- [core/session_store.py](c:\Users\user\Desktop\agent-omniretail\core\session_store.py): persistencia de sesión en DynamoDB
- [core/db.py](c:\Users\user\Desktop\agent-omniretail\core\db.py): acceso a datos tabulares con DuckDB
- [core/policy_loader.py](c:\Users\user\Desktop\agent-omniretail\core\policy_loader.py): carga y segmentación de políticas
- [core/s3_sync.py](c:\Users\user\Desktop\agent-omniretail\core\s3_sync.py): sincronización de CSV y Markdown desde S3
- [core/guards.py](c:\Users\user\Desktop\agent-omniretail\core\guards.py): reglas de seguridad
- [core/anti_hallucination.py](c:\Users\user\Desktop\agent-omniretail\core\anti_hallucination.py): verificación de uso real de tools antes de responder

### Tools

- [tools/auth_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\auth_tools.py)
- [tools/customer_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\customer_tools.py)
- [tools/order_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\order_tools.py)
- [tools/order_item_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\order_item_tools.py)
- [tools/product_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\product_tools.py)
- [tools/policy_tools.py](c:\Users\user\Desktop\agent-omniretail\tools\policy_tools.py)

## Arquitectura AWS

La versión desplegada en AWS usa esta arquitectura:

- **API Gateway**: expone el endpoint HTTP del agente
- **AWS Lambda**: ejecuta el handler del agente
- **S3**: almacena CSV y documentos de políticas
- **DynamoDB**: guarda la sesión por `session_id`
- **CloudWatch**: logs y observabilidad básica

### Flujo de ejecución en AWS

1. El cliente envía `message` y `session_id` al endpoint.
2. API Gateway invoca la Lambda.
3. Lambda rehidrata la sesión desde DynamoDB.
4. Si hace falta, descarga datasets y políticas desde S3 a caché temporal.
5. El agente procesa la consulta.
6. Lambda persiste el nuevo snapshot de sesión en DynamoDB.
7. La respuesta vuelve al cliente en JSON UTF-8.

## Estructura del proyecto

```text
agent-omniretail/
  app/
  core/
  tools/
  data/
    raw/
    policies/
  docs/
  tests/
  template.yaml
  Makefile
  requirements.txt
  requirements-dev.txt
  README.md
```

## Requisitos

- Python 3.11
- Docker Desktop
- AWS CLI
- AWS SAM CLI

Dependencias de runtime:

- `boto3`
- `duckdb`
- `pydantic`
- `python-dotenv`

Dependencias de desarrollo:

- `pytest`

## Instalación local

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Configuración de entorno

Archivo de ejemplo:

- [`.env.example`](c:\Users\user\Desktop\agent-omniretail\.env.example)

Variables principales:

- `APP_ENV=local|aws`
- `AWS_REGION`
- `DATA_BUCKET`
- `SESSIONS_TABLE`
- `BEDROCK_MODEL_ID`

Ejemplo típico para modo AWS:

```env
APP_ENV=aws
AWS_REGION=us-east-1
DATA_BUCKET=agent-omniretail-data-123456789012
SESSIONS_TABLE=agent-omniretail-sessions
BEDROCK_MODEL_ID=
```

## Datos esperados

### CSV

Deben existir estos archivos en `data/raw/` o en `s3://<bucket>/raw/`:

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

Deben existir estos archivos en `data/policies/` o en `s3://<bucket>/policies/`:

- `Política de devoluciones.md`
- `Política de garantía.md`
- `Políticas de envío.md`

## Uso local

### Crear el agente

```python
from core.agent import create_agent

agent = create_agent()
response = agent("Hola")

print(response.content)
print(str(response))
```

### Chat manual

```powershell
python tests/test_chat_manual.py
```

### Pruebas manuales recomendadas

```powershell
python tests/test_create_agent_manual.py
python tests/test_tools_manual.py
python tests/test_router_entities_manual.py
python tests/test_faq_manual.py
python tests/test_policy_answer_manual.py
python tests/test_guards_manual.py
python tests/test_full_flow_manual.py
```

## Despliegue en AWS

### 1. Configurar credenciales

```powershell
aws configure
aws sts get-caller-identity
```

### 2. Construir

```powershell
sam build --use-container
```

### 3. Desplegar

Primer despliegue:

```powershell
sam deploy --guided
```

Siguientes despliegues:

```powershell
sam deploy
```

## Recursos AWS esperados

La plantilla [template.yaml](c:\Users\user\Desktop\agent-omniretail\template.yaml) crea:

- una función Lambda
- un endpoint API Gateway `POST /chat`
- una tabla DynamoDB para sesión

La Lambda recibe estas variables:

- `APP_ENV=aws`
- `DATA_BUCKET=<bucket>`
- `SESSIONS_TABLE=agent-omniretail-sessions`

## Prueba del endpoint AWS

Ejemplo:

```powershell
Invoke-RestMethod -Method Post -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/Prod/chat" `
  -ContentType "application/json" `
  -Body '{"message":"¿Cuál es el precio del producto 5001?","session_id":"demo-1"}'
```

Ejemplo de flujo autenticado:

```powershell
Invoke-RestMethod -Method Post -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/Prod/chat" `
  -ContentType "application/json" `
  -Body '{"message":"Mi documento es 878545512","session_id":"demo-2"}'

Invoke-RestMethod -Method Post -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/Prod/chat" `
  -ContentType "application/json" `
  -Body '{"message":"Quiero saber del pedido 28","session_id":"demo-2"}'

Invoke-RestMethod -Method Post -Uri "https://<api-id>.execute-api.<region>.amazonaws.com/Prod/chat" `
  -ContentType "application/json" `
  -Body '{"message":"¿y la guía?","session_id":"demo-2"}'
```

## Seguridad y control

El agente aplica:

- autenticación obligatoria para consultas sensibles
- validación de ownership antes de exponer pedidos
- trazabilidad de tools
- protección anti-hallucination para respuestas sensibles
- bloqueo básico de prompt injection

## Estado actual del proyecto

### Ya funcionando

- flujo local completo
- despliegue en AWS con SAM
- lectura de CSV desde S3
- lectura de políticas desde S3
- sesión persistente en DynamoDB
- memoria útil entre turnos en AWS
- respuestas UTF-8 correctas en el endpoint

### Pendientes razonables

- integrar Bedrock si se quiere una capa LLM explícita en AWS
- seguir refinando algunos follow-ups ambiguos
- mejorar aún más el ranking de políticas
- separar aún más el runtime del material de prueba si se busca endurecer producción

## Fortalezas

- arquitectura clara para demo técnica
- buen balance entre reglas, datos y seguridad
- fácil de explicar ante evaluación
- costos contenidos para MVP
- flujo sensible ya soportado en AWS

## Limitaciones

- no es un chatbot generalista
- algunos mensajes muy ambiguos siguen requiriendo más contexto
- todavía usa DuckDB como capa tabular del MVP
- la integración Bedrock no está activada en el flujo actual

## Documentación adicional

- [docs/challenge_contract.md](c:\Users\user\Desktop\agent-omniretail\docs\challenge_contract.md)
- [docs/data_model.md](c:\Users\user\Desktop\agent-omniretail\docs\data_model.md)
- [docs/final_checklist.md](c:\Users\user\Desktop\agent-omniretail\docs\final_checklist.md)
- [docs/routing_rules.md](c:\Users\user\Desktop\agent-omniretail\docs\routing_rules.md)

## Nota final

Este proyecto ya quedó listo como MVP técnico desplegado en AWS, con separación entre consultas públicas y sensibles, persistencia de sesión y soporte documental real. La siguiente evolución natural sería decidir si conviene mantener la lógica mayoritariamente determinística o incorporar Bedrock de forma controlada y con criterio de costo.
