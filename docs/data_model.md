# Data Model - Agent OmniRetail

## 1. Objetivo

Documentar el esquema real de datos del proyecto para diseñar correctamente:

- autenticación
- consultas de catálogo
- consultas de stock
- consultas de promociones
- consultas de montos de pedido
- consultas de estado e historial
- validación de devoluciones
- validación de garantía

Este documento se basa en los archivos CSV reales del dataset del proyecto.

---

## 2. Tablas disponibles

### Clientes y contacto
- `customers.csv`
- `customer_emails.csv`
- `addresses.csv`
- `cards.csv`

### Catálogo
- `categories.csv`
- `brands.csv`
- `products.csv`
- `stock.csv`
- `promotions.csv`

### Pedidos y logística
- `orders.csv`
- `order_items.csv`
- `shipments.csv`
- `tracking.csv`

---

## 3. Reglas generales importantes

### Autenticación
Los únicos campos válidos para verificar identidad del cliente son:
- `dni`
- `phone`

No se debe autenticar con:
- `name`
- `last_name1`
- `last_name2`
- `email`

### Datos sensibles
Se consideran sensibles, entre otros:
- montos de un pedido específico
- estado de un pedido específico
- historial de tracking
- información logística específica
- dirección de entrega de un pedido
- garantía específica de una compra
- devolución específica de una compra

### Regla de dirección
La dirección de entrega solo debe usarse si el pedido tiene:
- `delivery_method = home_delivery`

Si el pedido tiene:
- `delivery_method = pickup_point`

no debe tratarse como entrega a domicilio.

### Regla de vigencias
Para casos específicos de compras reales, las fuentes prioritarias son:
- `warranty_expires_at`
- `return_deadline`

Estas están en `order_items.csv`.

### Regla de estado
- `orders.status` = estado actual resumido del pedido
- `tracking` = historial detallado de eventos

No se deben confundir.

---

## 4. Tabla `customers`

### Propósito
Datos maestros del cliente.

### Clave principal
- `customer_id`

### Columnas reales
- `customer_id`
- `tipo_id`
- `dni`
- `name`
- `last_name1`
- `last_name2`
- `birthday`
- `phone`
- `registration_date`
- `account_status`
- `is_premium`

### Usos principales
- autenticación por `dni`
- autenticación por `phone`
- obtener nombre visible del cliente
- consultar estado de cuenta del cliente
- identificar si es premium

### Observaciones
- la autenticación no debe depender del nombre
- los apellidos están separados en dos columnas
- `tipo_id` indica tipo de documento

---

## 5. Tabla `customer_emails`

### Propósito
Correos asociados al cliente.

### Clave principal
- `email_id`

### Relación principal
- `customer_id -> customers.customer_id`

### Columnas reales
- `email_id`
- `customer_id`
- `email`
- `email_type`
- `is_primary`
- `is_verified`

### Usos posibles
- contexto de contacto
- futuras mejoras

### Observaciones
- no usar para autenticación
- puede haber más de un correo por cliente

---

## 6. Tabla `addresses`

### Propósito
Direcciones asociadas al cliente.

### Clave principal
- `address_id`

### Relación principal
- `customer_id -> customers.customer_id`

### Columnas reales
- `address_id`
- `customer_id`
- `address_line1`
- `address_line2`
- `city`
- `department`
- `postal_code`
- `country`
- `delivery_notes`
- `landmark`
- `requires_appointment`
- `address_type`
- `is_default`
- `is_residential`

### Usos principales
- contexto de entrega
- detalle de dirección para pedidos con entrega a domicilio

### Observaciones
- no toda consulta de pedido requiere dirección
- usar con cuidado en consultas sensibles
- la dirección del pedido debe cruzarse con `orders.address_id`

---

## 7. Tabla `cards`

### Propósito
Tarjetas registradas del cliente.

### Clave principal
- `card_id`

### Relación principal
- `customer_id -> customers.customer_id`

### Columnas reales
- `card_id`
- `customer_id`
- `bin`
- `last_four`
- `card_type`
- `bank`
- `expiration_date`
- `is_primary`

### Usos posibles
- relación con pedidos pagados con tarjeta
- referencia interna de pago

### Observaciones
- no exponer detalles sensibles de tarjeta
- no es tabla central para el MVP del agente

---

## 8. Tabla `categories`

### Propósito
Catálogo de categorías.

### Clave principal
- `category_id`

### Columnas reales
- `category_id`
- `name`

### Usos principales
- enriquecer consultas de catálogo
- agrupar productos por categoría
- relacionar promociones por categoría

---

## 9. Tabla `brands`

### Propósito
Catálogo de marcas.

### Clave principal
- `brand_id`

### Columnas reales
- `brand_id`
- `name`

### Usos principales
- enriquecer respuestas de catálogo
- filtrar productos por marca

---

## 10. Tabla `products`

### Propósito
Catálogo principal de productos.

### Clave principal
- `product_id`

### Relaciones principales
- `category_id -> categories.category_id`
- `brand_id -> brands.brand_id`

### Columnas reales
- `product_id`
- `category_id`
- `brand_id`
- `name`
- `description`
- `specifications`
- `warranty_months`
- `return_days`
- `is_final_sale`
- `free_shipping`
- `shipping_days`
- `price`
- `active`
- `weight_kg`
- `requires_installation`
- `installation_notes`

### Usos principales
- precio general de producto
- características del producto
- garantía general del producto
- devolución general del producto
- envío gratis
- si requiere instalación
- tiempo general de envío del producto
- disponibilidad lógica junto con stock

### Observaciones
- `return_days = 0` implica que no tiene devolución
- `is_final_sale = true` implica producto sin devolución
- `active` indica si el producto está activo
- `warranty_months` sirve para contexto general
- para compras reales manda `order_items`

---

## 11. Tabla `stock`

### Propósito
Inventario por producto.

### Clave principal
- `stock_id`

### Relación principal
- `product_id -> products.product_id`

### Columnas reales
- `stock_id`
- `product_id`
- `warehouse_location`
- `stock_qty`
- `reserved_qty`
- `low_stock_threshold`
- `restock_date`
- `last_updated`

### Regla de negocio
Stock disponible real:
- `stock_qty - reserved_qty`

### Usos principales
- responder disponibilidad general
- advertir bajo stock
- estimar reabastecimiento

---

## 12. Tabla `promotions`

### Propósito
Promociones activas e históricas.

### Clave principal
- `promotion_id`

### Columnas reales
- `promotion_id`
- `promotion_name`
- `description`
- `discount_type`
- `discount_value`
- `min_purchase_amount`
- `start_date`
- `end_date`
- `active`
- `applicable_category_ids`
- `applicable_product_ids`

### Usos principales
- responder promociones generales
- detectar descuentos activos
- enriquecer respuesta de catálogo
- validar si una compra pudo estar afectada por promoción

### Observaciones
- `applicable_category_ids` y `applicable_product_ids` pueden requerir parseo
- un producto comprado en promoción puede afectar devolución según política

---

## 13. Tabla `orders`

### Propósito
Cabecera principal del pedido.

### Clave principal
- `order_id`

### Relaciones principales
- `customer_id -> customers.customer_id`
- `address_id -> addresses.address_id`
- `card_id -> cards.card_id`

### Columnas reales
- `order_id`
- `customer_id`
- `address_id`
- `order_date`
- `payment_confirmed_at`
- `shipped_at`
- `delivered_at`
- `cancelled_at`
- `status`
- `subtotal`
- `shipping_cost`
- `tax`
- `total_amount`
- `delivery_method`
- `payment_method`
- `card_id`
- `customer_notes`
- `internal_notes`
- `cancellation_reason`

### Usos principales
- montos del pedido
- estado actual resumido del pedido
- fechas principales del ciclo del pedido
- método de entrega
- método de pago
- costo de envío
- motivo de cancelación

### Observaciones
- `status` es la fuente principal del estado actual
- montos del pedido salen de esta tabla
- `internal_notes` no debe exponerse directamente al cliente
- consultas de pedido específico requieren autenticación

---

## 14. Tabla `order_items`

### Propósito
Detalle por ítem del pedido.

### Clave principal
- `item_id`

### Relaciones principales
- `order_id -> orders.order_id`
- `product_id -> products.product_id`

### Columnas reales
- `item_id`
- `order_id`
- `product_id`
- `qty`
- `unit_price`
- `warranty_expires_at`
- `return_deadline`
- `item_status`

### Usos principales
- desglose por producto comprado
- cantidad comprada
- precio unitario de compra
- vigencia específica de garantía
- vigencia específica de devolución
- estado del ítem

### Observaciones
- `qty` es la cantidad comprada
- esta tabla manda en garantía y devolución específicas
- un pedido puede tener varios ítems con estados distintos
- `item_status` puede diferir del estado global del pedido

---

## 15. Tabla `shipments`

### Propósito
Información logística de envío a nivel de ítem o envío asociado.

### Clave principal
- `shipment_id`

### Relaciones principales
- `order_id -> orders.order_id`
- `item_id -> order_items.item_id`

### Columnas reales
- `shipment_id`
- `order_id`
- `item_id`
- `carrier`
- `tracking_number`
- `tracking_url`
- `shipped_date`
- `estimated_delivery_date`
- `actual_delivery_date`
- `delivery_attempts`
- `last_attempt_date`
- `failed_delivery_reason`
- `shipment_status`

### Usos principales
- transportadora
- número de guía
- URL de tracking
- fecha estimada de entrega
- fecha real de entrega
- intentos de entrega
- razón de fallo de entrega
- estado logístico del envío

### Observaciones
- es muy útil para preguntas específicas de envío
- un pedido puede tener varios envíos o envíos por ítem
- la logística detallada debe cruzarse con `orders` y `tracking`

---

## 16. Tabla `tracking`

### Propósito
Historial de eventos del pedido y/o del ítem.

### Clave principal
- `tracking_id`

### Relaciones principales
- `order_id -> orders.order_id`
- `item_id -> order_items.item_id`

### Columnas reales
- `tracking_id`
- `order_id`
- `item_id`
- `timestamp`
- `status`
- `location`

### Usos principales
- historial de estados
- línea de tiempo del envío o pedido
- soporte a preguntas como:
  - dónde va mi pedido
  - cuándo salió
  - cuándo fue entregado
  - qué pasó en cada etapa

### Observaciones
- `timestamp` es el momento del evento
- `status` en esta tabla representa el evento histórico
- no confundir con `orders.status`, que representa el estado actual resumido

---

## 17. Relaciones principales para el agente

### Relaciones núcleo
- `orders.customer_id = customers.customer_id`
- `orders.address_id = addresses.address_id`
- `orders.card_id = cards.card_id`
- `orders.order_id = order_items.order_id`
- `order_items.product_id = products.product_id`
- `shipments.order_id = orders.order_id`
- `shipments.item_id = order_items.item_id`
- `tracking.order_id = orders.order_id`
- `tracking.item_id = order_items.item_id`

### Relaciones de catálogo
- `products.category_id = categories.category_id`
- `products.brand_id = brands.brand_id`
- `stock.product_id = products.product_id`

### Relaciones de contacto
- `customer_emails.customer_id = customers.customer_id`
- `addresses.customer_id = customers.customer_id`
- `cards.customer_id = customers.customer_id`

---

## 18. Fuente principal por tipo de pregunta

### Autenticación
- `customers`

### Precio general de producto
- `products`

### Stock general
- `stock`
- `products`

### Promociones
- `promotions`
- `products`
- `categories`

### Montos de pedido
- `orders`
- `order_items` si se requiere desglose

### Estado actual del pedido
- `orders`
- `shipments` si complementa

### Historial del pedido
- `tracking`

### Logística de envío
- `shipments`
- `tracking`

### Garantía específica de una compra
- `order_items`
- `products`

### Devolución específica de una compra
- `order_items`
- `products`
- `orders`

---

## 19. Reglas de prioridad de datos

### Prioridad 1
Dato específico de compra real:
- `orders`
- `order_items`
- `shipments`
- `tracking`

### Prioridad 2
Dato general de producto:
- `products`
- `stock`
- `promotions`

### Prioridad 3
Políticas del negocio:
- documentos Markdown

### Principio
Si existe un dato específico de compra, ese dato manda sobre la descripción general.

---

## 20. Riesgos que se deben evitar

- autenticar con nombre o email
- exponer `internal_notes`
- responder dirección de entrega si el pedido es `pickup_point`
- asumir que todos los ítems del pedido tienen la misma vigencia
- responder montos o estados sin consultar la fuente correcta
- confundir `orders.status` con eventos históricos de `tracking`
- suponer que un producto general tiene la misma condición exacta que un ítem ya comprado

---

## 21. Campos especialmente importantes para el MVP

### En autenticación
- `customers.customer_id`
- `customers.dni`
- `customers.phone`
- `customers.name`
- `customers.last_name1`
- `customers.last_name2`

### En pedidos
- `orders.order_id`
- `orders.customer_id`
- `orders.status`
- `orders.subtotal`
- `orders.shipping_cost`
- `orders.tax`
- `orders.total_amount`
- `orders.delivery_method`
- `orders.payment_method`

### En ítems
- `order_items.item_id`
- `order_items.order_id`
- `order_items.product_id`
- `order_items.qty`
- `order_items.unit_price`
- `order_items.warranty_expires_at`
- `order_items.return_deadline`
- `order_items.item_status`

### En logística
- `shipments.carrier`
- `shipments.tracking_number`
- `shipments.estimated_delivery_date`
- `shipments.actual_delivery_date`
- `shipments.delivery_attempts`
- `shipments.shipment_status`

### En historial
- `tracking.timestamp`
- `tracking.status`
- `tracking.location`

---

## 22. Principio final

Ante una duda entre:
- asumir
- o consultar la tabla correcta

siempre se debe consultar la tabla correcta.