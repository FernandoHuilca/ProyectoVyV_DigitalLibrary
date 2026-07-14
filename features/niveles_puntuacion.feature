# Created by sebas at 22/6/2026
  # language: es
Característica: Rangos o niveles de reputación por puntos alcanzados
  Como publicador de Notable
  Quiero acumular puntos de prestigio
  Para ascender de rango y demostrar a la comunidad la calidad y confiabilidad de mi contenido.

  Escenario: Asignación automática del rango inicial por defecto
  Dado que un estudiante se registra por primera vez
  Cuando se cree la cuenta
  Entonces su puntaje de prestigio es 0
  Y  el sistema registra en la cuenta el rango de "Prepo"

  Escenario: Ascenso de rango al superar un umbral de puntuación
  Dado un estudiante de rango “Prepo” y que cuenta con prestigio de 290 puntos
  Y el umbral establecido para el siguiente rango de "Tecnólogo" es de 300 puntos
  Cuando el sistema procese un incremento de 10 puntos de prestigio
  Entonces el sistema actualiza el puntaje acumulado a 300 puntos de prestigio
  Y el rango se actualiza automáticamente a "Tecnólogo".

  Escenario: Descenso de rango por pérdida de puntos
  Dado que un estudiante posee el rango "Ingeniero" con un puntaje exacto de 725 puntos
  Cuando el sistema registra la eliminación de un apunte con 35 puntos de prestigio
  Entonces el sistema disminuye el puntaje total del perfil a 690 puntos de prestigio
  Y el sistema degrada automáticamente el rango del estudiante a "Tecnologo".