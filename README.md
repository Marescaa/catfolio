# catfolio

Un gatito pixel-art para el README de tu perfil. Se mueve por una escena en loop
y cambia de ánimo según tus commits de los últimos 7 días. Inspirado en
[git-koi](https://docs.rs/crate/git-koi/latest).

<p align="center">
  <img src="dist/naranja/happy.gif" width="480" alt="Gato naranja paseando" />
</p>

## Estados

| Estado | Commits (7 días) | Qué hace |
|---|---|---|
| `sleep` | solo manual | Duerme sobre el cojín. |
| `calm` | 0 a 2 | Pasea despacio y se sienta en cada parada. |
| `happy` | 3 a 6 | Camina más ágil, se lame la pata y salen corazones. |
| `joyful` | 7 o más | Más paradas y más corazones. |

<p align="center">
  <img src="dist/naranja/sleep.gif" width="300" alt="sleep" />
  <img src="dist/naranja/calm.gif" width="300" alt="calm" />
  <img src="dist/naranja/joyful.gif" width="300" alt="joyful" />
</p>

## Pelajes

`gris`, `naranja`, `calico`, `siames`, `blanco`, `esmoquin`, `negro`, `atigrado`.
Cada uno está en `dist/<pelaje>/<estado>.gif`.

## Uso en tu perfil

1. Copiá [`examples/workflow.yml`](examples/workflow.yml) a
   `.github/workflows/cat.yml` de tu repo de perfil (`TU_USUARIO/TU_USUARIO`) y
   cambiá `Marescaa` por el usuario donde tengas este repo.
2. Pegá en tu `README.md`:

   ```html
   <p align="center"><img src="cat/cat.gif" width="480" alt="Mi gato" /></p>
   ```

3. Corré el workflow una vez a mano (`Actions → gato → Run workflow`). Después se
   actualiza solo todas las noches.

### Opciones del Action

| Input | Por defecto | Descripción |
|---|---|---|
| `coat` | `naranja` | Pelaje. |
| `state` | `auto` | `auto` según commits, o forzar `sleep`, `calm`, `happy`, `joyful`. |
| `days` | `7` | Ventana de días. |
| `login` | dueño del repo | Cuenta a consultar. |
| `output-dir` | `cat` | Carpeta de salida (`cat.gif`, `cat.json`, `preview.html`). |

## Línea de comandos

```bash
python src/git_cat.py --login TU_USUARIO --coat gris --output-dir cat   # usa GITHUB_TOKEN
python src/git_cat.py --commits 5 --coat negro --output-dir cat         # sin red
python src/git_cat.py --state sleep --coat calico --output-dir cat
```

Solo usa la biblioteca estándar de Python.

## Estructura

```text
.
├── action.yml      el GitHub Action
├── assets/gatos/   sprites originales (sentado, lamiendose, dormido, caminando)
├── dist/           escenas ya renderizadas, 8 pelajes x 4 estados
├── examples/       workflow de ejemplo
├── src/            git_cat.py: elige el estado y copia el GIF
├── tests/          umbrales y existencia de los GIF
└── tools/render.py regenera dist/ desde assets/ (requiere Pillow)
```

Para regenerar las escenas: `pip install -r requirements-dev.txt && python tools/render.py`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
