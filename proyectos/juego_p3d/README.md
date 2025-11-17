# Juego 3D Arcade - Panda3D

## Descripción

Juego 3D arcade desarrollado con Panda3D. El jugador avanza automáticamente por una calle infinita donde debe destruir fantasmas en movimiento y barreras 3D rotatorias usando proyectiles. Incluye sistema de power-ups, efectos de sonido, ambiente dinámico y sistema de usuarios con persistencia de puntajes.

## Características Principales

### Mecánicas de Juego

- **Cámara auto-scroll**: Avanza automáticamente a velocidad constante
- **Sistema de apuntado**: Apunta con el mouse en 3D
- **Proyectiles**: Dispara cuadrados con textura personalizada
- **Fantasmas en movimiento**: Destruye sprites animados que se mueven lateral y verticalmente
- **Barreras 3D rotatorias**: Obstáculos hexagonales (6 caras) que rotan continuamente
- **Power-ups dorados**: Cajas rotatorias que otorgan munición extra

### Sistema de Munición y Power-ups

- **Munición inicial**: 10 proyectiles al comenzar
- **Sistema de recarga**: Recoge power-ups dorados para obtener más munición
- **Sin munición**: No puedes disparar hasta recoger un power-up
- **Power-ups**: Aparecen cada 12 segundos, otorgan munición adicional

### Sistema de Puntuación

- **+10 puntos**: Por cada fantasma destruido
- **+5 puntos**: Por cada barrera destruida
- **-10 puntos**: Si chocas con una barrera sin destruirla
- **Game Over**: Cuando los puntos llegan a 0 o menos

### Sistema de Spawn

- **Fantasmas**: Aparecen 2 fantasmas cada 3 segundos en posiciones aleatorias
- **Movimiento**: Cada fantasma se mueve lateralmente (1.5-3.0 unidades) y verticalmente (±0.5 unidades)
- **Barreras 3D**: Aparecen cada 8 segundos, rotan continuamente en el espacio
- **Power-ups**: Aparecen cada 12 segundos, rotan sobre su eje

### Sistema de Colisiones

- Detección precisa usando BitMask32 por capas
- Cooldown de 0.5 segundos para evitar colisiones repetidas
- Fragmentos de explosión sin colisión para permitir disparos continuos
- Validación robusta de objetos antes de procesar colisiones

### Interfaz de Usuario

- **HUD superior**: Título del juego (amarillo), contador de munición (blanco/amarillo), puntuación (azul)
- **Menú de pausa profesional**: Panel con borde azul, título "JUEGO PAUSADO", instrucciones
- **Pantalla Game Over**: Muestra puntuación final y botón de reinicio
- **Sistema de login**: Registro e inicio de sesión con persistencia de usuarios

### Estética Visual y Ambiente

- **Cielo despejado**: Fondo azul claro (0.53, 0.81, 0.98) con sol brillante
- **Nubes animadas**: 8 nubes moviéndose a diferentes velocidades (2-5 unidades/seg)
- **Calle/carretera**: Asfalto gris oscuro con líneas amarillas centrales y bordes blancos
- **Paredes de ladrillo**: Paredes laterales continuas con textura de ladrillo a la vista
- **Sprites de fantasmas**: Textura fantasma.png con transparencia
- **Power-ups dorados**: Cajas con color dorado brillante (1.0, 0.85, 0.0)

### Sistema de Audio

- **Música de fondo**: Loop continuo durante el juego
- **Efectos de sonido**:
  - Disparo de proyectil
  - Ruptura de fantasmas
  - Recolección de power-ups
- **Control de audio**: La música se pausa automáticamente en pausa y game over

## Requisitos del Sistema

- Python 3.11+
- Panda3D 1.10.15
- Pillow 12.0.0

## Instalación y Ejecución

### 1. Crear entorno virtual

```bash
python -m venv venv_new
```

### 2. Activar entorno virtual

**Windows:**

```powershell
.\venv_new\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
source venv_new/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Agregar archivos de audio (requerido)

Coloca los siguientes archivos en la carpeta `sounds/`:

- `disparo.wav` o `disparo.mp3` - Sonido al disparar
- `fantasma_romper.wav` o `fantasma_romper.mp3` - Sonido al romper fantasmas
- `powerup.wav` o `powerup.mp3` - Sonido al recoger power-ups
- `musica.mp3` - Música de fondo del juego

### 5. Ejecutar el juego

```bash
python main.py
```

## Controles

- **Mouse**: Apuntar
- **Click Izquierdo / Espacio**: Disparar proyectil (requiere munición)
- **ESC**: Pausar/Reanudar juego
- **Botón Reiniciar**: Volver a jugar tras Game Over
- **Sistema de Login**: Crear cuenta o iniciar sesión antes de jugar

## Estructura del Proyecto

```
juego_p3d/
├── main.py                 # Punto de entrada, sistema de login y usuarios
├── game.py                 # Lógica principal del juego (~828 líneas)
├── player.py               # Control del jugador (disparo y colisiones)
├── sounds.py               # Sistema de gestión de audio
├── projectile.png          # Textura personalizada para proyectiles
├── fantasma.png            # Textura de sprite para enemigos
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Este archivo
├── entities/
│   ├── player.py           # Sistema de disparo y detección de colisiones
│   ├── projectile.py       # Pool de proyectiles con textura personalizada
│   ├── crystal.py          # Fantasmas con sprites y sistema de movimiento
│   ├── barrier.py          # Barreras 3D rotatorias (6 caras)
│   └── powerup.py          # Power-ups dorados con rotación
├── sounds/                 # Carpeta para archivos de audio (crear manualmente)
│   ├── disparo.wav
│   ├── fantasma_romper.wav
│   ├── powerup.wav
│   └── musica.mp3
└── data/                   # Carpeta de persistencia de datos
    ├── users.csv           # Usuarios registrados (hash SHA-256)
    └── scores.csv          # Puntajes guardados por usuario
```

## Detalles Técnicos

### Sistema de Colisiones

- **Bit 0**: Proyectiles y cristales
- **Bit 1**: Jugador y barreras
- CollisionTraverser con CollisionHandlerEvent
- Eventos: projectile-into-crystal, projectile-into-barrier, player-into-barrier

### Geometría

- **Cristales**: GeomVertexData con GeomTriangles (pirámides de 5 vértices)
- **Proyectiles**: CardMaker con textura PNG personalizada
- **Barreras**: CardMaker de -8 a 8 en X (ancho completo de pantalla, altura de -1 a 1)
- **Obstáculos**: CardMaker con diferentes formas y tamaños

### Pool de Proyectiles

- Máximo 20 proyectiles activos simultáneos
- Reutilización de proyectiles inactivos
- Limpieza automática de proyectiles fuera de pantalla

### Efectos Visuales

- Fragmentos animados al romper fantasmas y barreras con velocidades y direcciones aleatorias
- Transparencia en sprites de fantasmas con `TransparencyAttrib.MAlpha`
- Interpolación suave con `LerpPosInterval` y `LerpHprInterval` para animaciones fluidas
- Barreras 3D se rompen en múltiples fragmentos que vuelan en direcciones laterales
- Sistema de partículas al recoger power-ups

### Sistema de Audio

- **SoundManager**: Gestión centralizada de audio con preload y play
- **Efectos de sonido**: disparo, ruptura de fantasmas, recolección de power-ups
- **Música de fondo**: Loop continuo con control de pause/resume
- **Control de volumen**: Configuración global (0.3 por defecto)
- **Pause automático**: La música se pausa en game over y menú de pausa

### Persistencia de Datos

- **Sistema de usuarios**: Registro con hash SHA-256 de contraseñas
- **Almacenamiento CSV**: `users.csv` para credenciales, `scores.csv` para puntajes
- **Seguridad**: Las contraseñas nunca se almacenan en texto plano

## Personalización

### Cambiar Colores del Ambiente

- **Cielo**: `game.py` línea 73 → `Vec4(0.53, 0.81, 0.98, 1)`
- **Asfalto**: `game.py` línea 85 → `(0.3, 0.3, 0.50)`
- **Líneas amarillas**: `game.py` línea 100 → `(1, 1, 0, 1)`
- **Líneas blancas**: `game.py` línea 106 → `(1, 1, 1, 1)`
- **Paredes de ladrillo**: `game.py` línea 199 → `(0.65, 0.35, 0.25)`
- **Sol**: `game.py` línea 236 → `(1, 0.95, 0.3)`
- **Nubes**: `game.py` línea 254 → `(1, 1, 1, 0.8)`

### Ajustar Dificultad

- **Velocidad de spawn de fantasmas**: `game.py` → modificar tiempo en `spawn_crystals()`
- **Rango de movimiento**: `crystal.py` → ajustar valores `lateral_distance` (1.5-3.0) y `z_offset` (±0.5)
- **Duración de movimiento**: `crystal.py` → modificar `duration` en `start_movement()` (2.0-3.5)
- **Munición inicial**: `game.py` → cambiar `self.ammo = 10`
- **Frecuencia de power-ups**: `game.py` → ajustar tiempo en `spawn_powerups()`
- **Velocidad de cámara**: `game.py` → modificar `self.camera_speed`

### Agregar Archivos de Audio

Coloca los archivos en la carpeta `sounds/` con estos nombres:

- `disparo.wav` o `.mp3` - Se reproduce al disparar
- `fantasma_romper.wav` o `.mp3` - Se reproduce al destruir fantasmas
- `powerup.wav` o `.mp3` - Se reproduce al recoger power-ups
- `musica.mp3` - Música de fondo en loop

El sistema soporta formatos `.wav` y `.mp3`.

## Créditos

- **Engine**: Panda3D 1.10.15
- **Lenguaje**: Python 3.11.9
- **Texturas**: Personalizadas (projectile.png, fantasma.png)
- **Desarrollo**: Proyecto educativo de juego 3D arcade
