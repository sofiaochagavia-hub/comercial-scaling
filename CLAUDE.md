# Material comercial de Scaling

Página que usan los coaches de Scaling, casi siempre desde el celular, para
saber qué mandar a cada lead y cómo llevar cada reunión. Se publica con GitHub
Pages en <https://sofiaochagavia-hub.github.io/comercial-scaling/>.

**Este repo es público.** No subas nada confidencial: precios internos, datos
de contactos o notas de clientes. Los criterios completos del equipo están en
`CRITERIOS-SCALING.md` del repo privado `sofiaochagavia-hub/scaling-crm`;
si tienes acceso, léelo.

## Quién trabaja aquí

Sofía Ochagavía (Growth Manager) es la dueña del material. Otras personas del
equipo también lo ajustan, sin necesitar aprobación de Sofía: los cambios se
publican directo. Nadie es desarrollador: explica en castellano qué vas a
hacer y por qué. **No borres nada sin permiso explícito de la persona con la
que trabajas**, salvo lo que tú mismo creaste en la misma sesión.

## Qué hay adentro

```
index.html               LA página publicada: las 3 secciones en un solo archivo
_fuente/                 las 3 páginas originales (no se publican: Pages ignora las carpetas con _)
  estrategia.html        sección Estrategia
  guiones.html           sección Reuniones (guiones Sandler por etapa)
  seguimiento.html       sección Seguimiento (mensajes por tipo de lead, CTAs, casos de éxito)
  build.py               une las 3 páginas en index.html (requiere Python 3)
s01.webp … s30.webp      imágenes de las slides
estrategia-comercial/, nuggets-de-venta/   versiones antiguas sueltas, no enlazadas desde index.html
```

## Cómo se hace un cambio

1. `git pull` antes de empezar, para partir de lo último.
2. Cambia la página de `_fuente/` que corresponda y regenera con
   `python _fuente/build.py`. Si no hay Python en el computador, haz el mismo
   cambio en `_fuente/` y en `index.html`, para que no se desincronicen.
3. Revisa con `git diff` que solo cambió lo que querías.
4. Commit con un mensaje que entienda alguien que no programa, y `git push`.
   En 1 o 2 minutos se ve en la página.

Si las dos personas están editando el mismo día, avísense para no pisarse.

**El CRM copia los mensajes de esta página.** Su script (`npm run mensajes` en
`scaling-crm`) lee las clases `.msg-card`, `.channel-badge`, `.msg-card-title`,
`.msg-card-note` y `[data-copy]`. No cambies esa estructura sin revisar el
script. Después de cambiar un mensaje, hay que correr `npm run mensajes` en
el CRM para que lo tome.

## Diseño: simple y sobrio

- Poco color: gris neutro y el azul de la página para enlaces. El color se usa
  solo para lo seleccionado o un enlace.
- Orden de lectura claro, de arriba a abajo.
- Los pasos van como lista numerada que se despliega.
- Sin cajas de colores ni pastillas llamativas.
- Por qué: los coaches lo usan desde el celular y tienen que encontrar rápido
  qué mandar.

## Tono: el cliente es el protagonista

- El foco es el cliente: su bienestar, su crecimiento, sus resultados. Scaling
  es la guía, nunca el protagonista. Siempre con una salida sin presión.
- Nada de "gatillar urgencia". No agobiar: un toque cada 1 a 2 semanas y un
  cierre amable después de dos sin respuesta.
- Regalar algo útil en cada toque y acercarse de a poco.
- Siempre un CTA intermedio (un regalo, el diagnóstico de 3 minutos) y uno
  directo (conversemos).
- Entre reuniones solo se manda algo si la relación se puede enfriar. Si la
  próxima reunión está a menos de 3 semanas, basta el mensaje del mismo día.
- El diagnóstico de 3 minutos va **antes** de la propuesta, nunca después.
- El acuerdo de trabajo va solo si la propuesta se ajustó; si la aceptan tal
  cual, va directo el mail de bienvenida.
- Metodologías: Sandler (ya desarrollado aquí) y StoryBrand (Sofía va a pasar
  el material; no lo apliques de conocimiento general).
