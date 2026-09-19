# Sistema de Control de Acceso — Errores y Correcciones

## Descripción

Este proyecto implementa un sistema de control de acceso utilizando una **Raspberry Pi Pico**, dos botones (`A` y `B`) y tres LEDs:

* 🔴 Rojo: sistema bloqueado.
* 🟡 Amarillo: esperando el botón B.
* 🟢 Verde: acceso concedido.

La secuencia correcta para acceder es:

**A → B**

El sistema también cuenta los intentos incorrectos y activa un bloqueo de seguridad después de **3 errores consecutivos**.

---

## Errores encontrados y correcciones

### 1. Lógica de los botones

Los botones fueron configurados utilizando:

```python
A = Pin(16, Pin.IN, Pin.PULL_UP)
B = Pin(17, Pin.IN, Pin.PULL_UP)
```

Al utilizar `PULL_UP`, el estado normal del botón es `1` y al presionarlo cambia a `0`.

Por esta razón se utiliza:

```python
trigger=Pin.IRQ_FALLING
```

para detectar la pulsación.

---

### 2. Rebote de los botones

Un botón físico puede generar varias señales eléctricas al momento de presionarse. Esto puede provocar que una sola pulsación sea interpretada como varias.

Para evitarlo se agregó un sistema de **anti-rebote**:

```python
DEBOUNCE = 300
```

y se guarda el momento de la última pulsación:

```python
ultimo_A = 0
ultimo_B = 0
```

Antes de procesar una nueva pulsación se comprueba:

```python
if time.ticks_diff(ahora, ultimo_A) < DEBOUNCE:
    return
```

Esto evita eventos repetidos provocados por el rebote del botón.

---

### 3. Presionar B antes que A

Otro error contemplado es presionar `B` cuando el sistema todavía está bloqueado.

El programa detecta esta situación:

```python
if estado == BLOQUEADO:
    print("[ERROR] B fue presionado antes que A")
    fallo()
```

Esto aumenta el contador de errores.

---

### 4. Presionar A varias veces

Cuando el sistema ya está esperando que se presione `B`, una nueva pulsación de `A` no debe reiniciar la secuencia.

Por eso se utiliza:

```python
elif estado == ESPERANDO:
    print("[INFO] A ignorado: ya esperando B")
```

---

### 5. Tiempo de espera para B

Después de presionar `A`, el usuario tiene **5 segundos** para presionar `B`.

Se utiliza un temporizador de una sola ejecución:

```python
timer.init(
    mode=Timer.ONE_SHOT,
    period=5000,
    callback=timeout
)
```

Si no se presiona `B` dentro de ese tiempo, se genera un error:

```text
[ERROR] TIMEOUT
[ERROR] B no fue presionado a tiempo
```

---

### 6. Temporizador activo después de presionar B

Si `B` se presiona correctamente, el temporizador de 5 segundos debe detenerse.

Para esto se utiliza:

```python
timer.deinit()
```

Después se cambia el estado a:

```python
estado = ACCESO
```

y comienza el temporizador de acceso de 3 segundos.

---

### 7. Tres errores consecutivos

Cuando el contador llega a 3:

```python
if fallos >= 3:
```

el sistema cambia al estado:

```python
estado = SEGURIDAD
```

El LED amarillo permanece encendido durante el bloqueo:

```python
rojo.off()
amarillo.on()
verde.off()
```

El sistema queda bloqueado durante **10 segundos**:

```python
timer_seguridad.init(
    mode=Timer.ONE_SHOT,
    period=10000,
    callback=fin_seguridad
)
```

Durante este periodo, las pulsaciones de `A` y `B` son ignoradas.

---

### 8. Reinicio después del bloqueo

Al terminar los 10 segundos se ejecuta:

```python
def fin_seguridad(t):
```

Se reinicia el contador:

```python
fallos = 0
```

y el sistema vuelve al estado bloqueado:

```python
estado = BLOQUEADO
```

Finalmente se enciende nuevamente el LED rojo.

---

## Máquina de estados

El programa utiliza cuatro estados:

| Estado      | Valor | Función                             |
| ----------- | ----: | ----------------------------------- |
| `BLOQUEADO` |     0 | Espera que se presione A            |
| `ESPERANDO` |     1 | Espera que se presione B            |
| `ACCESO`    |     2 | Acceso concedido durante 3 segundos |
| `SEGURIDAD` |     3 | Bloqueo durante 10 segundos         |

### Secuencia normal

```text
BLOQUEADO
    ↓
    A
    ↓
ESPERANDO
    ↓
    B
    ↓
ACCESO
    ↓
 3 segundos
    ↓
BLOQUEADO
```

### Secuencia de error

```text
BLOQUEADO
    ↓
 Error
    ↓
fallos + 1
    ↓
¿3 errores?
    ↓ Sí
SEGURIDAD
    ↓
10 segundos
    ↓
BLOQUEADO
```

## Resumen

Los principales problemas corregidos fueron:

1. Configuración correcta de botones con `PULL_UP`.
2. Detección de pulsación mediante `IRQ_FALLING`.
3. Protección contra rebote.
4. Control de la secuencia `A → B`.
5. Temporizador de 5 segundos para presionar `B`.
6. Cancelación del temporizador cuando `B` es presionado.
7. Contador de errores.
8. Bloqueo de seguridad después de 3 errores.
9. Bloqueo de 10 segundos.
10. Reinicio del contador después del bloqueo.
11. Uso de una máquina de estados para controlar el comportamiento del sistema.

# Errores corregidos en `diagram.json`

Durante la configuración del circuito en Wokwi se encontraron algunos errores en el archivo `diagram.json`:

* Se corrigieron las conexiones de los **LEDs** con los GPIO correspondientes.
* Se corrigieron las conexiones de los **botones A y B**.
* Se verificó que los GPIO utilizados en el JSON coincidieran con los definidos en `main.py`.
* Se corrigieron conexiones que impedían que los botones funcionaran correctamente.
* Se revisó la configuración del circuito para evitar errores de sintaxis en el archivo JSON.

Después de las correcciones, el circuito funcionó correctamente en Wokwi.
