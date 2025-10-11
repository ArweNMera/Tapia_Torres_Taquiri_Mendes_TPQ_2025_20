# Configurar Túnel Cloudflare para Modelo ML

## 🎯 Objetivo
Exponer el modelo ML en `modelo.areallc.tech` usando Cloudflare Tunnel

## 📋 Pasos

### 1. Crear el Túnel en Cloudflare

```bash
# Crear túnel llamado "modelo"
cloudflared tunnel create modelo
```

Esto generará:
- Un archivo de credenciales en `~/.cloudflared/`
- Un UUID del túnel

### 2. Configurar el Túnel

Crea el archivo de configuración:

```bash
nano ~/.cloudflared/config.yml
```

Agrega esta configuración:

```yaml
tunnel: <TUNNEL_UUID>
credentials-file: /Users/phol1201/.cloudflared/<TUNNEL_UUID>.json

ingress:
  # Modelo ML
  - hostname: modelo.areallc.tech
    service: http://localhost:8001
  
  # Backend API (ya existente)
  - hostname: api.areallc.tech
    service: http://localhost:8000
  
  # Catch-all rule (requerido)
  - service: http_status:404
```

### 3. Configurar DNS en Cloudflare

```bash
# Crear registro DNS para el modelo
cloudflared tunnel route dns modelo modelo.areallc.tech
```

### 4. Iniciar el Túnel como Servicio

```bash
# Instalar como servicio
sudo cloudflared service install

# Iniciar el servicio
sudo launchctl start com.cloudflare.cloudflared
```

### 5. Verificar que Funciona

```bash
# Ver logs del túnel
cloudflared tunnel info modelo

# Probar el endpoint
curl https://modelo.areallc.tech/health
```

## 🔧 Comandos Útiles

```bash
# Ver túneles activos
cloudflared tunnel list

# Ver información del túnel
cloudflared tunnel info modelo

# Detener el servicio
sudo launchctl stop com.cloudflare.cloudflared

# Ver logs
sudo launchctl list | grep cloudflared
```

## ✅ Verificación Final

1. **Modelo ML**: https://modelo.areallc.tech/health
2. **Documentación**: https://modelo.areallc.tech/docs
3. **Endpoint de prueba**: 
   ```bash
   curl -X POST "https://modelo.areallc.tech/ml/predict_direct" \
     -H "Content-Type: application/json" \
     -d '{"age_months": 84, "sex": "F", "weight_kg": 30.0, "height_cm": 120.0}'
   ```

## 🚀 Iniciar el Modelo ML

Asegúrate de que el modelo esté corriendo en el puerto 8001:

```bash
cd modelo/ml-recomendator
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
