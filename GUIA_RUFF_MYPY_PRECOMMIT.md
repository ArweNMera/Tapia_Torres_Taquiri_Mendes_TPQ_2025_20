# Guía: Ruff + Mypy + Pre-commit

## 🎯 Stack Moderno de Calidad de Código Python

Esta guía configura las mejores herramientas para mantener código Python limpio y consistente:

- **Ruff**: Linter y formatter ultra-rápido (reemplaza Black, isort, Flake8, etc.)
- **Mypy**: Type checker estático
- **Pre-commit**: Automatiza la ejecución de herramientas antes de cada commit

## 📦 Instalación

### 1. Instalar Dependencias de Desarrollo

#### Para Nutricion API:
```bash
cd control/Nutricion-api/nutricion-api
pip install ruff mypy pre-commit bandit
```

#### Para ML Recomendator:
```bash
cd modelo/ml-recomendator
pip install ruff mypy pre-commit nbqa
```

### 2. Instalar Pre-commit Hooks

#### Nutricion API:
```bash
cd control/Nutricion-api/nutricion-api
pre-commit install
```

#### ML Recomendator:
```bash
cd modelo/ml-recomendator
pre-commit install
```

Esto instalará los hooks que se ejecutarán automáticamente antes de cada commit.

## 🚀 Uso

### Ejecución Automática (Recomendado)

Una vez instalado, los hooks se ejecutan automáticamente al hacer commit:

```bash
git add .
git commit -m "feat: nueva funcionalidad"
# Los hooks se ejecutan automáticamente
```

Si hay errores, el commit se cancela y debes corregirlos.

### Ejecución Manual

#### Ejecutar todos los hooks:
```bash
pre-commit run --all-files
```

#### Ejecutar solo Ruff:
```bash
# Linting
ruff check .

# Linting con auto-fix
ruff check --fix .

# Formateo
ruff format .
```

#### Ejecutar solo Mypy:
```bash
mypy .
```

## 📋 Configuraciones Incluidas

### Ruff (pyproject.toml)

#### Reglas Activadas:
- **E, W**: Errores y warnings de PEP 8
- **F**: Pyflakes (errores lógicos)
- **I**: isort (ordenar imports)
- **B**: flake8-bugbear (bugs comunes)
- **C4**: flake8-comprehensions (mejoras en comprehensions)
- **UP**: pyupgrade (modernizar código)
- **ARG**: flake8-unused-arguments (argumentos no usados)
- **SIM**: flake8-simplify (simplificar código)
- **NPY**: NumPy-specific (solo ML)
- **PD**: pandas-vet (solo ML)

#### Configuración:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
```

### Mypy (pyproject.toml)

#### Configuración:
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
show_error_codes = true
```

### Pre-commit (.pre-commit-config.yaml)

#### Hooks Incluidos:
1. **pre-commit-hooks**: Validaciones básicas
2. **ruff**: Linting y formateo
3. **mypy**: Type checking
4. **bandit**: Seguridad (solo API)
5. **nbqa**: Notebooks (solo ML)

## 🔧 Comandos Útiles

### Actualizar Hooks
```bash
pre-commit autoupdate
```

### Ejecutar en Archivos Específicos
```bash
pre-commit run --files src/models/*.py
```

### Saltar Hooks (NO RECOMENDADO)
```bash
git commit -m "mensaje" --no-verify
```

### Ver Configuración de Ruff
```bash
ruff check --show-settings
```

### Generar Reporte de Mypy
```bash
mypy . --html-report mypy-report
```

## 📊 Integración con CI/CD

### GitHub Actions

Crea `.github/workflows/quality.yml`:

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install ruff mypy pre-commit
          pip install -r requirements.txt

      - name: Run Ruff
        run: ruff check .

      - name: Run Mypy
        run: mypy .

      - name: Run Pre-commit
        run: pre-commit run --all-files
```

## 🎨 Integración con VS Code

### settings.json

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.lint.args": ["--config=pyproject.toml"],
  "mypy-type-checker.args": ["--config-file=pyproject.toml"]
}
```

### Extensiones Recomendadas:
- **Ruff**: `charliermarsh.ruff`
- **Mypy**: `ms-python.mypy-type-checker`
- **Python**: `ms-python.python`

## 🔍 Ejemplos de Uso

### Antes de Ruff:
```python
import sys
import os
from typing import List
import numpy as np
from fastapi import FastAPI

def calculate_bmi(weight:float,height:float)->float:
    return weight/(height**2)

class User:
    def __init__(self,name,age):
        self.name=name
        self.age=age
```

### Después de Ruff:
```python
import os
import sys
from typing import List

import numpy as np
from fastapi import FastAPI


def calculate_bmi(weight: float, height: float) -> float:
    return weight / (height**2)


class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

## 🐛 Solución de Problemas

### Error: "command not found: pre-commit"
```bash
pip install pre-commit
```

### Error: "No module named 'ruff'"
```bash
pip install ruff
```

### Mypy reporta muchos errores
Ajusta la configuración en `pyproject.toml`:
```toml
[tool.mypy]
ignore_missing_imports = true
disallow_untyped_defs = false
```

### Pre-commit es muy lento
Ejecuta solo en archivos modificados:
```bash
pre-commit run --files $(git diff --name-only --cached)
```

## 📚 Recursos

- **Ruff**: https://docs.astral.sh/ruff/
- **Mypy**: https://mypy.readthedocs.io/
- **Pre-commit**: https://pre-commit.com/
- **Bandit**: https://bandit.readthedocs.io/

## ✅ Checklist de Configuración

### Nutricion API:
- [x] `pyproject.toml` configurado
- [x] `.pre-commit-config.yaml` configurado
- [ ] Instalar dependencias: `pip install ruff mypy pre-commit bandit`
- [ ] Instalar hooks: `pre-commit install`
- [ ] Ejecutar primera vez: `pre-commit run --all-files`

### ML Recomendator:
- [x] `pyproject.toml` configurado
- [x] `.pre-commit-config.yaml` configurado
- [ ] Instalar dependencias: `pip install ruff mypy pre-commit nbqa`
- [ ] Instalar hooks: `pre-commit install`
- [ ] Ejecutar primera vez: `pre-commit run --all-files`

## 🎯 Mejores Prácticas

1. **Ejecuta pre-commit antes de push**:
   ```bash
   pre-commit run --all-files
   git push
   ```

2. **Actualiza hooks regularmente**:
   ```bash
   pre-commit autoupdate
   ```

3. **Revisa los cambios de Ruff**:
   ```bash
   ruff check --diff .
   ```

4. **Usa type hints gradualmente**:
   - Empieza con funciones públicas
   - Luego clases principales
   - Finalmente todo el código

5. **Ignora errores específicos cuando sea necesario**:
   ```python
   # ruff: noqa: E501
   very_long_line = "..."

   # type: ignore[arg-type]
   result = function(arg)
   ```

## 🚀 Próximos Pasos

1. Instalar dependencias en ambos proyectos
2. Ejecutar `pre-commit run --all-files` para ver estado actual
3. Corregir errores críticos
4. Configurar CI/CD con GitHub Actions
5. Integrar con VS Code
6. Documentar convenciones del equipo
