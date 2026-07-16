# language: es
Característica: Guardado de apuntes
  Como usuario registrado
  Quiero guardar apuntes en una lista personal
  Para volver a ellos fácilmente más adelante sin perder tiempo buscándolos

  Escenario: Registrar un nuevo guardado
    Dado que el usuario no tiene el apunte "X" en su lista de guardados
  Y el apunte "X" se encuentra disponible y es accesible para el usuario
  Cuando el usuario guarda el apunte "X"
  Entonces el sistema registra el apunte "X" en la lista de guardados del usuario
  Y el prestigio del autor del apunte "X" se incrementa en "5" puntos

  Escenario: Quitar un guardado existente
  Dado que el usuario tiene guardado el apunte "X"
  Cuando el usuario quita el apunte "X" de sus guardados
  Entonces el sistema elimina el registro de guardado asociado al usuario
  Y el prestigio del autor del apunte "X" disminuye en "5" puntos

  Escenario: El autor no puede guardar su propio apunte
    Dado que el autor tiene el apunte "Y"
    Cuando el autor intenta guardar el apunte "Y"
    Entonces el sistema impide la acción
