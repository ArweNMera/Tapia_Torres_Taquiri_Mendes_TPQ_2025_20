# Despliegue en Google Cloud Platform (GCP)

Este documento guía el despliegue del backend (`control/Nutricion-api`) y el servicio de modelo ML (`modelo/ml-recomendator`) en GCP. El frontend ya está hospedado en la nube (Netlify/Vercel), así que el objetivo es publicar los servicios de API y conectarlos a una base de datos administrada.

## Resumen y Recomendación

- Stack actual:
  - Backend: FastAPI en Python 3.11, puerto `8000`, con MySQL (via `mysql+pymysql`).
  - Modelo ML: FastAPI en Python 3.11, puerto `8001`, usa MySQL para datos/modelos.
  - DB local: MySQL corriendo en host (`host.docker.internal`).
  - Variables de entorno y credenciales (Google OAuth, Firebase) gestionadas vía `.env` y archivo JSON.
- Recomendación: **Cloud Run (serverless contenedores)** para backend y modelo ML.
  - Ventajas: menor operación, escala automática (incluye escala a 0), facturación por uso, integración nativa con Cloud SQL, Secret Manager, IAM, Logging/Monitoring.
  - Usa imágenes de contenedor existentes (ya hay Dockerfiles) y soporta puertos personalizados (`--port=8000/8001`).
- Alternativa: **GKE (Kubernetes Autopilot)** si más adelante necesitan:
  - GPUs dedicadas o despliegues complejos (DaemonSets, Jobs, colas internas).
  - Control fino de networking, malla de servicios, operadores, sidecars.
  - Tolerancia a requisitos muy específicos de runtime.

Para el estado actual (dos APIs HTTP con FastAPI, MySQL administrado, credenciales y OAuth), Cloud Run es el balance ideal de simplicidad y robustez.

## Arquitectura Propuesta en GCP

- Artifact Registry: repositorio Docker para imágenes `backend` y `modelo-ml`.
- Cloud Run:
  - Servicio `nutricion-backend` (puerto 8000).
  - Servicio `nutricion-ml` (puerto 8001).
- Cloud SQL (MySQL): instancia administrada `nutricion-mysql` + base `nutricion`.
- Secret Manager: credenciales sensibles (DB, JWT secret, Google OAuth, Firebase JSON).
- Serverless VPC Access: conector para salida privada hacia Cloud SQL.
- Cloud Logging y Cloud Monitoring: observabilidad.

## Preparativos

1) Habilitar APIs:
```
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  sqladmin.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com
```

2) Variables base:
```
PROJECT_ID=<tu_project_id>
REGION=us-central1
REPO=nutricion
SQL_INSTANCE=nutricion-mysql
DB_NAME=nutricion
```

3) Artifact Registry:
```
gcloud artifacts repositories create $REPO \
  --repository-format=docker --location=$REGION \
  --description="Imágenes del proyecto Nutrición"
```

## Construcción y Push de Imágenes

Backend:
```
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest ./control/Nutricion-api
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest
```

Modelo ML:
```
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/modelo-ml:latest ./modelo/ml-recomendator
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO/modelo-ml:latest
```

## Base de Datos (Cloud SQL - MySQL)

Crear instancia y base:
```
gcloud sql instances create $SQL_INSTANCE --database-version=MYSQL_8_0 \
  --cpu=2 --memory=7680MiB --region=$REGION

gcloud sql databases create $DB_NAME --instance=$SQL_INSTANCE
```

Usuario de aplicación (evitar `root`):
```
DB_USER=app_user
DB_PASSWORD=<genera_un_password_seguro>

gcloud sql users create $DB_USER --instance=$SQL_INSTANCE --password=$DB_PASSWORD
```

Cadena de conexión (Cloud Run + Cloud SQL socket):
```
# Formato SQLAlchemy (pymysql) usando socket unix
DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASSWORD@/$DB_NAME?unix_socket=/cloudsql/$PROJECT_ID:$REGION:$SQL_INSTANCE
```

Carga de esquema/datos (opcional):
- Conecta con `gcloud sql connect $SQL_INSTANCE --user=$DB_USER` y ejecuta los `.sql` de `BaseDatos/database/`.
- O usa `mysql` client desde tu máquina/CI apuntando a Cloud SQL.

## Secretos y Configuración

- Secret Manager: crea secretos para `SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `FIREBASE_CREDENTIALS_JSON`, etc.
```
echo -n "$SECRET_KEY" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "$GOOGLE_CLIENT_ID" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "$GOOGLE_CLIENT_SECRET" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
# Archivo JSON de Firebase
gcloud secrets create FIREBASE_CREDENTIALS_JSON --data-file=control/Nutricion-api/nutricion-api/nutricion-dd80c-firebase-adminsdk-fbsvc-356ee61526.json
```

- Opciones de uso del secreto de Firebase:
  1) Como **env var** (`FIREBASE_CREDENTIALS_JSON`) y que el código lo lea desde env.
  2) Como **archivo montado**: Cloud Run soporta secretos como volumen; puedes montar en `/secrets/firebase_credentials.json` si tu código lo requiere.

## Despliegue en Cloud Run

Crear conector VPC (para Cloud SQL):
```
gcloud compute networks vpc-access connectors create serverless-conn \
  --region=$REGION --network=default --range=10.8.0.0/28
```

Backend (puerto 8000):
```
gcloud run deploy nutricion-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest \
  --region=$REGION --allow-unauthenticated --port=8000 \
  --memory=1Gi --cpu=1 \
  --vpc-connector=serverless-conn --vpc-egress=all-traffic \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:$SQL_INSTANCE \
  --set-env-vars=DATABASE_URL="mysql+pymysql://$DB_USER:$DB_PASSWORD@/$DB_NAME?unix_socket=/cloudsql/$PROJECT_ID:$REGION:$SQL_INSTANCE" \
  --set-env-vars=SECRET_KEY=$SECRET_KEY,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  --set-env-vars=GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET \
  --set-env-vars=FRONTEND_ORIGINS="https://tu-dominio-frontend" \
  --set-env-vars=ML_SERVICE_URL="https://nutricion-ml-343042748851.europe-west1.run.app"
```

Modelo ML (puerto 8001):
```
gcloud run deploy nutricion-ml \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/modelo-ml:latest \
  --region=$REGION --allow-unauthenticated --port=8001 \
  --memory=1Gi --cpu=1 \
  --vpc-connector=serverless-conn --vpc-egress=all-traffic \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:$SQL_INSTANCE \
  --set-env-vars=DB_HOST="/cloudsql/$PROJECT_ID:$REGION:$SQL_INSTANCE" \
  --set-env-vars=DB_PORT=3306,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_NAME=$DB_NAME
```

Notas importantes:
- Cloud Run por defecto usa `PORT=8080`. Aquí se fija `--port=8000/8001` para respetar los contenedores actuales. Alternativamente, modifica el comando de `uvicorn` para leer `PORT` dinámico.
- Para CORS, ajusta `FRONTEND_ORIGINS` con el dominio real del frontend.
- Si usas secretos como archivo, añade la sección de volúmenes de secretos en el servicio.

## Observabilidad y Seguridad

- Logging: Cloud Logging (consulta por servicio).
- Metrics/Alerting: Cloud Monitoring (latencia, errores, CPU, memoria).
- IAM: crea una service account por servicio (backend y ML) y limita permisos.
- Cloud Armor (opcional): reglas de seguridad HTTP en el frontend/backends públicos.
- Dominios y HTTPS: usa mapeo de dominio de Cloud Run y certificados administrados.

## Alternativa: GKE (Kubernetes)

Cuándo considerar GKE:
- Necesidad de GPU y workloads intensivos, pipelines de batch, colas internas.
- Sidecars (auth proxy), operadores de ML, control de nodos.

Resumen de pasos (Autopilot):
1) Crear cluster Autopilot.
2) YAMLs de `Deployment`, `Service`, `ConfigMap`, `Secret` para backend y ML.
3) Ingresos HTTP (HTTP Load Balancer) vía `Ingress`.
4) Cloud SQL Auth Proxy (sidecar) o Connector en VPC.
5) CI/CD hacia GKE (Cloud Build/GitHub Actions + `kubectl` o `kustomize`).

Más potente, pero mayor complejidad operativa y costo base (cluster).

## Costos y Escalado

- Cloud Run: pago por request/CPU/memoria, escala automática y a 0; ideal para picos.
- GKE: costo del cluster + nodos, útil para cargas constantes y complejas.
- Cloud SQL: costo por instancia y almacenamiento; dimensionar según uso.

## Próximos Pasos

1) Crear los recursos (Artifact Registry, Cloud SQL, Secret Manager, VPC Connector).
2) Construir y publicar imágenes.
3) Desplegar servicios en Cloud Run y configurar CORS.
4) Probar endpoints (`/docs`) y revisar logs.
5) Integrar CI/CD (Cloud Build o GitHub Actions) para builds y despliegues automáticos.

---

Ante cualquier ajuste (p.ej., lectura dinámica del `PORT`, montaje de secretos como archivo, o cambios en cadena de conexión), puedo adaptar los Dockerfiles/arranque para producción.
