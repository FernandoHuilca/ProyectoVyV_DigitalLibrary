# language: es

Característica: Revisión por pares de apuntes
  Como publicador de apuntes,
  quiero solicitar una revisión por parte de otros estudiantes antes de publicar mi apunte,
  para recibir retroalimentación sobre su calidad académica, corregir posibles errores y asegurar que el material ha sido verificado.

  Escenario: El autor envía un apunte a revisión
    Dado que tengo un apunte en estado "Borrador"
    Cuando selecciono a un estudiante como revisor y envío el apunte a revisión
    Entonces el apunte debe cambiar a estado "En revisión"
    Y debe crearse una solicitud de revisión pendiente para el estudiante seleccionado

  Escenario: El revisor aprueba un apunte y recibe puntos
    Dado que tengo un apunte en estado "En revisión" enviado por otro estudiante
    Cuando apruebo el apunte
    Entonces el estado del apunte debe cambiar a "Aprobado"
    Y mi perfil debe incrementar en 15 puntos de prestigio

  Escenario: El revisor solicita cambios en el apunte
    Dado que tengo un apunte en estado "En revisión" enviado por otro estudiante
    Cuando rechazo el apunte explicando los cambios necesarios
    Entonces el estado del apunte debe volver a "Borrador"

  Escenario: El autor publica el apunte tras ser avalado
    Dado que mi apunte ha sido aprobado por un revisor
    Cuando confirmo la publicación desde mi panel de "Mis apuntes"
    Entonces el apunte debe cambiar a estado "Publicado"
