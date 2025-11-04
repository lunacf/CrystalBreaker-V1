# Smash Hit Style Game - Panda3D

## Descripción
Juego 3D estilo Smash Hit desarrollado con Panda3D. El jugador avanza automáticamente por un túnel infinito donde debe destruir cristales triangulares y barreras rectangulares tipo peaje usando proyectiles con textura personalizada.

## Características Principales

### Mecánicas de Juego
- **Cámara auto-scroll**: Avanza automáticamente a velocidad constante
- **Sistema de apuntado**: Apunta con el mouse en 3D
- **Proyectiles**: Dispara cuadrados con textura personalizada (Boca shield)
- **Cristales triangulares**: Destruye pirámides de cristal para ganar puntos
- **Barreras tipo peaje**: Obstáculos rectangulares que cruzan toda la pantalla horizontalmente

### Sistema de Puntuación
- **+10 puntos**: Por cada cristal destruido
- **+5 puntos**: Por cada barrera destruida
- **-10 puntos**: Si chocas con una barrera sin destruirla
- **Game Over**: Cuando los puntos llegan a 0 o menos

### Sistema de Spawn
- **Cristales**: Aparecen 2 cristales cada 3 segundos
- **Barreras**: Aparecen cada 8 segundos (tipo peaje, cruzan toda la pantalla)
- **Obstáculos decorativos**: Columnas, vigas, arcos y pilares aleatorios

### Sistema de Colisiones
- Detección precisa usando BitMask32
- Cooldown de 0.5 segundos para evitar colisiones repetidas
- Validación de objetos antes de procesar colisiones
- Efectos de ruptura con fragmentos animados

### Interfaz de Usuario
- **HUD superior**: Título del juego (amarillo), contador de cristales (verde), puntuación (azul)
- **Menú de pausa**: Presiona ESC para pausar (fondo azul, centrado)
- **Pantalla Game Over**: Muestra puntuación final y botón de reinicio

### Estética Visual
- Paleta de colores gris/blanco estilo Smash Hit
- Fondo gris claro (0.85, 0.88, 0.92)
- Paredes laterales y techo grises
- Cristales con efecto de transparencia
- Barreras grises tipo peaje (cubren todo el ancho de pantalla)

## Requisitos
- Python 3.11+
- Panda3D 1.10.15
- Pillow 12.0.0

## Instalación y Ejecución

### 1. Crear entorno virtual
```
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

### 4. Ejecutar el juego
```bash
python main.py
```

## Controles
- **Mouse**: Apuntar
- **Click Izquierdo / Espacio**: Disparar proyectil
- **ESC**: Pausar/Reanudar juego
- **Botón Reiniciar**: Volver a jugar tras Game Over

## Estructura del Proyecto
```
juego_p3d/
 main.py                 # Punto de entrada de la aplicación
 game.py                 # Lógica principal del juego (455 líneas)
 player.py               # Control del jugador (disparo y colisiones)
 menu.py                 # Menú principal y pantalla de título
 projectile.png          # Textura personalizada para proyectiles
 requirements.txt        # Dependencias del proyecto
 README.md              # Este archivo
 entities/
     player.py          # Sistema de disparo y detección de colisiones con barreras
     projectile.py      # Pool de proyectiles con textura personalizada
     crystal.py         # Cristales triangulares (pirámides de 5 vértices)
     obstacle.py        # Obstáculos decorativos (columnas, vigas, arcos)
     barrier.py         # Barreras destructibles tipo peaje
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
- Fragmentos animados al romper cristales y barreras
- Transparencia en cristales
- Interpolación suave con LerpPosInterval
- Velocidades aleatorias para fragmentos
- Barreras se rompen en 4 fragmentos que vuelan en direcciones laterales

## Créditos
- Engine: Panda3D
- Textura de proyectil: Personalizada (Boca Juniors shield)
- Desarrollo: Fines educativos 
