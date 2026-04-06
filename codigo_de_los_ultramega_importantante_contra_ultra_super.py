from machine import Pin, PWM, ADC
import time

# POTENCIOMETROS
pot_extra1 = ADC(Pin(33))
pot_extra2 = ADC(Pin(32))
pot_extra3 = ADC(Pin(13))

pot_extra1.atten(ADC.ATTN_11DB)
pot_extra2.atten(ADC.ATTN_11DB)
pot_extra3.atten(ADC.ATTN_11DB)

pot_extra1.width(ADC.WIDTH_10BIT)
pot_extra2.width(ADC.WIDTH_12BIT)
pot_extra3.width(ADC.WIDTH_12BIT)

# SERVOS 
servo_extra1 = PWM(Pin(12), freq=50)
servo_extra2 = PWM(Pin(14), freq=50)
servo_extra3 = PWM(Pin(27), freq=50)

# BOTONES 
boton_retorno = Pin(18, Pin.IN, Pin.PULL_UP)
boton_rutina = Pin(19 , Pin.IN, Pin.PULL_UP)

# ANTIRREBOTE 
ultimo_retorno = 0
ultimo_rutina = 0
debounce = 200  # ms

# LEDS 
led_verde = Pin(0, Pin.OUT)
led_rojo = Pin(4, Pin.OUT)

# BUZZER 
buzzer = PWM(Pin(26))
buzzer.duty(0)

# ESTADOS 
modo_manual = True
retorno = False
rutina_auto = False

# FILTRO EMA 
alpha = 0.5
f_extra1 = 0
f_extra2 = 0
f_extra3 = 0

def ema(nuevo, anterior):
    return alpha * nuevo + (1 - alpha) * anterior

# SERVOS 
def mover_servo_extra1(angulo):
    duty = 40 + (angulo / 180) * (115 - 40)
    servo_extra1.duty(int(duty))

def mover_servo_extra2(angulo):
    duty = 40 + (angulo / 180) * (115 - 40)
    servo_extra2.duty(int(duty))

def mover_servo_extra3(angulo):
    duty = 40 + (angulo / 180) * (115 - 40)
    servo_extra3.duty(int(duty))

# BUZZER 
def beep_retorno():
    buzzer.freq(1000)
    buzzer.duty(512)
    time.sleep(0.15)
    buzzer.duty(0)

def beep_rutina():
    buzzer.freq(2000)
    buzzer.duty(512)
    time.sleep(0.1)
    buzzer.duty(0)
    time.sleep(0.05)
    buzzer.duty(512)
    time.sleep(0.1)
    buzzer.duty(0)

# MOVIMIENTOS 
def posicion_inicial():
    for a in range(90, 0, -2):
        mover_servo_extra1(a)
        mover_servo_extra2(a)
        mover_servo_extra3(a)
        time.sleep(0.02)

def rutina():
    for a in range(0,120,3):
        mover_servo_extra1(a)
        mover_servo_extra2(a)
        mover_servo_extra3(a)
        time.sleep(0.02)

    for a in range(120,30,-3):
        mover_servo_extra1(a)
        mover_servo_extra2(a)
        mover_servo_extra3(a)
        time.sleep(0.02)

# INTERRUPCIONES CON ANTIRREBOTE 
def handler_retorno(pin):
    global retorno, ultimo_retorno
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, ultimo_retorno) > debounce:
        retorno = True
        ultimo_retorno = ahora

def handler_rutina(pin):
    global rutina_auto, ultimo_rutina
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, ultimo_rutina) > debounce:
        rutina_auto = True
        ultimo_rutina = ahora

boton_retorno.irq(trigger=Pin.IRQ_FALLING, handler=handler_retorno)
boton_rutina.irq(trigger=Pin.IRQ_FALLING, handler=handler_rutina)

# INICIO
led_verde.on()

# LOOP 
while True:

    if retorno:
        retorno = False
        modo_manual = False

        led_verde.off()
        led_rojo.on()

        beep_retorno()
        posicion_inicial()

        led_rojo.off()
        led_verde.on()
        modo_manual = True

    elif rutina_auto:
        rutina_auto = False
        modo_manual = False

        led_verde.off()
        led_rojo.on()

        beep_rutina()
        rutina()
        posicion_inicial()

        led_rojo.off()
        led_verde.on()
        modo_manual = True

    elif modo_manual:

        raw_extra1 = pot_extra1.read()
        raw_extra2 = pot_extra2.read()
        raw_extra3 = pot_extra3.read()

        volt_extra1 = (raw_extra1 / 1023) * 3.3
        volt_extra2 = (raw_extra2 / 4095) * 3.3
        volt_extra3 = (raw_extra3 / 4095) * 3.3

        ang_extra1 = (raw_extra1 / 1023) * 180
        ang_extra2 = (raw_extra2 / 4095) * 180
        ang_extra3 = (raw_extra3 / 4095) * 180

        # EMA 
        f_extra1 = ema(ang_extra1, f_extra1)
        f_extra2 = ema(ang_extra2, f_extra2)
        f_extra3 = ema(ang_extra3, f_extra3)

        mover_servo_extra1(f_extra1)
        mover_servo_extra2(f_extra2)
        mover_servo_extra3(f_extra3)

        time.sleep(0.05)

        print("Extra1 -> ADC:", raw_extra1,
              "Volt:", round(volt_extra1, 2),
              "Ang:", int(f_extra1))

        print("Extra2 -> ADC:", raw_extra2,
              "Volt:", round(volt_extra2, 2),
              "Ang:", int(f_extra2))

        print("Extra3 -> ADC:", raw_extra3,
              "Volt:", round(volt_extra3, 2),
              "Ang:", int(f_extra3))

        print("------------------------")

    time.sleep(0.05)