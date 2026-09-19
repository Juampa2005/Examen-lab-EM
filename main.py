from machine import Pin, Timer
import time
rojo = Pin(13, Pin.OUT)
amarillo = Pin(14, Pin.OUT)
verde = Pin(15, Pin.OUT)

A = Pin(16, Pin.IN, Pin.PULL_UP)
B = Pin(17, Pin.IN, Pin.PULL_UP)

BLOQUEADO = 0
ESPERANDO = 1
ACCESO = 2
SEGURIDAD = 3

estado = BLOQUEADO
fallos = 0

timer = Timer()
timer_acceso = Timer()
timer_seguridad = Timer()


# ==================================================
# All Things Must Pass
# ANTI-REBOTE
# ==================================================

ultimo_A = 0
ultimo_B = 0

DEBOUNCE = 300


def bloqueado():
    rojo.on()
    amarillo.off()
    verde.off()

    print()
    print("==============================")
    print("[LISTO] SISTEMA BLOQUEADO")
    print("[LED] ROJO: ON")
    print("[LISTO] Secuencia correcta: A -> B")
    print("==============================")


# ==================================================
# ESPERANDO B
# ==================================================

def esperando():
    rojo.off()
    amarillo.on()
    verde.off()

    print()
    print("------------------------------")
    print("[INFO] A detectado")
    print("[ESPERA] Presiona B")
    print("[TIMER] Ventana: 5 segundos")
    print("------------------------------")


# ==================================================
# What Is Life wihout you?    (   ͡°╭╮ʖ   ͡°)
# ACCESO CONCEDIDO
# ==================================================

def acceso():
    rojo.off()
    amarillo.off()
    verde.on()

    print()
    print("==============================")
    print("[OK] ACCESO CONCEDIDO")
    print("[LED] VERDE: ON")
    print("[TIMER] Acceso durante 3 segundos")
    print("==============================")


def fallo():
    global estado, fallos

    fallos += 1

    print("[ERROR] Intentos fallidos:", fallos)

    if fallos >= 3:

        estado = SEGURIDAD

        rojo.on()
        amarillo.off()
        verde.off()

        print()
        print("[BLOQUEO] 3 errores detectados")
        print("[BLOQUEO] Sistema bloqueado 10 segundos")

        timer_seguridad.init(
            mode=Timer.ONE_SHOT,
            period=10000,
            callback=fin_seguridad
        )

    else:

        estado = BLOQUEADO

        print("[LISTO] Intenta nuevamente con A -> B")

        bloqueado()


def timeout(t):
    global estado

    if estado == ESPERANDO:

        print()
        print("[ERROR] TIMEOUT")
        print("[ERROR] B no fue presionado a tiempo")

        fallo()


# ==================================================
# 200 años de que sirvio?
# FINALIZAR ACCESO
# ==================================================

def fin_acceso(t):
    global estado

    estado = BLOQUEADO

    print()
    print("[TIMER] Fin del acceso")

    bloqueado()


# ==================================================
# FINALIZAR BLOQUEO
# ==================================================

def fin_seguridad(t):
    global estado, fallos

    fallos = 0
    estado = BLOQUEADO

    print()
    print("[TIMER] Fin del bloqueo")
    print("[RESET] Intentos fallidos = 0")

    bloqueado()


# ==================================================
# INTERRUPCION DEL BOTON A
# ==================================================

def presionar_A(pin):
    global estado, ultimo_A

    ahora = time.ticks_ms()

    # Anti-rebote
    if time.ticks_diff(ahora, ultimo_A) < DEBOUNCE:
        return

    ultimo_A = ahora

    if estado == BLOQUEADO:

        estado = ESPERANDO

        esperando()

        timer.init(
            mode=Timer.ONE_SHOT,
            period=5000,
            callback=timeout
        )

    elif estado == SEGURIDAD:

        print("[INFO] A ignorado: bloqueo de seguridad")

    elif estado == ESPERANDO:

        print("[INFO] A ignorado: ya esperando B")

    elif estado == ACCESO:

        print("[INFO] A ignorado: acceso activo")


# ==================================================
# INTERRUPCION DEL BOTON B
# ==================================================

def presionar_B(pin):
    global estado, ultimo_B

    ahora = time.ticks_ms()

    # Anti-rebote
    if time.ticks_diff(ahora, ultimo_B) < DEBOUNCE:
        return

    ultimo_B = ahora

    if estado == BLOQUEADO:

        print()
        print("[ERROR] B fue presionado antes que A")

        fallo()

    elif estado == ESPERANDO:

        timer.deinit()

        estado = ACCESO

        acceso()

        timer_acceso.init(
            mode=Timer.ONE_SHOT,
            period=3000,
            callback=fin_acceso
        )

    elif estado == SEGURIDAD:

        print("[INFO] B ignorado: bloqueo de seguridad")

    elif estado == ACCESO:

        print("[INFO] B ignorado: acceso activo")


# ==================================================
# INTERRUPCIONES
# ==================================================

A.irq(
    trigger=Pin.IRQ_FALLING,
    handler=presionar_A
)

B.irq(
    trigger=Pin.IRQ_FALLING,
    handler=presionar_B
)


# ==================================================
# INICIO DEL SISTEMA
# ==================================================

bloqueado()

print()
print("[SISTEMA] Sistema iniciado")
print("[SISTEMA] Esperando eventos...")
print()


# ==================================================
# BUCLE PRINCIPAL
# ==================================================

while True:
    time.sleep_ms(100)
