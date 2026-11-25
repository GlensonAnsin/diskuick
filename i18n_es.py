"""Spanish strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("es", "Español", (
    "Panel", "Juegos", "Herramientas", "Ajustes",                                                      # 1-5
    "Mantiene tu unidad activa mientras juegas",
    "Bloqueos recientes", "Estado de la unidad", "Prueba de lag", "Prueba y ajuste automático",
    "Comportamiento", "Apariencia", "Cuándo ejecutar", "Intensidad predeterminada",                    # 10-14
    "Latencia de lectura en vivo",
    "Activo", "En espera", "Apagado", "Error", "Desactivado", "Inactivo", "Iniciando",                 # 16-22
    "En pausa con batería",
    "Elige una unidad en Ajustes", "Añade juegos en la pestaña Juegos",
    "Esperando a que se inicie un juego", "Esperando a que la ventana del juego tenga el foco",
    "Mantenida activa", "Sesiones", "Bloqueos registrados", "Habilitado",                              # 28-31
    "Aún no hay bloqueos registrados.",
    "Cada punto es la lectura más lenta de ese segundo. Los picos por encima de la línea roja son bloqueos: momentos en que la unidad dudó.",
    "Inicia un juego (o elige «Siempre activo») para ver la latencia en vivo.",
    "Esperando datos...",
    "bloqueo", "ahora", "Actualización disponible", "Descargar",                                       # 36-39
    "Detectar juegos instalados", "Buscando...", "Añadir programa en ejecución…",
    "o escribe el nombre de un programa, p. ej. juego.exe",
    "Añadir", "Unidad", "Intensidad", "Predeterminada",                                                # 44-47
    "Aún no hay juegos.\nHaz clic en «Detectar juegos instalados» para encontrarlos automáticamente.",
    "Elige un programa en ejecución", "Abre primero tu juego y luego elígelo aquí.",
    "Buscar...", "No se encontró nada", "Juegos detectados", "No se encontraron juegos nuevos.",       # 51-54
    "Se buscó en Steam, Epic Games y GOG. Aún puedes añadir un juego con «Añadir programa en ejecución» o escribiendo el nombre de su exe.",
    "Elige los juegos para los que mantener activa tu unidad.",
    "El nombre del programa es una suposición: revísalo si un juego no se activa.",
    "Seleccionar todo", "Añadir selección", "Cerrar",                                                  # 58-60
    "Unidad a revisar", "Actualizar", "Reiniciar como administrador", "Leyendo información de la unidad...",
    "Lo que Windows sabe de esta unidad, con consejos en lenguaje sencillo.",
    "Salud", "Temperatura", "Desgaste", "Horas encendida", "n/d",                                      # 66-70
    "{free} GB libres de {total} GB",
    "Mide cuánto tarda la primera lectura tras un periodo de inactividad, con y sin mantenimiento activo, y elige el ajuste más ligero que ayude. Tarda unos 2 minutos. No abras un juego mientras tanto.",
    "Ejecutar ajuste automático", "Preparando…", "Cancelar", "Cancelado.", "La prueba falló",         # 73-77
    "Mantenimiento activo", "ms prom.", "ms p95", "ms máx.", "Ninguno",                                # 78-82
    "El mantenimiento activo elimina los bloqueos por inactividad. Ajuste recomendado: {p}.",
    "No se detectaron bloqueos por inactividad en esta unidad: despierta rápido. Probablemente el mantenimiento activo no ayude aquí.",
    "Esta unidad duda tras estar inactiva, pero el mantenimiento activo no ayudó claramente. La causa puede estar en otro lugar: prueba la Prueba de lag.",
    "Usar {p} como predeterminada", "Guardado.",                                                       # 86-87
    "Cambia a tu juego justo después de pulsar Iniciar. A los 10 segundos Diskuick observa tu disco, CPU y memoria reales durante 30 segundos y te dice qué parece ir mal.",
    "Iniciar prueba de lag", "Empieza en {s} s: cambia a tu juego ahora…", "Midiendo… sigue jugando",
    "Solo orientativo: la red no se mide.",
    "Solo al jugar", "Siempre activo",                                                                 # 93-94
    "Se inicia automáticamente al abrir uno de tus juegos y se detiene al cerrarlo. Añade juegos en la pestaña Juegos.",
    "Funciona todo el tiempo que Diskuick está abierto. Es simple, pero mantiene la unidad ocupada incluso en reposo.",
    "Unidades a mantener activas",
    "Cuánto estimular la unidad. Los juegos pueden anular esto.",
    "Ligera", "Equilibrada", "Intensa",                                                                # 99-101
    "Lecturas aleatorias diminutas, unas 10 por segundo. Menor sobrecarga: prueba esta primero.",
    "Lecturas secuenciales ligeras, unas 20 por segundo. Para unidades que necesitan algo más.",
    "Lecturas continuas. Efecto más fuerte, pero la unidad siempre está ocupada.",
    "Segundos entre lecturas (avanzado)", "predeterminado",                                            # 105-106
    "Introduce un número positivo, o déjalo vacío para el valor predeterminado.",
    "Pausar con batería", "Portátiles: no mantiene la unidad ocupada cuando está desenchufado.",
    "Solo con el juego enfocado", "Se pausa al salir del juego con Alt+Tab.",
    "Avisar al iniciar un juego", "Una pequeña notificación en la bandeja.",
    "Iniciar con Windows", "Se ejecuta en silencio en la bandeja al iniciar sesión.",
    "Tema", "Sistema", "Oscuro", "Tema claro", "Idioma",                                               # 116-120
    "Buscar actualizaciones",
    "Solo se contacta con el nombre del repositorio; no se envía nada sobre ti.",
    "La búsqueda de actualizaciones está desactivada hasta que se defina un repositorio de versiones.",
    "Abrir carpeta de datos", "Abrir registro de bloqueos",
    "La intensidad inteligente está activada: elige el nivel por ti. Desactívala para elegir uno tú mismo.",
    "Inteligente",                                                                                     # 127
    "Reiniciar como administrador para un análisis rápido",
    "Muestra qué ocupa espacio, de mayor a menor. Aquí no se cambia ni se borra nada. Como administrador lee directamente la tabla de archivos de la unidad (como WizTree) y tarda segundos; si no, lee las carpetas una a una, lo que puede tardar uno o dos minutos.",
    "Tardó {s} s.", "Renombrar juego", "Nombre a mostrar para",                                         # 130-132
    "Superposición de latencia",
    "Una pequeña lectura en vivo en una esquina de la pantalla mientras la unidad se mantiene activa (hay un juego en ejecución o «Siempre activo»). Es una ventana aparte que nunca toca el juego y se muestra sobre juegos en ventana y sin bordes. No puede mostrarse sobre pantalla completa exclusiva (por ejemplo, Battlefield 3): cambia ese juego a sin bordes o en ventana.",
    "Mostrar superposición mientras corre un juego", "Posición", "Vista previa",                       # 135-137
    "Arriba a la izquierda", "Arriba a la derecha", "Abajo a la izquierda", "Abajo a la derecha",
    "Actualizar ahora", "Descargando… {p}%", "Error al actualizar", "Reintentar", "Buscar ahora",      # 142-146
    "Comprobando…", "Estás al día.", "No se pudo buscar actualizaciones.", "Actualización disponible: {v}",
    "Abrir Diskuick", "Salir", "Manteniendo activa la unidad {d}:",                                    # 151-153
    "No se pudo cambiar el inicio con Windows",
    "Últimas sesiones", "¿Fue la unidad? Un resumen de tus últimas sesiones de juego.",
    "Aún no hay sesiones registradas. Aparece un informe cuando se cierra un juego.",
    "Peor lectura", "bloqueos", "pico", "ping",                                                        # 158-161
    "Marcas de lag",
    "Pulsa Ctrl+Alt+L (o usa el menú de la bandeja) en el momento en que un juego vaya con lag. Diskuick guarda lo que hacía el PC en ese instante.",
    "Aún no se ha marcado ningún lag.", "Marcar lag ahora", "Lag marcado", "Sesión terminada",         # 162-167
    "Cerrado para liberar recursos", "Intensidad inteligente",
    "Empieza en Ligera y sube solo mientras la unidad sigue bloqueándose; luego baja cuando todo va bien. Ignora la elección de arriba (el ajuste propio de un juego sigue mandando).",
    "Alertas de unidad", "Avísame cuando la unidad de juegos esté casi llena o deje de estar sana.",   # 171-172
    "Atajos de teclado",
    "Ctrl+Alt+L marca un momento de lag. Ctrl+Alt+O muestra u oculta la superposición.",
    "Mostrar superposición mientras la unidad se mantiene activa",
    "Mostrar también la carga de CPU y GPU", "Mostrar también los FPS",                                # 176-177
    "Requiere PresentMon.exe junto a Diskuick.exe y que Diskuick se ejecute como administrador.",
    "Comprobación de red (opcional)",
    "Comprueba si tu conexión a internet podría ser la causa del lag. Escribe 1.1.1.1 para comprobar tu conexión general, o la dirección de un servidor en el que juegues (el :puerto es opcional y por defecto es 443). Durante una Prueba de lag (y cuando marcas un lag) Diskuick mide el ping (cuánto tarda el servidor en responder) y la pérdida de paquetes (respuestas que nunca llegan), para que distingas un problema de red de uno de la unidad. Solo se abre una conexión normal, unas pocas veces por segundo, y no se envía nada sobre ti. Déjalo vacío para mantenerlo desactivado.",
    "Host", "Introduce un nombre de host o una dirección, opcionalmente con :puerto.",
    "Modo juego (opcional)",
    "Cuando se inicia uno de tus juegos, pide amablemente a estos programas que se cierren (aún pueden pedirte guardar) y los reabre cuando el juego termina. No se fuerza el cierre de nada.",
    "No se eligió ningún programa.", "Quitar", "Ese programa está protegido y no se puede cerrar.",    # 185-187
    "Reabrirlos después", "Disco", "Unidad a analizar", "Analizar", "Detener", "Deteniendo...", "Subir", # 188-194
    "Nombre", "Tamaño", "Archivos", "% del padre", "Abrir en el Explorador", "Abrir esta carpeta aquí", # 195-200
    "Analizador de espacio en disco",
    "Muestra qué ocupa espacio, de mayor a menor. Lee las carpetas una a una, así que una unidad grande tarda uno o dos minutos. Aquí no se cambia ni se borra nada.",
    "Pulsa Analizar para empezar.", "Analiza una unidad para ver su mapa aquí.",                        # 203-204
    "Analizando {drive}: ...", "Analizando {drive}: {files} archivos, {size} hasta ahora",
    "Se encontraron {size} en {files} archivos y {folders} carpetas.", "Unidad usada: {used}.",
    "Detenido antes de tiempo, así que es parcial.",
    "Algunas carpetas están protegidas; ejecuta como administrador para incluirlas.",
    "Tipos de archivo", "Qué tipos de archivo ocupan más espacio en esta unidad.",                    # 211-212
    "Limpieza de disco",
    "Elimina solo restos seguros y regenerables: archivos temporales, cachés e informes de fallos. Tus propios archivos nunca se tocan. Marca lo que quieras, revisa los tamaños y limpia.",
    "Comprobar tamaños", "Comprobando tamaños...", "Limpiar selección", "Limpiando...",               # 215-218
    "Marca al menos un elemento primero.", "Los elementos marcados liberarían unos {size}.",
    "La Papelera de reciclaje se vacía de forma permanente.",
    "Se eliminarán unos {size} de:\n\n{names}{note}\n\n¿Continuar?",
    "Se liberaron {size} ({files} archivos). Se omitieron los elementos en uso.",
    "Archivos temporales", "Dejados por programas en tu carpeta Temp.",                               # 224-225
    "Archivos temporales de Windows", "La carpeta Temp propia de Windows. Ejecuta como administrador para borrarla entera.",
    "Caché de miniaturas", "El Explorador reconstruye las vistas previas de imágenes cuando hace falta.",
    "Volcados de fallos e informes de errores", "Archivos de diagnóstico de programas que fallaron.",
    "Cachés de navegadores", "Cachés de Chrome, Edge y Brave. Los sitios cargan un poco más lento una vez.",
    "Cachés de shaders", "Cachés de shaders de la GPU. Los juegos pueden dar tirones al iniciarse la próxima vez mientras se reconstruyen.",
    "Papelera de reciclaje", "Elimina de forma permanente lo que hay en la Papelera de reciclaje.",
    "Mover a la Papelera de reciclaje", "carpeta", "archivo",                                          # 238-240
    "¿Mover esta {kind} a la Papelera de reciclaje?\n\n{path}\n{size}\n\nPuedes restaurarla desde la Papelera de reciclaje.",
    "Moviendo a la Papelera de reciclaje...",
    "No se pudo mover a la Papelera de reciclaje (en uso, protegido o cancelado).",
    "Se movieron {size} a la Papelera de reciclaje. Analiza de nuevo para actualizar los tipos de archivo.",
    "Análisis rápido (tabla de archivos NTFS).",
    "Ejecuta Diskuick como administrador para un análisis mucho más rápido.",
    "Carpetas", "Libre",                                                                           # 246-247
    "p. ej. 1.1.1.1",
))
