from controller import Supervisor, Keyboard
from sympy import Matrix, cos, sin, pi
import math

supervisor = Supervisor()
paso_tiempo = int(supervisor.getBasicTimeStep())

# Obtener el nodo del humanoide
nodo_peaton = supervisor.getFromDef("pedestrian1")
if nodo_peaton is None:
    print("ERROR: No se encontró el nodo con DEF del humanoide")

# 🔥 BOTELLA
nodo_botella = supervisor.getFromDef("botella1")
if nodo_botella is None:
    print("ERROR: No se encontró la botella")

# Parámetros de movimiento
TAMANO_PASO = 0.05
PASO_ANGULO = math.pi / 36

# Activar teclado
teclado = supervisor.getKeyboard()
teclado.enable(paso_tiempo)

# ---------------------------------------------------------------
# TRASLACIÓN
# ---------------------------------------------------------------
def trasladar(nodo, dx_local, dy_local):
    campo_traslacion = nodo.getField("translation")
    pos = campo_traslacion.getSFVec3f()
    P_vieja = Matrix([pos[0], pos[1], pos[2]])

    campo_rotacion = nodo.getField("rotation")
    _, _, _, angulo = campo_rotacion.getSFRotation()

    R_z = Matrix([
        [cos(angulo), -sin(angulo), 0],
        [sin(angulo),  cos(angulo), 0],
        [0, 0, 1]
    ])

    d_local = Matrix([dx_local, dy_local, 0])
    d_mundial = R_z * d_local
    P_nueva = P_vieja + d_mundial

    campo_traslacion.setSFVec3f([
        float(P_nueva[0]),
        float(P_nueva[1]),
        float(P_nueva[2])
    ])

# ---------------------------------------------------------------
# ROTACIÓN
# ---------------------------------------------------------------
def rotar_z(nodo, delta_angulo):
    campo_rotacion = nodo.getField("rotation")
    _, _, _, angulo = campo_rotacion.getSFRotation()
    campo_rotacion.setSFRotation([0, 0, 1, angulo + delta_angulo])

# ---------------------------------------------------------------
# BOTELLA FIJA EN LA MANO
# ---------------------------------------------------------------
def actualizar_botella(nodo_robot, nodo_botella):
    pos = nodo_robot.getField("translation").getSFVec3f()
    x_r, y_r, z_r = pos

    _, _, _, angulo = nodo_robot.getField("rotation").getSFRotation()

    # 🔧 AJUSTA ESTO SI NO QUEDA EXACTO EN LA MANO
    x_local =  0.08
    y_local = -0.20
    z_local = -0.50

    # Convertir a coordenadas globales
    x_global = x_local * math.cos(angulo) - y_local * math.sin(angulo)
    y_global = x_local * math.sin(angulo) + y_local * math.cos(angulo)

    nueva_pos = [
        x_r + x_global,
        y_r + y_global,
        z_r + z_local
    ]

    # Posición
    nodo_botella.getField("translation").setSFVec3f(nueva_pos)

    # Rotación (sigue al robot)
    nodo_botella.getField("rotation").setSFRotation([0, 0, 1, angulo])

    # 🔥 CLAVE: evitar que la física la tumbe
    nodo_botella.resetPhysics()

# ---------------------------------------------------------------
# CONTROLES
# ---------------------------------------------------------------
print("=== Control de teclado ===")
print("↑ / ↓  → Mover adelante / atrás")
print("← / →  → Mover izquierda / derecha")
print("Q / E  → Rotar")
print("==========================")

# ---------------------------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------------------------
while supervisor.step(paso_tiempo) != -1:

    tecla = teclado.getKey()

    if nodo_peaton is not None and tecla != -1:

        if tecla == Keyboard.UP:
            trasladar(nodo_peaton, TAMANO_PASO, 0.0)

        elif tecla == Keyboard.DOWN:
            trasladar(nodo_peaton, -TAMANO_PASO, 0.0)

        elif tecla == Keyboard.LEFT:
            trasladar(nodo_peaton, 0.0, TAMANO_PASO)

        elif tecla == Keyboard.RIGHT:
            trasladar(nodo_peaton, 0.0, -TAMANO_PASO)

        elif tecla == ord('Q'):
            rotar_z(nodo_peaton, PASO_ANGULO)

        elif tecla == ord('E'):
            rotar_z(nodo_peaton, -PASO_ANGULO)

    # 🔥 ACTUALIZAR BOTELLA SIEMPRE
    if nodo_botella is not None and nodo_peaton is not None:
        actualizar_botella(nodo_peaton, nodo_botella)