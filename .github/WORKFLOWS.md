# GitHub Actions Workflows

Este proyecto incluye tres workflows de GitHub Actions para automatizar el proceso de integración continua (CI), construcción de Docker, y análisis de seguridad.

## Workflows Disponibles

### 1. CI Workflow (`ci.yml`)

**Propósito**: Ejecutar tests automáticos y validación de código en cada push o pull request.

**Se ejecuta cuando**:
- Push a las ramas `main` o `develop`
- Pull requests hacia `main` o `develop`

**Pasos**:
1. **Checkout del código**: Descarga el código del repositorio
2. **Configuración de Python**: Instala Python 3.11 y 3.12 (matriz de versiones)
3. **Instalación de dependencias**: Instala las dependencias desde `requirements.txt`
4. **Instalación de herramientas de desarrollo**: Instala flake8 y pylint
5. **Análisis con flake8**: 
   - Verifica errores de sintaxis críticos
   - Genera estadísticas de calidad del código
6. **Test de importaciones**: Verifica que los módulos principales se pueden importar correctamente
7. **Test de ejecución**: Ejecuta el programa con `--help` y `status` para verificar funcionalidad básica

**Badges**: 
```markdown
[![CI](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/ci.yml)
```

### 2. Docker Build Workflow (`docker.yml`)

**Propósito**: Construir y verificar la imagen Docker del proyecto.

**Se ejecuta cuando**:
- Push a las ramas `main` o `develop`
- Push de tags con formato `v*` (ej: v1.0.0)
- Pull requests hacia `main` o `develop`

**Pasos**:
1. **Checkout del código**: Descarga el código del repositorio
2. **Setup Docker Buildx**: Configura el entorno de construcción Docker
3. **Build de imagen Docker**: Construye la imagen usando el Dockerfile
4. **Test de imagen Docker**: 
   - Verifica la versión de Python
   - Lista los paquetes instalados

**Características**:
- Utiliza caché de GitHub Actions para acelerar las construcciones
- No sube la imagen a ningún registro (puede configurarse para releases)

**Badges**: 
```markdown
[![Docker Build](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/docker.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/docker.yml)
```

### 3. CodeQL Security Analysis (`codeql.yml`)

**Propósito**: Análisis automático de seguridad del código Python.

**Se ejecuta cuando**:
- Push a las ramas `main` o `develop`
- Pull requests hacia `main` o `develop`
- Cada lunes a las 00:00 UTC (programado)

**Pasos**:
1. **Checkout del repositorio**: Descarga el código
2. **Inicialización de CodeQL**: Configura el análisis para Python
3. **Análisis de CodeQL**: Escanea el código en busca de vulnerabilidades y problemas de calidad

**Características**:
- Detecta vulnerabilidades de seguridad comunes
- Analiza patrones de código problemáticos
- Ejecutión programada semanal para monitoreo continuo
- Los resultados aparecen en la pestaña "Security" del repositorio

**Permisos requeridos**:
- `actions: read`
- `contents: read`
- `security-events: write`

**Badges**: 
```markdown
[![CodeQL](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/codeql.yml/badge.svg)](https://github.com/DMsuDev/ASCII_Generator/actions/workflows/codeql.yml)
```

## Configuración Adicional

### Dependencias para CI
El workflow CI requiere que `requirements.txt` esté actualizado con todas las dependencias del proyecto.

### Dockerfile
El workflow Docker utiliza el `Dockerfile` existente en la raíz del proyecto.

### Caché de pip
Los workflows utilizan caché de pip para acelerar las instalaciones:
```yaml
cache: 'pip'
```

## Ver Resultados

Los resultados de los workflows se pueden ver en:
1. La pestaña "Actions" del repositorio
2. En cada pull request (como checks)
3. Los badges en el README.md

## Solución de Problemas

### CI falla en tests
- Verifica que todas las dependencias estén en `requirements.txt`
- Ejecuta localmente: `pip install -r requirements.txt && python src/main.py --help`

### Docker build falla
- Verifica que el Dockerfile sea válido
- Construye localmente: `docker build -t ascii-generator .`

### CodeQL encuentra problemas
- Revisa la pestaña "Security" → "Code scanning alerts"
- Analiza cada alerta y aplica las correcciones sugeridas

## Mantenimiento

Actualiza las versiones de las acciones periódicamente:
- `actions/checkout@v4` → última versión
- `actions/setup-python@v5` → última versión
- `docker/build-push-action@v5` → última versión
- `github/codeql-action/*@v3` → última versión
