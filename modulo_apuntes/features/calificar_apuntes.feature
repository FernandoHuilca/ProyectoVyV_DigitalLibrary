# language: es
# Created by GregorySD at 09/06/2026
Característica: Calificar apuntes
  Como un estudiante que leyó un apunte
  Quiero calificar el material
  Para que los otros alumnos sepan su utilidad

  Antecedentes:
    Dado que Pepe es un estudiante autenticado
    Dado que existe un apunte de Termodinámica subido

  Esquema del escenario: Calificar un apunte por primera vez
    Dado que Pepe no ha calificado ese apunte anteriormente
    Cuando Pepe le asigna una puntuación de <calificacion_dada> sobre <calificacion_maxima>
    Entonces su calificación de <calificacion_dada> queda registrada en el apunte
    Y la puntuación promedio del apunte se actualiza incluyendo su voto
    Y Pepe mira su calificación
    Ejemplos:
      | calificacion_dada | calificacion_maxima |
      | 4                 | 5                   |
      | 3                 | 5                   |

  Esquema del escenario: Modificar una calificación existente
    Dado que Pepe ya calificó el apunte de Termodinámica con <calificacion_dada> sobre <calificacion_maxima>
    Cuando Pepe cambia su calificación a <nueva_calificacion> sobre <calificacion_maxima>
    Entonces su calificación anterior de <calificacion_dada> es reemplazada por <nueva_calificacion>
    Y la puntuación promedio del apunte se actualiza con el nuevo valor
    Y Pepe mira su nueva calificación de <nueva_calificacion> en la interfaz
    Ejemplos:
      | calificacion_dada | nueva_calificacion | calificacion_maxima |
      | 4                 | 5                  | 5                   |
      | 3                 | 2                  | 5                   |

  Esquema del escenario: Eliminar una calificación confirmando la acción
    Dado que Pepe ya calificó el apunte de Termodinámica con <calificacion_dada> sobre <calificacion_maxima>
    Cuando solicita eliminar su calificación
    Y confirma la eliminación
    Entonces su calificación es removida del apunte
    Y la puntuación promedio se actualiza sin su voto
    Y Pepe ya no mira ninguna calificación suya en el apunte
    Ejemplos:
      | calificacion_dada | calificacion_maxima |
      | 4                 | 5                   |
      | 3                 | 5                   |

  Esquema del escenario: Cancelar la eliminación de una calificación
    Dado que Pepe ya calificó el apunte de Termodinámica con <calificacion_dada> sobre <calificacion_maxima>
    Cuando solicita eliminar su calificación
    Y cancela la eliminación
    Entonces su calificación de <calificacion_dada> permanece registrada sin cambios
    Y la puntuación promedio del apunte no cambia
    Ejemplos:
      | calificacion_dada | calificacion_maxima |
      | 4                 | 5                   |
      | 3                 | 5                   |
