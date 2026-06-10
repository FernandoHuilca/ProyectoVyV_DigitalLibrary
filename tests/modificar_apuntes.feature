# language: es
# Created by ferna at 6/9/2026



Característica: Modificar apuntes
  Como estudiante de la EPN creador de apuntes
  Quiero modificar mis apuntes publicados en la plataforma
  Para corregir errores o actualizar información relevante

#  Regla: Solo se puede modificar:
#  El título, la descripción, la materia y el semestre.
#  No se puede modificar el tipo de apunte ni el archivo subido.


  Antecedentes: Ana tiene un apunte publicado en el sistema
    Dado que Ana es una estudiante registrada
    Y ella ha publicado previamente el siguiente apunte:
      | tipo_apunte | título          | descripcion                  | materia    | semestre |
      | PDF         | Intro a Testing | Conceptos básicos de pruebas | Testing SW | Segundo  |

#  Regla: Los autores pueden actualizar la información descriptiva de su apunte

  Esquema del escenario: Modificar exitosamente los campos permitidos (Caso Ideal)
    Cuando Ana actualiza su apunte con <titulo>, <descripcion>, <materia> y <semestre>
    Entonces los detalles del apunte deben actualizarse correctamente
    Y el tipo de apunte <tipo_apunte> debe mantenerse
    Ejemplos:
      | titulo              | descripcion                          | materia                   | semestre | tipo_apunte |
      | Pruebas de Software | Guía completa y corregida de testing | Verificación y Validación | Septimo  | PDF         |



#  Regla: Los campos esenciales no pueden quedar vacíos al modificar

    Esquema del escenario: Intentar guardar modificaciones con campos obligatorios vacíos (Caso Alternativo)
      Cuando Ana intenta actualizar su apunte dejando el campo <Campo_Vacio> en blanco
      Entonces la plataforma debe rechazar la modificación
      Y debe mostrarle el mensaje de error: "<Mensaje_Error>"

      Ejemplos:
        | Campo_Vacio | Mensaje_Error                                          |
        | título      | "El título del apunte no puede estar vacío."           |
        | materia     | "Debes especificar a qué materia pertenece el apunte." |






#  Regla: Solo el autor original del apunte tiene permisos de edición
#
#    Escenario: Un estudiante intenta modificar un apunte que no es suyo (Caso Alternativo 3)
#      Dado que Luis es otro estudiante de la plataforma
#      Cuando Luis intenta modificar el apunte "Intro a Testing" creado por Ana
#      Entonces el sistema debe denegar la acción
#      Y debe mostrarle el mensaje "No tienes permisos para editar los apuntes de otros compañeros"





      #  Regla: El tipo de apunte no se puede modificar una vez el documento ha sido publicado

#    Escenario: Intentar cambiar el tipo de apunte de un documento existente (Caso Alternativo 1)
#      Cuando Ana intenta cambiar el "tipo_apunte" de su documento a "Examen"
#      Entonces el sistema debe rechazar este cambio específico
#      Y el documento debe conservar su "tipo_apunte" original como "Resumen"
#      Y Ana debe ser notificada que el tipo de apunte es inmutable