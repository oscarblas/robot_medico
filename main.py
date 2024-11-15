import pygame
import sys
import time
import math
import random
import pyttsx3  # Para texto a voz
import speech_recognition as sr  # Para reconocimiento de voz
import threading

# Inicialización de pygame
pygame.init()

# Inicialización de pyttsx3
engine = pyttsx3.init()
is_speaking = False  # Variable para controlar si el robot está hablando

# Inicialización de SpeechRecognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Dimensiones de la ventana en modo exclusivo de pantalla completa
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size()  # Obtener tamaño de pantalla completa
pygame.display.set_caption("Animación de cara de robot con micrófono dibujado")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Tamaño y posición de los ojos
eye_width, eye_height = 300, 350  # Tamaño de los ojos aumentado
eye_distance = 250  # Distancia entre los ojos
left_eye_base_x = WIDTH // 2 - eye_distance - eye_width // 2  # Posición base de los ojos
right_eye_base_x = WIDTH // 2 + eye_distance - eye_width // 2
eye_y_base = HEIGHT // 3 - 50  # Posición vertical base de los ojos

# Variables para el movimiento de los ojos
eye_x_offset = 0
eye_y_offset = 0
last_eye_move_time = time.time()
eye_move_interval = 1.5  # Intervalo de tiempo entre movimientos aleatorios de los ojos

# Variables para el movimiento de las pupilas
pupil_radius = eye_width // 3  # Tamaño de la pupila aumentado proporcionalmente
pupil_x_offset = 0
pupil_y_offset = 0
last_pupil_move_time = time.time()
pupil_move_interval = 1  # Intervalo de tiempo entre movimientos aleatorios de las pupilas

# Variables para el parpadeo
is_blinking = False
last_blink_time = time.time()
blink_interval = 3  # Segundos entre parpadeos
blink_duration = 0.2  # Duración del parpadeo en segundos

# Variables para la boca
mouth_open = False
last_mouth_change = time.time()
mouth_change_interval = 0.2  # Intervalo para abrir/cerrar la boca

# Variables para el estado de escucha
is_listening = False
dots = ""  # Para los puntos suspensivos animados
dots_update_time = 0.5  # Tiempo entre actualizaciones de puntos
last_dots_update = time.time()

# Variables para mostrar el DNI y nombre
show_check = False
display_text = ""  # Almacena el texto que se mostrará en la pantalla (DNI o nombre)
show_text_time = 0
dni_asked = False  # Controla si se ha preguntado el DNI
name_asked = False  # Controla si se ha preguntado el nombre
waiting_for_next_question = False  # Controla si está esperando para preguntar el nombre

# Variables de espera para el flujo de preguntas
wait_time_after_check = 10  # Tiempo de espera tras mostrar el check verde antes de la siguiente pregunta

# Cargar sonido "ding.mp3"
pygame.mixer.init()
ding_sound = pygame.mixer.Sound("ding.mp3")  # Asegúrate de tener el archivo "ding.mp3" en la misma carpeta

# Bandera para controlar si el sonido "ding" ya ha sido reproducido
ding_played = False

# Función para mover los ojos a una posición aleatoria
def move_eyes_randomly():
    global eye_x_offset, eye_y_offset, last_eye_move_time
    if time.time() - last_eye_move_time > eye_move_interval:
        eye_x_offset = random.randint(-20, 20)
        eye_y_offset = random.randint(-10, 10)
        last_eye_move_time = time.time()

# Función para mover las pupilas a una posición aleatoria
def move_pupils_randomly():
    global pupil_x_offset, pupil_y_offset, last_pupil_move_time
    if time.time() - last_pupil_move_time > pupil_move_interval:
        pupil_x_offset = random.randint(-20, 20)
        pupil_y_offset = random.randint(-10, 10)
        last_pupil_move_time = time.time()

# Función para dibujar el micrófono
def draw_microphone():
    global last_dots_update, dots
    screen.fill(BLACK)  # Asegurarse de limpiar la pantalla antes de dibujar el micrófono
    mic_x = WIDTH // 2
    mic_y = HEIGHT // 2
    mic_width = 80
    mic_height = 150
    base_width = 100
    base_height = 20
    stand_width = 10
    stand_height = 60

    pygame.draw.ellipse(screen, BLUE, (mic_x - mic_width // 2, mic_y - mic_height // 2, mic_width, mic_height))

    line_y_offset = mic_height // 4
    for i in range(-1, 2):
        pygame.draw.line(screen, BLUE, (mic_x - mic_width // 2 + 10, mic_y + i * line_y_offset),
                         (mic_x + mic_width // 2 - 10, mic_y + i * line_y_offset), 6)

    pygame.draw.rect(screen, BLUE, (mic_x - stand_width // 2, mic_y + mic_height // 2, stand_width, stand_height))
    pygame.draw.rect(screen, BLUE, (mic_x - base_width // 2, mic_y + mic_height // 2 + stand_height, base_width, base_height))

    pygame.draw.arc(screen, BLUE, (mic_x - mic_width, mic_y - mic_height + 110, mic_width * 2, mic_height), math.pi, 2 * math.pi, 10)

    if time.time() - last_dots_update > dots_update_time:
        dots += "." if len(dots) < 3 else ""
        dots = "" if len(dots) >= 3 else dots
        last_dots_update = time.time()

    font = pygame.font.Font(None, 50)
    dots_text = font.render("Escuchando" + dots, True, WHITE)
    screen.blit(dots_text, (WIDTH // 2 - dots_text.get_width() // 2, mic_y + mic_height // 2 + stand_height + base_height + 20))

# Función para dibujar los ojos y la boca animada
def draw_eyes_and_mouth():
    global mouth_open, last_mouth_change
    screen.fill(BLACK)

    move_eyes_randomly()
    move_pupils_randomly()

    left_eye_x = left_eye_base_x + eye_x_offset
    right_eye_x = right_eye_base_x + eye_x_offset
    eye_y = eye_y_base + eye_y_offset

    pygame.draw.ellipse(screen, WHITE, (left_eye_x, eye_y, eye_width, eye_height))
    pygame.draw.circle(screen, BLACK, (left_eye_x + eye_width // 2 + pupil_x_offset, eye_y + eye_height // 2 + pupil_y_offset), pupil_radius)
    pygame.draw.circle(screen, WHITE, (left_eye_x + eye_width // 2 + pupil_x_offset - 10, eye_y + eye_height // 2 + pupil_y_offset - 20), pupil_radius // 4)

    pygame.draw.ellipse(screen, WHITE, (right_eye_x, eye_y, eye_width, eye_height))
    pygame.draw.circle(screen, BLACK, (right_eye_x + eye_width // 2 + pupil_x_offset, eye_y + eye_height // 2 + pupil_y_offset), pupil_radius)
    pygame.draw.circle(screen, WHITE, (right_eye_x + eye_width // 2 + pupil_x_offset - 10, eye_y + eye_height // 2 + pupil_y_offset - 20), pupil_radius // 4)

    if is_speaking:
        if mouth_open:
            pygame.draw.ellipse(screen, WHITE, (WIDTH // 2 - 50, HEIGHT // 2 + 100, 100, 60))
        else:
            pygame.draw.line(screen, WHITE, (WIDTH // 2 - 50, HEIGHT // 2 + 130), (WIDTH // 2 + 50, HEIGHT // 2 + 130), 10)
        if time.time() - last_mouth_change > mouth_change_interval:
            mouth_open = not mouth_open
            last_mouth_change = time.time()

# Función para mostrar el check verde y el texto en pantalla completa
def show_full_screen_check():
    global show_check, ding_played
    screen.fill(BLACK)
    check_position = (WIDTH // 2, HEIGHT // 2 - 50)
    pygame.draw.circle(screen, GREEN, check_position, 50)
    pygame.draw.line(screen, BLACK, (check_position[0] - 15, check_position[1]), (check_position[0] - 5, check_position[1] + 15), 5)
    pygame.draw.line(screen, BLACK, (check_position[0] - 5, check_position[1] + 15), (check_position[0] + 20, check_position[1] - 20), 5)

    font = pygame.font.Font(None, 80)
    text_surface = font.render(display_text, True, WHITE)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 + 50))

    # Reproducir el sonido "ding" solo una vez cuando aparece el check verde
    if not ding_played:
        ding_sound.play()
        ding_played = True  # Marcar que el sonido ha sido reproducido

# Función para iniciar el habla del robot y preguntar
def start_speaking(question, expected_input):
    global is_speaking
    is_speaking = True
    engine.say(question)
    engine.runAndWait()
    is_speaking = False
    threading.Thread(target=listen_for_input, args=(expected_input,)).start()

# Función para escuchar y reconocer la respuesta en paralelo
def listen_for_input(expected_input):
    global show_check, display_text, show_text_time, is_listening, waiting_for_next_question, ding_played
    is_listening = True
    with microphone as source:
        print("Escuchando...")
        audio_data = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio_data, language="es-ES")
        display_text = f"{expected_input.capitalize()}: {text.strip()}"
        show_text_time = time.time()
        show_check = True
        ding_played = False  # Reiniciar la bandera para permitir que el sonido se reproduzca la próxima vez
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
    except sr.RequestError:
        print("Error en el servicio de reconocimiento de voz")
    finally:
        is_listening = False

# Bucle principal
clock = pygame.time.Clock()
start_time = time.time()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    current_time = time.time()

    # Preguntar el DNI después de 5 segundos desde el inicio
    if not dni_asked and current_time - start_time >= 5:
        start_speaking("Por favor, dime tu número de DNI, deletreado", "DNI")
        dni_asked = True

    # Mostrar el DNI reconocido con check verde durante 5 segundos
    if show_check and time.time() - show_text_time < 5:
        show_full_screen_check()

    # Después de mostrar el check verde, esperar 10 segundos antes de pasar a la siguiente pregunta
    elif show_check and time.time() - show_text_time >= 4:
        show_check = False
        waiting_for_next_question = True
        start_time = time.time()

    # Preguntar el nombre después de 10 segundos de esperar tras el DNI
    if waiting_for_next_question and not name_asked and current_time - start_time >= wait_time_after_check:
        start_speaking("¿Cuál es tu nombre?", "Nombre")
        name_asked = True
        waiting_for_next_question = False

    # Mostrar el micrófono si está escuchando
    if is_listening:
        draw_microphone()
    elif not show_check:
        draw_eyes_and_mouth()

    pygame.display.flip()
    clock.tick(30)
