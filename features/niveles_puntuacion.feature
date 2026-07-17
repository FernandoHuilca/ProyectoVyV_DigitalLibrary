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


  Esquema del escenario: Ascenso de rango al superar un umbral de puntuación
  Dado un estudiante de rango "<rango_inicial>" y que cuenta con prestigio de <prestigio_inicial> puntos
  Y el siguiente rango "<rango_final>" requiere un mínimo de <umbral> puntos
  Cuando el sistema procesa un incremento de <incremento> puntos de prestigio
  Entonces el sistema actualiza el puntaje acumulado a <prestigio_final> puntos de prestigio
  Y el rango del estudiante se actualiza automáticamente a "<rango_final>"

  Ejemplos:
    | rango_inicial | prestigio_inicial | incremento | prestigio_final | umbral | rango_final |
    | Prepo         | 290               | 10         | 300             | 300    | Tecnólogo   |
    | Tecnólogo     | 690               | 10         | 700             | 700    | Ingeniero   |
    | Ingeniero     | 2995              | 5          | 3000            | 3000   | PHD         |


  Esquema del escenario: Descenso de rango por pérdida de puntos
  Dado un estudiante con el rango "<rango_inicial>" y un prestigio de <prestigio_inicial> puntos
  Cuando el sistema registra una pérdida de <perdida> puntos de prestigio
  Entonces el prestigio acumulado del estudiante es de <prestigio_final> puntos
  Y el rango del estudiante se actualiza automáticamente a "<rango_final>"

  Ejemplos:
    | rango_inicial | prestigio_inicial | perdida | prestigio_final | rango_final |
    | Ingeniero     | 725               | 35      | 690             | Tecnólogo   |
    | Tecnólogo     | 320               | 25      | 295             | Prepo       |
    | PHD           | 3010              | 20      | 2990            | Ingeniero   |

