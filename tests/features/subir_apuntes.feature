# language: es
# Created by ferna at 6/9/2026



Característica: Subir apuntes
  Como estudiante de la EPN
  Quiero publicar mis apuntes en la plataforma
  Para destacar mi perfil académico compartiendo mi conocimiento


  Esquema del escenario: : Subir un apunte exitosamente
    Dado que existe un estudiante registrado en la plataforma
    #Y que haya iniciado sesión en su cuenta
    Cuando el estudiante sube un apunte de tipo <tipo_apunte> con el título <título>, la descripcion <descripcion>, materia <materia> y semestre <semestre>
    Entonces el sistema registra el apunte en la plataforma
    Y el sistema debe notificar al estudiante que su apunte ha sido publicado exitosamente con el mensaje <mensaje>
    # poner periodos académicos? 2026-A?
    Ejemplos:
      | tipo_apunte | título             | descripcion                                | materia   | semestre | mensaje                           |
      | PDF         | Apuntes de Cálculo | Este apunte lo hice con mucho carino       | Cálculo I | Segundo  | "¡Apunte publicado exitosamente!" |
      | markdown    | Apuntes de Física  | Aqui podras encontrar contenido importante | Física II | Tercero  | "¡Apunte publicado exitosamente!" |


  Esquema del escenario: Intentar subir un apunte con un formato no permitido
    Dado que existe un estudiante registrado en la plataforma
    Cuando él intenta subir un archivo con el formato <Formato>
    Entonces el sistema debe rechazar la publicación
    Y debe mostrarle el mensaje de informativo de error: <Mensaje de Error>

    Ejemplos:
      | Formato | Mensaje de Error                                          |
      | .exe    | "Formato no permitido. Por favor sube un PDF o markdown." |
      | .bat    | "Formato no permitido. Por favor sube un PDF o markdown." |
      #| .mp4    | "El archivo es muy pesado o el formato es incorrecto."    | sería otro escenario para el peso?

  # Escenario sobre campos obligatorios vacíos al subir un apunte

  Esquema del escenario: Intentar subir apuntes con campos obligatorios vacíos (Caso Alternativo)
    Dado que existe un estudiante registrado en la plataforma
    Cuando intenta subir su apunte dejando el campo <Campo_Vacio> en blanco
    Entonces la plataforma debe rechazar el apunte
    Y debe mostrarle el mensaje de error: "<Mensaje_Error>"

    Ejemplos:
      | Campo_Vacio | Mensaje_Error                                          |
      | título      | "El título del apunte no puede estar vacío."           |
      | materia     | "Debes especificar a qué materia pertenece el apunte." |