# language: es

Característica: Votos de utilidad sobre apuntes y cálculo de prestigio
  Como estudiante de la EPN
  Quiero calificar los apuntes de mis compañeros como Útil o No útil
  Para apoyar el prestigio de los creadores de contenido de la calidad


  Antecedentes:
    Dado que existe un apunte identificado como "AP1" creado por el estudiante "AutorA"
    Y existen los usuarios registrados "UserB", "UserC"


  Escenario: Prohibición de auto-voto
    Cuando el creador "AutorA" intenta calificar su propio apunte "AP1" como "Útil"
    Entonces el sistema deniega la acción indicando que no está permitido el auto-voto
    Y el apunte "AP1" se mantiene con 0 votos


  Esquema del escenario: Matriz de transiciones, alternancia e idempotencia de votos
    Dado que el usuario "UserB" <estado_inicial> el apunte "AP1"
    Cuando "UserB" <accion> sobre el apunte "AP1"
    Entonces el apunte "AP1" debe tener <cant_util> votos "Útil"
    Y el apunte "AP1" debe tener <cant_no_util> votos "No útil"

    Ejemplos:
      | estado_inicial               | accion                  | cant_util | cant_no_util | descripcion                      |
      | no ha calificado             | califica como "Útil"    | 1         | 0            | Primer voto positivo             |
      | no ha calificado             | califica como "No útil" | 0         | 1            | Primer voto negativo             |
      | ha calificado como "Útil"    | califica como "Útil"    | 0         | 0            | Quitar voto por re-clic positivo |
      | ha calificado como "No útil" | califica como "No útil" | 0         | 0            | Quitar voto por re-clic negativo |
      | ha calificado como "Útil"    | califica como "No útil" | 0         | 1            | Cambiar de positivo a negativo   |
      | ha calificado como "No útil" | califica como "Útil"    | 1         | 0            | Cambiar de negativo a positivo   |
      | ha calificado como "Útil"    | retira su calificación  | 0         | 0            | Retirar calificación positiva    |
      | ha calificado como "No útil" | retira su calificación  | 0         | 0            | Retirar calificación negativa    |


  Esquema del escenario: Recálculo de prestigio por cambio de rango del votante

    Dado que el usuario "UserB" tiene el rango de "<rango_inicial>"
    Y ha calificado el apunte "AP1" como "<voto_inicial>"
    Y el prestigio neto acumulado de "AutorA" es de 10 puntos
    Y el usuario "UserB" es promovido al rango de "<rango_final>"
    Cuando "UserB" califica el apunte "AP1" como "<voto_final>"
    Entonces el prestigio neto acumulado de "AutorA" debe ser de <prestigio_final> puntos

    Ejemplos:
      | rango_inicial | voto_inicial | rango_final | voto_final | prestigio_final | descripcion                                     |
      | Prepo         | Útil         | Tecnólogo   | No útil    | 6               | Cambia de positivo a negativo subiendo de rango |
      | Prepo         | No útil      | Ingeniero   | Útil       | 17              | Cambia de negativo a positivo subiendo de rango |
      | Tecnólogo     | Útil         | Ingeniero   | Retirar    | 6               | Retira voto positivo habiendo subido de rango   |