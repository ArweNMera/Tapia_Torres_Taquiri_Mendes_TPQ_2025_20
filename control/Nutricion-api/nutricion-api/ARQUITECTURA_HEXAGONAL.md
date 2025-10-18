# Revisión de arquitectura · `control/Nutricion-api/nutricion-api`

## Visión general
- El backend está organizado alrededor de un esqueleto de arquitectura hexagonal con capas explícitas para API (`app/api`), aplicación (`app/application`), dominio (`app/domain`), infraestructura (`app/infrastructure`), utilidades transversales (`app/core`) y contratos de datos (`app/schemas`).
- La aplicación expone servicios REST mediante FastAPI (`app/main.py`) y usa SQLAlchemy únicamente como fábrica de sesiones; la persistencia real se basa en procedimientos almacenados ejecutados desde los repositorios de infraestructura.
- La carpeta incluye recursos auxiliares como migraciones Alembic (`alembic/`), scripts operativos (`scripts/`) y pruebas unitarias dirigidas a servicios y endpoints (`app/tests/`).

## Capas y responsabilidades

### API (`app/api`)
- Define routers FastAPI agrupados por contexto de negocio (`app/api/v1/endpoints/*.py`).
- Los endpoints resuelven dependencias por medio de `Depends`, instanciando servicios de aplicación o, en varios casos, repositorios de infraestructura directamente.
- Aún conviven módulos legacy en `app/api/v1/*.py` con la nueva estructura `app/api/v1/endpoints/`, lo que indica una migración en progreso.

### Aplicación (`app/application`)
- Contiene servicios de casos de uso, como `AuthService` y `NinosService`, que coordinan validaciones y orquestación entre dominio e infraestructura.
- `app/application/services/` alberga la versión más alineada con el enfoque hexagonal; los archivos `app/application/*.py` fuera de `services/` están vacíos o pendientes.
- Los servicios aplican reglas de negocio específicas (permisos, cálculos de edad, ensamblaje de respuestas) usando entidades o utilidades de dominio.

### Dominio (`app/domain`)
- Incluye entidades puras implementadas como `dataclass` (`app/domain/entities/nino.py`), interfaces de puertos (`app/domain/interfaces/*.py`) y utilidades con reglas propias (`app/domain/utils/nutrition_recommendations.py`).
- Los módulos `app/domain/policies/` están creados pero vacíos, lo que denota intención de centralizar reglas más complejas todavía no implementadas.
- La capa no depende de frameworks externos, cumpliendo el principio central de la arquitectura hexagonal.

### Infraestructura (`app/infrastructure`)
- Implementa los adaptadores secundarios: repositorios que se conectan a la base mediante SQL textual y procedimientos almacenados (`app/infrastructure/repositories/*.py`), capa de seguridad (`security/`) y configuración de base de datos (`db/session.py`).
- Las clases de infraestructura implementan las interfaces declaradas en el dominio (por ejemplo, `UsuariosRepository` -> `IUsuariosRepository`), aunque otras dependencias como `PasswordService` y `JWTService` no tienen contrato abstracto.
- La lógica de persistencia depende fuertemente de procedimientos almacenados definidos en `BaseDatos/database` (`procedimientos.sql`, `procedimientos_nutricion.sql`, `funciones.sql`). El repositorio ejecuta llamadas `CALL sp_*` en prácticamente todas las operaciones (registro de usuarios, antropometrías, nutrición, tokens), lo que reduce la visibilidad del dominio y limita pruebas unitarias sin base de datos.

### Persistencia basada en procedimientos almacenados
- Tras la primera ola de migración se eliminaron todas las sentencias SQL crudas del backend; los repositorios ahora invocan procedimientos (`CALL sp_*`) definidos en `BaseDatos/database/procedimientos.sql`.
- Se añadieron procedimientos específicos para menús, preferencias, administración de usuarios y alergias (`sp_menus_*`, `sp_preferencias_*`, `sp_admin_*`, `sp_comidas_favoritas_*`, `sp_ninos_alergia_eliminar`, etc.), manteniendo la lógica de lectura/escritura en la base y liberando a la capa API de concatenar consultas.
- El enfoque sigue ubicando reglas significativas en la base de datos; es crucial acompañar estos SP con pruebas y versionamiento coordinado para no desplazar inadvertidamente reglas del dominio a SQL difícil de testear.

### Esquemas (`app/schemas`)
- Agrupan los DTOs y modelos Pydantic utilizados por API y servicios para validar I/O. Sirven como boundary entre la API y las capas internas.

### Core (`app/core`)
- Contiene configuraciones transversales (`config.py`), logging, paginación y la integración con Firebase (`firebase.py`, `events.py`). Funciona como soporte compartido entre capas.

## Flujo de dependencias
- **API → Aplicación → Dominio**: cuando se usa `AuthService` o `UsuariosService`, el flujo respeta la dirección propuesta por la arquitectura hexagonal.
- **API → Infraestructura**: varios endpoints (`app/api/v1/endpoints/ninos.py`, `ml.py`, etc.) instancian repositorios directamente, saltándose los servicios de aplicación. Esto "achata" la capa de aplicación y mezcla lógica de orquestación dentro del adaptador HTTP.
- **Aplicación → Infraestructura**: los servicios aceptan implementaciones concretas de repositorios (cumpliendo inversión de dependencias) pero también consumen clases de infraestructura sin interfaz (`PasswordService`, `JWTService`, `GoogleOAuthClient`), lo que introduce acoplamiento fuerte con tecnología.

## Evaluación frente a la arquitectura hexagonal

**Fortalezas**
- Separación física clara de carpetas por capa, lo que facilita la navegación y el reemplazo de adaptadores.
- Interfaces de repositorio en `app/domain/interfaces` que permiten intercambiar implementaciones de persistencia.
- Entidades y utilidades de dominio sin dependencias externas, alineadas con el núcleo independiente de la arquitectura hexagonal.
- Servicios de aplicación que encapsulan validaciones de negocio y coordinan múltiples repositorios (`app/application/services/ninos_service.py`, `usuarios_service.py`).

**Desviaciones / riesgos**
- Endpoints que consumen repositorios directamente (`app/api/v1/endpoints/ninos.py`, `ml.py`) rompen el principio de que la lógica de casos de uso viva en la capa de aplicación.
- Dependencias concretas de infraestructura inyectadas desde la capa de aplicación (por ej. `AuthService` importa `PasswordService` y `JWTService` de `app/infrastructure/security` sin interfaces), lo que dificulta sustituir tecnología (otro proveedor de hashes o JWT).
- Módulos de dominio previstos (`app/domain/policies/`, `models.py`) todavía vacíos; la lógica sigue residiendo en servicios o utilidades, perdiendo oportunidad de centralizar reglas.
- Duplicidad de routers legacy en `app/api/v1/*.py` vs `app/api/v1/endpoints/*.py`, lo que puede causar rutas inconsistentes y carga cognitiva adicional.
- Servicios en `app/application/` fuera del submódulo `services/` están vacíos, señalando refactor incompleto.
- Las reglas encapsuladas en procedimientos almacenados impiden aplicar pruebas unitarias aisladas y requieren despliegues coordinados de código y base de datos; cualquier cambio en negocio exige migraciones SQL complejas.

## Recomendaciones
1. Completar la migración de endpoints para que todos utilicen `app/application/services`, evitando instanciar repositorios desde la capa API.
2. Introducir interfaces (puertos) para servicios de seguridad (`PasswordHasher`, `TokenProvider`, `OAuthClient`) que hoy están acoplados a implementaciones concretas en `app/infrastructure/security`.
3. Trasladar reglas de negocio repetidas de los endpoints (`app/api/v1/endpoints/ninos.py`) hacia entidades o políticas de dominio, o extender los servicios de aplicación existentes.
4. Eliminar o archivar los módulos legacy de `app/api/v1/*.py` una vez que `app/api/v1/endpoints/` cubra toda la superficie, para evitar duplicidad.
5. Poblar los módulos vacíos de `app/domain/policies/` o consolidarlos con `app/domain/utils/` para mantener un núcleo de dominio coherente y fácilmente testeable.
6. Revisar y modularizar el catálogo de procedimientos almacenados recién incorporados, documentando parámetros y efectos colaterales para asegurar trazabilidad y poder cubrirlos con pruebas automáticas.

## Plan de migración desde SQL crudo y procedimientos almacenados
1. **Inventario y clasificación**
   - Documentar cada `CALL sp_*` detectado, describiendo qué endpoints o servicios lo utilizan y en qué archivos SQL se encuentra su definición.
   - Clasificar los procedimientos según criticidad (autenticación, nutrición, catálogos) y complejidad (solo CRUD, cálculos, transacciones compuestas).
2. **Definir modelo de datos en código**
   - Crear modelos SQLAlchemy (o dataclasses + mapeos) para tablas clave (`usuarios`, `ninos`, `antropometria`, catálogos) y establecer repositorios que soporten operaciones CRUD equivalentes a las de los SP sencillos.
   - Establecer pruebas unitarias sobre estos repositorios usando una base de datos en memoria o fixtures controlados.
3. **Extraer reglas de negocio al dominio**
   - Migrar reglas actualmente implementadas dentro de los SP (validaciones de rol, cálculos de autonomía, evaluaciones nutricionales) hacia servicios/entidades de dominio (`app/domain/policies`, `app/domain/utils`).
   - Validar que el dominio pueda ejecutarse sin acceso a la base mediante pruebas unitarias puras.
4. **Reemplazo gradual de endpoints**
   - Para cada caso de uso, crear una implementación alternativa en los repositorios/servicios que use el nuevo stack ORM o consultas parametrizadas explícitas.
   - Incorporar feature flags o configuración que permitan seleccionar entre SP y nueva lógica durante el periodo de transición.
5. **Migración de scripts y despliegue**
   - Reducir el contenido de `procedimientos.sql` y `procedimientos_nutricion.sql` a solo operaciones imprescindibles (por ejemplo, reporting masivo).
   - Añadir migraciones Alembic que creen vistas, funciones o triggers necesarios, eliminando procedimientos deprecated una vez verificada la nueva ruta.
6. **Automatización y monitoreo**
   - Actualizar pipelines CI/CD para ejecutar pruebas sobre la nueva capa y asegurar que la eliminación de SP no rompe compatibilidad.
   - Registrar métricas de rendimiento para comparar tiempos entre SP y nueva lógica; mantener SP específicos solo si el impacto en performance es crítico.

En conjunto, la estructura establece una buena base hexagonal, pero requiere completar la inversión de dependencias y consolidar los puntos de acceso a la lógica de negocio para materializar plenamente los principios de la arquitectura.
