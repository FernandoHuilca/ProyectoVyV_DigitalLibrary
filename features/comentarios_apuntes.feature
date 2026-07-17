# language: es
Característica: Interaccion con apuntes
  Como un estudiante registrado
  Quiero poder interactuar con los apuntes de mis compañeros
  Para poder expresar mi opinión sobre que apuntes considero de utilidad

  Escenario: Una respuesta a una respuesta de Nivel 2 se aplana automáticamente
    Dado que "UserB" tiene un comentario principal en un apunte
    Y "UserC" escribió una respuesta al comentario de "UserB"
    Cuando "UserD" responde a la respuesta de "UserC"
    Entonces la respuesta de "UserD" se registra bajo el comentario principal de "UserB"

  Escenario: El creador del apunte gana prestigio por un comentario principal de un tercero
    Dado que "AutorA" tiene un apunte "Cálculo I"
    Y "AutorA" tiene inicialmente 10 puntos de prestigio
    Cuando el usuario "UserB" escribe un comentario principal en "Cálculo I"
    Entonces el prestigio de "AutorA" debe ser de 12 puntos

  Escenario: Un usuario gana prestigio cuando responden a su comentario
    Dado que "UserB" tiene un comentario principal en un apunte
    Y "UserB" tiene inicialmente 5 puntos de prestigio
    Cuando el usuario "UserC" responde al comentario de "UserB"
    Entonces el prestigio de "UserB" debe ser de 6 puntos

  Escenario: El creador otorga un corazón a un aporte valioso
    Dado que "UserB" tiene un comentario en el apunte de "AutorA"
    Y "UserB" tiene inicialmente 5 puntos de prestigio
    Cuando "AutorA" reacciona con un corazón al comentario de "UserB"
    Entonces el prestigio de "UserB" debe ser de 10 puntos

  Escenario: El creador del apunte no gana prestigio por auto-comentarse
    Dado que "AutorA" tiene un apunte "Física"
    Y "AutorA" tiene inicialmente 10 puntos de prestigio
    Cuando "AutorA" escribe un comentario principal en su propio apunte "Física"
    Entonces el prestigio de "AutorA" debe mantenerse en 10 puntos

  Escenario: El autor del apunte responde a un comentario sin alterar su propio prestigio
    Dado que "UserB" tiene un comentario principal en el apunte de "AutorA"
    Y "UserB" tiene inicialmente 5 puntos de prestigio
    Y "AutorA" tiene inicialmente 10 puntos de prestigio
    Cuando "AutorA" escribe una respuesta al comentario de "UserB"
    Entonces el prestigio de "UserB" debe incrementarse a 6 puntos
    Y el prestigio de "AutorA" debe mantenerse en 10 puntos

  Escenario: Un usuario edita su comentario para corregir su contenido
    Dado que "UserB" tiene un comentario publicado con el texto "Este apunte es mui bueno"
    Y el comentario no registra ninguna marca de edición
    Y "AutorA" (autor del apunte) tiene inicialmente 12 puntos de prestigio
    Cuando "UserB" edita el texto de su comentario a "Este apunte es muy bueno"
    Entonces el comentario debe actualizar su texto en la base de datos
    Y el comentario debe quedar marcado como editado
    Y el prestigio de "AutorA" debe mantenerse en 12 puntos