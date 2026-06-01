# AgroManager - Quick Start (5 minutos)

## 🚀 Start en 5 Pasos

### Paso 1: Instalar Backend
```bash
cd c:\Users\danie\Desktop\tfg\tfg-claude
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 2: Arrancar Backend
```bash
uvicorn app.main:app --reload --port 8000
```

✅ Backend corriendo en http://localhost:8000

### Paso 3: Instalar Frontend (Nueva Terminal)
```bash
cd c:\Users\danie\Desktop\tfg\tfg-claude\frontend
npm install
```

### Paso 4: Arrancar Frontend
```bash
npm run dev
```

✅ Frontend corriendo en http://localhost:5173

### Paso 5: Probar
```bash
# En otra terminal con venv activado
python -m unittest tests.test_api.TestHealth -v
```

✅ Tests verdes = Todo funciona

---

## 🧪 Pruebas Rápidas (Postman/cURL)

### Registrar
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!","name":"Test"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}'
```

Copia el `access_token`.

### Acceder Protegido
```bash
curl -X GET http://localhost:8000/users/1 \
  -H "Authorization: Bearer {token}"
```

---

## 📚 Documentación

- **README.md** - Documentación completa
- **SETUP.md** - Comandos detallados
- **API Docs** - http://localhost:8000/docs (Swagger UI)

---

## ✅ Criterios Met

- ✅ Backend + Frontend funcionando
- ✅ Autenticación JWT
- ✅ Permisos usuarios/admin
- ✅ Modelos y schemas
- ✅ Tests automáticos
- ✅ BD SQLite local (sin deps externas)

---

**¡Listo! Reconstrucción piloto completada** 🎉
