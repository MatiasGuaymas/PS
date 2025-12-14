# Puff-Tóricos 🏛️

Sistema web integral para la gestión, visualización y difusión del patrimonio histórico argentino. Permite a administradores y editores gestionar sitios históricos, mientras que el público puede explorar, buscar y reseñar estos lugares de interés cultural.

## 🌐 Despliegue

El proyecto se encuentra deployado y disponible en los siguientes enlaces:

- **Portal Público:** https://grupo21.proyecto2025.linti.unlp.edu.ar/
- **Panel de Administración:** https://admin-grupo21.proyecto2025.linti.unlp.edu.ar/

## 👥 Colaboradores

- [Lautaro Budini](https://github.com/lautibudini)
- [Matias Guaymas](https://github.com/MatiasGuaymas)
- [Francisco Lima](https://github.com/franciscolima05)
- [Leo Luna](https://github.com/Leonardo-Luna)
- [Santiago Marcos](https://github.com/santi440)

## 💻 Lenguajes de Programación

### Lenguajes Principales
- **Python** 3.12+ (Backend - Flask, SQLAlchemy)
- **JavaScript** (Frontend - Vue.js 3, Vite)
- **SQL** (PostgreSQL con PostGIS - Consultas geoespaciales)

### Lenguajes de Marcado y Estilos
- **HTML5** (Templates Jinja2)
- **CSS3** (Estilos y variables CSS)

### Lenguajes de Configuración
- **YAML** (Docker Compose)
- **JSON** (Configuración de dependencias y build)

## 🚀 Tecnologías Utilizadas

### Backend (Admin)
- **Framework:** Flask 3.1.2
- **ORM:** SQLAlchemy con Flask-SQLAlchemy
- **Base de Datos:** PostgreSQL 16 con PostGIS 3.4
- **Autenticación:** Flask-Session, Bcrypt, Google OAuth
- **Almacenamiento:** MinIO (S3-compatible)
- **Geolocalización:** GeoAlchemy2, Shapely
- **Containerización:** Docker

### Frontend (Portal)
- **Framework:** Vue.js 3
- **Router:** Vue Router
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Estilos:** CSS3, Variables CSS
- **UI Components:** Bootstrap 5
- **Iconos:** Bootstrap Icons

### Herramientas de Desarrollo
- **Gestión de Dependencias Backend:** Poetry
- **Gestión de Dependencias Frontend:** npm
- **Control de Versiones:** Git
- **IDE Recomendado:** Visual Studio Code
- **Administración DB:** pgAdmin 4

## 📋 Requisitos Previos

- **Python:** 3.12 o superior
- **Node.js:** 16.x o superior
- **Docker:** 20.x o superior
- **Docker Compose:** 2.x o superior
- **Poetry:** 1.x o superior
- **Git:** 2.x o superior

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd code
```

### 2. Configuración de Variables de Entorno

#### Backend (.env en /admin)
Crear el archivo .env con el siguiente contenido:

```
# Configuración de PostgreSQL
POSTGRES_USER=proyecto_user
POSTGRES_PASSWORD=123456
POSTGRES_DB=proyecto

# Configuración de Google OAuth
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
GOOGLE_SECRET_KEY=tu-secret-key-generada
GOOGLE_SESSION_TYPE=filesystem

# Configuración de pgAdmin
PGADMIN_EMAIL=admin@proyecto.com
PGADMIN_PASSWORD=123456

# Configuración de MinIO
MINIO_USER=admin
MINIO_PASSWORD=adminpass
MINIO_ACCESS_KEY=LaRompeToda
MINIO_SECRET_KEY=LaRompeToda1234
MINIO_SECURE=False

# Configuración de Flask
FLASK_ENV=development
```

#### Frontend (.env en /portal)
Crear el archivo portal/.env con el siguiente contenido:

```
VITE_API_URL=http://localhost:5000
```

## 🔧 Ejecución del Proyecto
#### Backend (Admin)

### 1. Navegar al directorio del backend:
```bash
cd admin
```

### 2. Instalar dependencias con Poetry: 
```bash
poetry install
```

### 3. Levantar servicios de infraestructura (PostgreSQL, pgAdmin, MinIO):
```bash
docker-compose up -d
```

### 4. Activar el entorno virtual:
```bash
poetry env activate
```
Copia la salida de la consola y ejecútala para activar el entorno virtual.

### 5. Inicializar la base de datos (primera vez):
```bash
flask reset-db
flask seed-db
```

### 6. Ejecutar el servidor Flask:
```bash
python main.py
```
El backend estará disponible en: http://localhost:5000

#### Frontend (Portal)
#### 1. Navegar al directorio del frontend:
```bash
cd portal
```

### 2. Instalar dependencias con npm:
```bash
npm install
```

### 3. Ejecutar el servidor de desarrollo:
```bash
npm run dev
```
El frontend estará disponible en: http://localhost:5173

## 🐳 Servicios Docker
Una vez ejecutado docker-compose up -d en admin/, los siguientes servicios estarán disponibles:

| Servicio | Puerto | Acceso | Credenciales |
|----------|--------|--------|--------------|
| PostgreSQL | 5432 | localhost:5432 | User: proyecto_user<br>Pass: 123456 |
| pgAdmin | 5050 | http://localhost:5050 | Email: admin@proyecto.com<br>Pass: 123456 |
| MinIO Console | 9001 | http://localhost:9001 | User: admin<br>Pass: adminpass |
| MinIO API | 9000 | localhost:9000 | - |

## 📁 Estructura del Proyecto

```
code/
├── admin/                     # Backend Flask
│   ├── src/
│   │   ├── core/              # Lógica de negocio
│   │   │   ├── models/        # Modelos SQLAlchemy
│   │   │   ├── services/      # Servicios de negocio
│   │   │   └── utils/         # Utilidades
│   │   └── web/               # Capa web
│   │       ├── controllers/   # Controladores Flask
│   │       ├── templates/     # Templates Jinja2
│   │       └── utils/         # Utilidades web
│   ├── static/                # Archivos estáticos
│   ├── tests/                 # Tests unitarios
│   └── docker-compose.yaml    # Infraestructura
├── portal/                     # Frontend Vue.js
│   ├── src/
│   │   ├── components/        # Componentes Vue
│   │   ├── views/             # Vistas/Páginas
│   │   ├── router/            # Configuración de rutas
│   │   └── utils/             # Utilidades
│   └── public/                # Assets públicos
└── README.md
```

## 🎯 Funcionalidades Principales

### Panel de Administración
- ✅ CRUD completo de sitios históricos
- ✅ Gestión de imágenes con MinIO
- ✅ Sistema de roles y permisos
- ✅ Moderación de reseñas
- ✅ Exportación de datos a CSV
- ✅ Feature flags para mantenimiento
- ✅ Auditoría de acciones

### Portal Público
- ✅ Búsqueda y filtrado avanzado de sitios
- ✅ Visualización de sitios con mapas interactivos
- ✅ Sistema de reseñas y calificaciones
- ✅ Gestión de favoritos
- ✅ Autenticación con Google OAuth
- ✅ Perfil de usuario personalizable
- ✅ Modo mantenimiento configurable

## 🔐 Usuarios por Defecto

Después de ejecutar `flask seed-db`, se crean los siguientes usuarios:

| Email | Password | Rol |
|-------|----------|-----|
| admin@admin.com | admin123 | Administrador |
| editor@editor.com | editor123 | Editor |

## 🛠️ Comandos Útiles

### Backend
```bash
# Resetear base de datos
flask reset-db

# Poblar base de datos con datos de prueba
flask seed-db

# Crear migraciones
flask db migrate -m "descripción"

# Aplicar migraciones
flask db upgrade

# Ejecutar tests
poetry run pytest
```

### Frontend
```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Compilar para producción
npm run build

# Previsualizar build de producción
npm run preview

# Ejecutar linter
npm run lint
```

### Docker
```bash
# Levantar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Ver estado de contenedores
docker-compose ps
```

## 📝 Notas Adicionales

- Para producción, asegurarse de cambiar `FLASK_ENV=production` en el archivo .env
- Las credenciales de Google OAuth deben configurarse en la [Google Cloud Console](https://console.cloud.google.com/)
  - Configurar URLs autorizadas de origen: `http://localhost:5000`
  - Configurar URIs de redirección: `http://localhost:5000/api/auth/google/callback`
- MinIO requiere configuración inicial la primera vez que se accede a su consola
- El bucket de MinIO (grupo21) se crea automáticamente al ejecutar seeds
- PostGIS se activa automáticamente mediante el script `init.sql`

## 🐛 Solución de Problemas

### Error de conexión a PostgreSQL
```bash
# Verificar que el contenedor esté corriendo
docker ps

# Reiniciar el contenedor de PostgreSQL
docker-compose restart postgres
```

### Error de instalación de dependencias Backend
```bash
# Limpiar caché de Poetry
poetry cache clear pypi --all

# Reinstalar dependencias
poetry install
```

### Error de instalación de dependencias Frontend
```bash
# Eliminar node_modules y package-lock.json
rm -rf node_modules package-lock.json

# Reinstalar
npm install
```

### Puerto ya en uso
```bash
# Encontrar proceso usando el puerto (ejemplo: 5000)
lsof -i :5000

# Matar el proceso
kill -9 <PID>
```

### MinIO no guarda imágenes
```bash
# Verificar que el bucket existe
# Acceder a http://localhost:9001 y crear manualmente el bucket "grupo21"

# O ejecutar nuevamente los seeds
flask seed-db
```

### Error al activar entorno virtual de Poetry
```bash
# Activar manualmente el entorno virtual
source $(poetry env info --path)/bin/activate
```

## 🔒 Seguridad

- Las contraseñas se hashean con Bcrypt antes de almacenarse
- Las sesiones se gestionan con Flask-Session
- CORS configurado para permitir solo orígenes autorizados
- Validación de permisos en cada endpoint del backend
- Sanitización de inputs en formularios

## 📄 Licencia

Este proyecto es parte del curso de **Proyecto de Software 2025 - UNLP**.
