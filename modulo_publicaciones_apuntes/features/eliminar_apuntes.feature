# language: es
# Created by Juan at 9/6/2026
Característica: Eliminar apuntes
  Como estudiante de la EPN
  Quiero eliminar los apuntes que he publicado
  Para mantener el contenido de calidad en mi perfil

  #    Y mi score de reputación debe disminuir en 50 puntos
  #    Incluir un puntaje al perfil sumando los puntos de las publicaciones?

  Escenario: Eliminar un apunte propio de forma exitosa
    Dado Eliceo es un estudiante registrado
    Y tiene un apunte publicado titulado "Álgebra Lineal - Resumen"
    Cuando solicito eliminar el apunte "Álgebra Lineal - Resumen"
    Y confirmo la acción
    Entonces el apunte debe ser eliminado exitosamente del repositorio

    Escenario: Cancelar el proceso de eliminación de un apunte
    Dado que tengo un apunte publicado titulado "Cálculo en Varias Variables"
    Cuando solicito eliminar el apunte "Cálculo en Varias Variables"
    Y cancela la eliminación
    Entonces el apunte "Cálculo en Varias Variables" no debe eliminarse
    Y debe seguir en el repositorio
