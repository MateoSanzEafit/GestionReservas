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

- **Backend**: Python 3, Django
- **Base de Datos**: SQLite (por defecto en desarrollo), compatible con PostgreSQL/MySQL via configuración.

## Estructura del Proyecto

El proyecto sigue la estructura estándar de Django:

- `gestion_canchas/`: Configuración principal del proyecto.
- `reservas/`: Aplicación principal que contiene la lógica de negocio (Modelos, Vistas, URLs).
- `manage.py`: Utilidad de línea de comandos de Django.

### Modelos de Datos

El sistema se basa en los siguientes modelos principales (definidos en `reservas/models.py`):

1.  **Usuario**: Almacena información de los clientes del complejo.
2.  **Cancha**: Define las propiedades de las instalaciones deportivas (tipo, ubicación, tarifa).
3.  **Reserva**: Relaciona un usuario con una cancha en un horario específico.
4.  **Pago**: Registra el estado de los pagos de las reservas.
5.  **Notificacion**: Historial de comunicaciones enviadas a los usuarios.

## Configuración e Instalación

1.  **Clonar el repositorio** (si aplica):
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear un entorno virtual** (recomendado):
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En Mac/Linux
    source venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install django
    ```

4.  **Aplicar migraciones**:
    ```bash
    python manage.py migrate
    ```

5.  **Ejecutar el servidor de desarrollo**:
    ```bash
    python manage.py runserver
    ```

    El proyecto estará disponible en `http://127.0.0.1:8000/`.

## Uso

- Acceder al panel de administración en `http://127.0.0.1:8000/admin/` (requiere crear un superusuario con `python manage.py createsuperuser`).
- Desde allí se pueden gestionar usuarios, canchas y reservas.

## Contribución

1.  Hacer un Fork del proyecto.
2.  Crear una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3.  Hacer commit de tus cambios (`git commit -m 'Aañadir nueva funcionalidad'`).
4.  Hacer push a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Abrir un Pull Request.
