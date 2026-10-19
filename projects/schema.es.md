[English](schema.en.md) · **Español**

# Metadatos de proyectos

[Portafolio](../README.es.md)

`projects/projects.yaml` es la fuente de verdad de los metadatos. Los README en inglés y en español la repiten para que GitHub muestre un índice legible. Un sitio futuro debe leer el YAML. La forma preferida de ese sitio es un sitio estático con Astro. Este repositorio no contiene ese sitio.

## Fuente de verdad

Primero se cambia el YAML, después los dos README y, si una herramienta pasó de "visto en un repositorio privado" a "aún no hay laboratorio publicado" o al revés, las tablas del stack. El cambio no está listo hasta que el validador termina bien.

```bash
python3 scripts/validate_portfolio.py
python3 scripts/validate_portfolio.py --check-links
```

`--check-links` pide cada URL de GitHub verificada. Hay que usarlo cuando se agrega o se cambia una URL. El comando estructural alcanza para un cambio de redacción que no toca URLs.

## Campos

| Campo | Obligatorio | Regla |
| --- | --- | --- |
| `id` | Sí | Dos dígitos, único, clave de la tabla. Ejemplo: `"01"`. |
| `slug` | Sí | Solo el nombre del repositorio, como `floci-cloud-foundation`. Único. |
| `name.en`, `name.es` | Sí | Nombres visibles. Deben ser distintos. |
| `description.en`, `description.es` | Sí | Una oración para la tabla de la hoja de ruta. Deben ser distintas. La fila del README debe contener esta oración de forma exacta. |
| `technologies` | Sí | Nombres del alcance de aprendizaje. La fila de la hoja de ruta debe listarlos. Un laboratorio publicado puede implementar solo una parte de la lista. |
| `difficulty` | Sí | `foundational`, `intermediate` o `advanced`. Etiqueta de secuencia, no una puntuación. |
| `status` | Sí | Una de las claves de estado de abajo. |
| `url` | Sí, anulable | `https://github.com/<owner>/<slug>` o `null`. |
| `url_verified` | Sí | `true` solo después de abrir la URL y comprobar que resuelve. Si es `false`, `url` debe ser `null`. |
| `documentation` | Sí | Lista de `{label.en, label.es, url}`. Vacía si no hay nada comprobado. Cada URL debe vivir bajo la URL del proyecto. |
| `demo` | Sí, anulable | URL pública de demo, o `null`. No corresponde poner aquí una URL de localhost. |
| `featured` | Sí | `true` solo con evidencia de implementación y una decisión consciente de destacarlo. |
| `repository_note` | No | `{en, es}` o `null`. Los dos README deben contener el texto de forma exacta. Sirve para un matiz que la tabla no puede decir, como una herramienta listada que no está en el Terraform publicado. |

`schema_version` es `1`. Las etiquetas de estado y de dificultad viven junto a sus claves para que un renderizador no invente traducciones.

## Valores de estado

| Clave | English | Español |
| --- | --- | --- |
| `planned` | Planned | Planificado |
| `in_progress` | In progress | En progreso |
| `implemented_learning_pending` | Implemented — learning/reconstruction pending | Implementado — reconstrucción y validación del aprendizaje pendientes |
| `completed` | Completed | Completado |
| `archived` | Archived | Archivado |

Hay que usar `implemented_learning_pending` cuando un repositorio contiene implementación y la reconstrucción manual de la [metodología de aprendizaje](../docs/learning-methodology.es.md) no está registrada como hecha. Los proyectos 01 y 02 están en ese estado. No hay que usar `completed` para decir "el repositorio existe".

## Valores de dificultad

| Clave | English | Español |
| --- | --- | --- |
| `foundational` | Foundational | Fundacional |
| `intermediate` | Intermediate | Intermedio |
| `advanced` | Advanced | Avanzado |

## Registrar un proyecto

1. Agregar un objeto en `projects` dentro de `projects/projects.yaml`, con los dos idiomas completos.
2. Dejar `status: planned`, `url: null`, `url_verified: false`, `featured: false` y `documentation: []` hasta que haya evidencia.
3. Agregar una fila de la hoja de ruta en `README.md` y la fila equivalente en `README.es.md`. La fila debe contener el id, el nombre y la descripción de ese idioma, la etiqueta de dificultad, la etiqueta de estado y el slug.
4. Si el proyecto introduce una herramienta, agregar una fila en los dos archivos del stack. Una herramienta sin evidencia publicada usa `Aún no hay laboratorio publicado` y permanece en `MUST_NOT_CLAIM` dentro de `scripts/validate_portfolio.py`.
5. Agregar el mismo alcance en [roadmap.en.md](../docs/roadmap.en.md) y [roadmap.es.md](../docs/roadmap.es.md).
6. Ejecutar el validador.

No hay que crear la aplicación dentro de este repositorio. El laboratorio tiene su propio repositorio.

## Actualizar el progreso

Cambiar `status` en el YAML y después reemplazar la celda de estado en las dos filas del README. Movimientos permitidos:

| Desde | Hacia | Evidencia necesaria |
| --- | --- | --- |
| `planned` | `in_progress` | Existe un repositorio y el trabajo empezó. Hay que registrar la URL verificada en el mismo cambio. |
| `in_progress` o `planned` | `implemented_learning_pending` | El repositorio contiene la implementación. `repository_note` dice qué hay. No afirma que el camino manual esté hecho. |
| `implemented_learning_pending` | `completed` | El repositorio del proyecto registra la reconstrucción manual, y este índice enlaza ese registro. |
| cualquiera | `archived` | El proyecto sale del camino activo. `repository_note` dice por qué. |

No hay que inventar un porcentaje, un conteo de pruebas ni una fecha de cierre. Si la única evidencia es "una sesión anterior dijo que pasó", se mantiene el estado más conservador.

## Agregar un enlace de GitHub

1. Confirmar que el repositorio existe y que es el correcto. Abrir la URL. `gh repo view <owner>/<slug>` alcanza.
2. Poner `url` en `https://github.com/<owner>/<slug>` y `url_verified: true`.
3. Agregar enlaces de documentación solo para archivos que se hayan abierto. Cada uno necesita una etiqueta en inglés y otra en español.
4. Poner la URL en la fila del README en los dos idiomas. Las filas no publicadas siguen en código en línea más "Not published" o "No publicado", sin enlace `https://`.
5. Ejecutar `python3 scripts/validate_portfolio.py --check-links`.

Un slug entre comillas invertidas no es un enlace. No hay que adivinar el owner ni la rama por defecto.

## Proyectos destacados

`featured: true` solo cuando la implementación está lo bastante completa para mostrarla en una entrevista y la nota dice qué va a encontrar quien lea. Después hay que reemplazar la oración "No project is featured yet." en `README.md` y "Ningún proyecto está destacado todavía." en `README.es.md` por una entrada breve de cada proyecto destacado. El validador rechaza una marca featured que el README no menciona, y rechaza la oración de estado vacío cuando algún proyecto está destacado.

Los proyectos 01 y 02 siguen sin destacarse mientras la reconstrucción esté pendiente.

## Mantener los dos idiomas alineados

Los documentos en inglés y en español llevan la misma estructura, los mismos proyectos y las mismas afirmaciones. Los nombres de producto se quedan en inglés. Las traducciones de estado y de dificultad salen del YAML, no de una paráfrasis en la tabla.

Cuando cambia una oración de `repository_note`, hay que pegar la oración nueva en los dos README. El validador las compara como texto exacto.

Archivos que deben seguir en pareja:

| English | Español |
| --- | --- |
| `README.md` | `README.es.md` |
| `docs/roadmap.en.md` | `docs/roadmap.es.md` |
| `docs/learning-methodology.en.md` | `docs/learning-methodology.es.md` |
| `docs/technology-stack.en.md` | `docs/technology-stack.es.md` |
| `projects/schema.en.md` | `projects/schema.es.md` |

## Validar

El validador comprueba el esquema, las filas exactas del README, el texto de proyectos destacados, los enlaces relativos, la ausencia de rutas del directorio personal y de material secreto evidente, y la columna de laboratorio publicado en los dos documentos del stack.

`SEEN_IN_PRIVATE_REPOSITORY` y `MUST_NOT_CLAIM` en `scripts/validate_portfolio.py` son el cierre de esa columna. Una herramienta pasa de una lista a la otra solo cuando un repositorio la muestra. Los dos documentos del stack se actualizan en el mismo cambio. La oración de `PUBLISHED_STATUS` hoy significa que la herramienta se vio en un repositorio privado retirado. Los proyectos 01 y 02 se van a rehacer, y sus slugs del portafolio no están publicados. Cuando exista un repositorio público, hay que cambiar esa oración en el validador y en los dos documentos del stack, y poner `url_verified: true`.

El workflow de GitHub Actions `.github/workflows/validate-portfolio.yml` ejecuta el mismo comando con `--check-links` en push y en pull request. No despliega un sitio.
