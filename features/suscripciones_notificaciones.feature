# language: es
Característica: Suscripción y Notificaciones entre Publicador y Consumidor

  Escenario: El consumidor se suscribe a un publicador por primera vez
    Dado que existe un estudiante consumidor autenticado "Pepe"
    Y existe el perfil público de la publicadora "Ana"
    Y "Pepe" no está suscrito a "Ana"
    Cuando "Pepe" se suscribe al perfil de "Ana"
    Entonces "Pepe" debe figurar en la lista de suscriptores de "Ana"
    Y el contador de suscriptores de "Ana" debe incrementarse en 1

  Escenario: El consumidor cancela su suscripción
    Dado que existe un estudiante consumidor autenticado "Pepe"
    Y "Pepe" está suscrito a la publicadora "Ana"
    Cuando "Pepe" cancela su suscripción al perfil de "Ana"
    Entonces "Pepe" ya no debe figurar en la lista de suscriptores de "Ana"
    Y el contador de suscriptores de "Ana" debe disminuir en 1

  Escenario: El consumidor recibe notificación cuando un publicador suscrito publica nuevo apunte
    Dado que el consumidor "Pepe" está suscrito a la publicadora "Ana"
    Cuando "Ana" publica un nuevo apunte titulado "Termodinámica Básica"
    Entonces "Pepe" debe recibir una notificación en la plataforma
    Y la notificación debe contener el texto "Ana ha publicado un nuevo apunte: Termodinámica Básica"
    Y la notificación debe incluir el enlace directo al apunte

  Escenario: El publicador recibe notificación cuando su apunte es calificado como útil
    Dado que la publicadora "Ana" tiene publicado un apunte de "Termodinámica"
    Y el estudiante "Pepe" no es el autor del apunte
    Cuando "Pepe" da like útil al apunte "Termodinámica"
    Entonces "Ana" debe recibir una notificación en la plataforma
    Y la notificación debe indicar que su apunte "Termodinámica" alcanzó los 1 likes

  Escenario: El publicador recibe notificación al alcanzar el hito de 10 likes
    Dado que la publicadora "Ana" tiene publicado un apunte de "Termodinámica"
    Y el apunte de "Termodinámica" tiene 9 likes útiles
    Cuando "Pepe" da like útil al apunte "Termodinámica"
    Entonces "Ana" debe recibir una notificación en la plataforma
    Y la notificación debe indicar que su apunte "Termodinámica" alcanzó los 10 likes

  Escenario: El publicador recibe notificación cuando su apunte se guarda en biblioteca
    Dado que la publicadora "Ana" tiene publicado un apunte de "Termodinámica"
    Cuando el estudiante "Pepe" guarda el apunte "Termodinámica" en su biblioteca
    Entonces "Ana" debe recibir una notificación en la plataforma
    Y la notificación debe indicar que su apunte "Termodinámica" fue guardado en biblioteca

  Escenario: El consumidor no recibe notificación de publicadores a los que no está suscrito
    Dado que el consumidor "Pepe" no está suscrito al publicador "Carlos"
    Cuando "Carlos" publica un nuevo apunte titulado "Álgebra Lineal"
    Entonces "Pepe" no debe recibir ninguna notificación de la plataforma

  Esquema del escenario: Puntos de prestigio ganados al alcanzar hitos de suscripciones
    Dado que la publicadora "Ana" tiene <suscriptores_previos> suscriptores y "<puntos_iniciales>" puntos de prestigio
    Cuando un nuevo estudiante se suscribe al perfil de "Ana"
    Entonces "Ana" debe tener "<suscriptores_finales>" suscriptores
    Y sus puntos de prestigio deben incrementarse en <puntos> puntos
    Y su total de puntos de prestigio debe ser "<puntos_totales>"

    Ejemplos:
      | suscriptores_previos | puntos_iniciales | suscriptores_finales | puntos | puntos_totales |
      | 0                    | 100              | 1                    | 5      | 105            |
      | 9                    | 105              | 10                   | 30     | 135            |
      | 49                   | 135              | 50                   | 60     | 195            |
      | 99                   | 195              | 100                  | 120    | 315            |


