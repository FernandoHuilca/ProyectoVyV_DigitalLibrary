# Created by sebas at 9/6/2026
  # language: es
Característica: Comentar apuntes
  Como estudiante de la EPN
  Quiero publicar, editar y eliminar comentarios en los apuntes
  Para dar retroalimentación y contribuir a la evaluación del contenido

  Antecedentes:
    Dado un estudiante que se encuentra autenticado en el sistema

Escenario: Publicar un comentario exitosamente
Dado un estudiante que se encuentra visualizando un apunte publicado
Cuando escribe un comentario válido
Y selecciona la opción "Publicar comentario"
Entonces el sistema registra el comentario

Escenario: Intentar publicar un comentario vacío
Dado un estudiante que se encuentra visualizando un apunte publicado
Cuando selecciona la opción "Publicar comentario" sin ingresar contenido
Entonces el sistema impide la publicación del comentario


Escenario: Editar un comentario propio
Dado un estudiante que se encuentra visualizando un apunte publicado
Y previamente publicó un comentario en tal apunte
Cuando modifica el contenido del comentario
Y selecciona la opción "Guardar cambios"
Entonces el sistema actualiza el comentario

Escenario: Intentar editar un comentario de otro estudiante
Dado un estudiante que se encuentra visualizando un apunte publicado
Y existe un comentario publicado por otro estudiante
Cuando intenta editar dicho comentario
Entonces el sistema impide la acción

Escenario: Eliminar un comentario propio
Dado un estudiante que se encuentra visualizando un apunte publicado
Y previamente publicó un comentario en un apunte
Cuando selecciona la opción "Eliminar comentario" y confirma la acción
Entonces el sistema elimina el comentario


Escenario: Intentar eliminar un comentario de otro estudiante
Dado un estudiante que se encuentra visualizando un apunte publicado
Y existe un comentario publicado por otro estudiante
Cuando intenta eliminar dicho comentario
Entonces el sistema impide la acción