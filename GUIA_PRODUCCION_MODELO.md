# 🚀 Guía Completa: Modelo ML en Producción

## Paso 1: Entrenar el Modelo

```bash
cd modelo/ml-recomendator
source venv/bin/activate
./ENTRENAR_AHORA.sh
```

## Paso 2: Configurar Cloudflare Tunnel

```bash
# 1. Crear túnel
cloudflared tunnel create modelo

# 2. Configurar DNS
cloudflared tunnel route dns modelo modelo.areallc.tech

# 3. Ejecutar script de configuración
chmod +x setup_tunel_modelo.sh
./setup_tunel_modelo.sh
```

## Paso 3: Instalar Modelo como Servicio

```bash
cd modelo/ml-recomendator
chmod +x instalar_servicio.sh
./instalar_servicio.sh
```

## Paso 4: Verificar

```bash
# Local
curl http://localhost:8001/health

# Producción
curl https://modelo.areallc.tech/health
```

## 🎯 URLs Finales

- **Modelo ML**: https://modelo.areallc.tech
- **Documentación**: https://modelo.areallc.tech/docs
- **Health Check**: https://modelo.areallc.tech/health

## 🔧 Comandos Útiles

```bash
# Ver logs del modelo
tail -f modelo/ml-recomendator/logs/modelo-ml.log

# Reiniciar servicio
launchctl stop com.areallc.modelo-ml
launchctl start com.areallc.modelo-ml

# Ver túnel
cloudflared tunnel info modelo
```
