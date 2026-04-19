# Sistema de Gestión de Reservas de Canchas Deportivas
## Desarrollado por: Mateo Sanz Medina, Jose Miguel Sánchez, Samuel Arango Echeverri

Este proyecto es una plataforma digital desarrollada en Django para la gestión de reservas de canchas deportivas. Permite a los usuarios consultar disponibilidad, realizar reservas y gestionar pagos, centralizando la administración para los dueños de complejos deportivos.

## Características Principales

- **Gestión de Usuarios**: Registro y autenticación de usuarios.
- **Gestión de Canchas**: Administración de diferentes tipos de canchas (fútbol, tenis, pádel, etc.) con sus tarifas y disponibilidad.
- **Reservas**: Sistema para consultar disponibilidad y reservar canchas en fechas y horarios específicos.
- **Pagos**: Registro de transacciones asociadas a las reservas.
- **Notificaciones**: Sistema de notificaciones (correo electrónico/sms simulado) para confirmar reservas.

## Tecnologías Utilizadas

- **Backend Monolito**: Python 3, Django
- **Microservicio (Notificaciones)**: Python 3, Flask
- **Orquestación y API Gateway**: Docker, Docker Compose, Nginx
- **Base de Datos**: SQLite (por defecto en desarrollo), compatible con PostgreSQL/MySQL via configuración.

## Estructura del Proyecto

El proyecto está compuesto por un monolito y un microservicio orquestados mediante contenedores:

- `gestion_canchas/`: Configuración principal del proyecto Django.
- `reservas/`: Aplicación principal que contiene la lógica de negocio (Modelos, Vistas, URLs).
- `micro_notificaciones/`: Microservicio en Flask extraído usando el patrón Strangler.
- `nginx/`: Configuración del API Gateway que enruta el tráfico.
- `docker-compose.yml`: Archivo de orquestación para levantar todos los servicios.
- `manage.py`: Utilidad de línea de comandos de Django.

### Modelos de Datos

El sistema se basa en los siguientes modelos principales (definidos en `reservas/models.py`):

1.  **Usuario**: Almacena información de los clientes del complejo.
2.  **Cancha**: Define las propiedades de las instalaciones deportivas (tipo, ubicación, tarifa).
3.  **Reserva**: Relaciona un usuario con una cancha en un horario específico.
4.  **Pago**: Registra el estado de los pagos de las reservas.
5.  **Notificacion**: Historial de comunicaciones enviadas a los usuarios.

## Configuración e Instalación

### Método 1: Ejecución con Docker (Recomendado - Arquitectura Strangler Pattern)

Gracias a la implementación del **Strangler Pattern** (Taller 02), el sistema ahora funciona orquestando el monolito (Django) y el microservicio (Flask) a través de un API Gateway (Nginx).

1.  Asegúrate de tener instalado **Docker** y **Docker Compose**.
2.  En la raíz del proyecto, ejecuta:
    ```bash
    docker-compose up --build -d
    ```
3.  El proyecto estará disponible en `http://localhost/` (puerto 80). Nginx enrutará `/api/v1/` a Django y `/api/v2/notificaciones/` al microservicio Flask.

### Método 2: Ejecución Local Tradicional (Solo Django)

1.  **Clonar el repositorio**:
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear un entorno virtual** e instalar dependencias:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # En Windows
    # source venv/bin/activate  # En Mac/Linux
    pip install -r requirements.txt
    ```

3.  **Aplicar migraciones y ejecutar**:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
    El monolito estará disponible en `http://127.0.0.1:8000/`.

## Uso

- Acceder al panel de administración en `http://127.0.0.1:8000/admin/` (requiere crear un superusuario con `python manage.py createsuperuser`).
- Desde allí se pueden gestionar usuarios, canchas y reservas.

## Contribución

1.  Hacer un Fork del proyecto.
2.  Crear una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3.  Hacer commit de tus cambios (`git commit -m 'Aañadir nueva funcionalidad'`).
4.  Hacer push a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Abrir un Pull Request.
