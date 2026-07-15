# language: es
# Created by GregorySD at 09/06/2026
Característica: Calificar comentarios
  Como un estudiante que leyó algún comentario
  Quiero calificar la opinión
  Para que otros alumnos sepan los comentarios más útiles

  Antecedentes:
    Dado que Pepe es un estudiante autenticado
    Y existe un comentario en el apunte de Termodinámica

  Esquema del escenario: Calificar un comentario por primera vez
    Dado que Pepe no ha calificado ese comentario anteriormente
    Cuando marca el comentario como <tipo_comentario>
    Entonces el contador de <tipo_comentario> del comentario aumenta en 1
    Ejemplos:
      | tipo_comentario |
      | util            |
      | no util         |

  Esquema del escenario: Cambiar la calificación de un comentario
    Dado que Pepe ya marcó el comentario como <tipo_comentario>
    Cuando marca el mismo comentario como <otro_tipo_comentario>
    Entonces el contador de <tipo_comentario> disminuye en 1
    Y el contador de <otro_tipo_comentario> aumenta en 1
    Ejemplos:
      | tipo_comentario | otro_tipo_comentario |
      | util            | no util              |
      | no util         | util                  |

  Esquema del escenario: Eliminar la calificación de un comentario
    Dado que Pepe ya marcó el comentario del otro estudiante como <tipo_comentario>
    Cuando vuelve a pulsar el botón <tipo_comentario>
    Entonces el contador de <tipo_comentario> disminuye en 1
    Ejemplos:
      | tipo_comentario |
      | util            |
      | no util         |