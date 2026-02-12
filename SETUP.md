# Guía de Configuración para Colaboradores

Esta guía detalla los pasos necesarios para configurar el entorno de desarrollo y poner en marcha el proyecto desde cero.

## Requisitos Previos

- **Python 3.8+**: Asegúrate de tener Python instalado. Puedes verificarlo con `python --version`.
- **Git**: Para clonar el repositorio y gestionar ramas.

## Pasos para la Configuración

### 1. Clonar el Proyecto
Si ya tienes acceso al repositorio, clónalo en tu máquina local:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

### 2. Crear y Activar el Entorno Virtual
Es fundamental usar un entorno virtual para mantener las dependencias aisladas.

**En Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
Una vez activado el entorno virtual, instala Django (y cualquier otra dependencia futura):
```bash
pip install django
```
*Nota: Próximamente se añadirá un archivo `requirements.txt` para simplificar este paso.*

### 4. Configurar la Base de Datos
El proyecto utiliza SQLite por defecto para desarrollo. Ejecuta las migraciones para crear las tablas en tu base de datos local:
```bash
python manage.py migrate
```

### 5. Crear un Superusuario (Administrador)
Para acceder al panel de administración de Django y gestionar los datos:
```bash
python manage.py createsuperuser
```
Sigue las instrucciones en la consola para definir tu `username`, `email` y `password`.

### 6. Ejecutar el Servidor de Desarrollo
Inicia el servidor local:
```bash
python manage.py runserver
```
El proyecto estará disponible en [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
Puedes acceder al panel de administración en [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

---

## Verificación del Entorno

Para confirmar que todo está correctamente configurado, ejecuta los tests unitarios:
```bash
python manage.py test reservas.tests_services
```
Si ves un mensaje de `OK`, tu entorno está listo para empezar a desarrollar.

## Flujo de Trabajo Sugerido

1.  **Sincronizar**: Siempre haz un `git pull` de la rama principal antes de empezar.
2.  **Ramas**: Crea una rama para cada nueva funcionalidad o corrección: `git checkout -b feature/nombre-funcionalidad`.
3.  **Calidad**: Asegúrate de que los tests pasen antes de subir tus cambios.
4.  **Pull Requests**: Sube tu rama y abre un PR para revisión.
