# Final Checklist - Agent OmniRetail

## 1. Estructura obligatoria
- [ ] Existe `core/agent.py`
- [ ] Existe `core/session_context.py`
- [ ] `create_agent(streaming=False)` funciona
- [ ] `create_agent()` no lanza excepción al inicializar
- [ ] El agente es invocable como `agent("texto")`
- [ ] La respuesta nunca es `None`
- [ ] La respuesta soporta `str(response)` o `.content`

## 2. Session context y auditoría
- [ ] Existe `add_tool_trace()`
- [ ] Existe `set_session_customer()`
- [ ] Existe `reset_session()`
- [ ] Existe `get_tool_trace()`
- [ ] Existe `get_tool_trace_length()`
- [ ] Existe `get_tool_trace_since(index)`
- [ ] La traza se registra cuando se usan tools
- [ ] La sesión del cliente se registra al autenticar

## 3. Routing
- [ ] FAQ pública funciona
- [ ] Consulta de políticas funciona
- [ ] Precio/stock general funciona
- [ ] Montos de pedido requieren autenticación
- [ ] Estado/historial requieren autenticación
- [ ] Garantía específica funciona
- [ ] Devolución específica funciona

## 4. Seguridad
- [ ] No responde pedidos sin autenticación
- [ ] No autentica con nombre o email
- [ ] Bloquea intentos de prompt injection
- [ ] Bloquea acceso a pedidos ajenos
- [ ] Diferencia entre pedido inexistente y pedido ajeno

## 5. Anti-alucinación
- [ ] No responde montos sin tool-use
- [ ] No responde estado sin tool-use
- [ ] No responde tracking sin tool-use
- [ ] No responde garantía específica sin tool-use
- [ ] No responde devolución específica sin tool-use

## 6. Memoria
- [ ] Recuerda `last_order_id`
- [ ] Recuerda `last_product_id`
- [ ] No rompe autenticación por recordar contexto

## 7. Datos
- [ ] Los CSV están en `data/raw/`
- [ ] Las políticas están en `data/policies/`
- [ ] DuckDB carga correctamente
- [ ] Las tools consultan los datos reales

## 8. Antes del ZIP final
- [ ] Ejecutar pruebas manuales principales
- [ ] Revisar imports
- [ ] Revisar rutas relativas
- [ ] Verificar que no haya archivos temporales innecesarios
- [ ] Confirmar que el proyecto corre desde cero