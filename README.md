# APP_SALON - Gestión de citas para salón de belleza

Aplicación full-stack con **FastAPI + PostgreSQL (Neon) + SQLAlchemy + JWT + TailwindCSS** lista para deploy en Railway.

## Características
- Registro/login con email o teléfono.
- Roles: cliente y admin.
- Dashboard con próxima cita destacada y contador de citas del día.
- Validaciones de negocio en backend:
  - No se agenda en pasado ni el mismo día.
  - Sin doble reserva en la misma fecha/hora.
- Gestión admin de citas y servicios.
- Paginación en panel admin.
- Estados visuales de cita.
- Alembic para migraciones.

## Estructura
```
/app
  main.py
  models.py
  schemas.py
  database.py
  auth.py
  /routes
/templates
/static
/alembic
Dockerfile
requirements.txt
```

## Variables de entorno
Crear `.env` en Railway o localmente:

- `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB`
- `SECRET_KEY=clave-super-segura`
- `ACCESS_TOKEN_EXPIRE_MINUTES=120`
- `CORS_ORIGINS=*`
- `PORT=8000`

## Ejecutar local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Deploy en Railway con Neon
1. Crear proyecto en [Neon](https://neon.tech) y copiar connection string.
2. Crear proyecto en Railway y conectar repo.
3. En Variables de Railway, configurar:
   - `DATABASE_URL` (Neon)
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `CORS_ORIGINS`
4. Railway detectará `Dockerfile` y desplegará automáticamente.
5. Ejecutar migraciones:
   - Opción A: `railway run alembic upgrade head`
   - Opción B: en pre-deploy step.

## Seguridad
- Contraseñas hasheadas con bcrypt (`passlib`).
- JWT con expiración.
- SQL injection mitigado al usar SQLAlchemy ORM con parámetros.

## Usuario admin
Crear manualmente un usuario admin actualizando el campo `rol` a `admin` en la tabla `usuarios`.
