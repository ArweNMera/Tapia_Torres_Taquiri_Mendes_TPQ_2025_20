# Inventario de SQL incrustado para migrar a procedimientos almacenados

## Contexto
- Este listado da seguimiento a los puntos que faltan para alinear el backend con la estrategia descrita en `ARQUITECTURA_HEXAGONAL.md`: concentrar la lógica de persistencia en adaptadores secundarios y reducir SQL embebido en capas superiores.
- Cada caso indica dónde existe SQL literal, qué hace y la propuesta de moverlo a un procedimiento almacenado (a definir en `BaseDatos/database/procedimientos.sql` o archivos relacionados).

## Repositorios de infraestructura
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:16` · `obtener_perfil_nutricional` migrado a `sp_perfil_nutricional_vigente`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:69` · `crear_menu` migrado a `sp_menus_crear`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:85` · `agregar_item_menu` utiliza `sp_menus_items_agregar`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:106` · `actualizar_calorias_menu` delega en `sp_menus_actualizar_kcal`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:114` · `obtener_datos_nino` usa `sp_ninos_datos_basicos`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:134` · `obtener_ingredientes_receta` usa `sp_recetas_ingredientes`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:148` · `listar_menus_nino` se apoya en `sp_menus_listar`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:172` · `obtener_detalle_menu` ahora usa `sp_menus_detalle`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:186` · `obtener_items_menu` migrado a `sp_menus_items_listar`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:202` · `actualizar_estado_menu` usa `sp_menus_cambiar_estado`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:306` · `_obtener_recetas_disponibles` delega en `sp_recetas_disponibles`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:405` · `_generar_plan_fallback` usa `sp_recetas_aleatorias`.
- ✅ `app/infrastructure/repositories/planes_comidas_repo.py:451` · `_obtener_detalle_receta` ahora depende de `sp_recetas_detalle` y `sp_recetas_nutrientes`.
- ✅ `app/infrastructure/repositories/preferencias_repo.py:20` · `obtener_preferencias_nino` usa `sp_preferencias_listar`.
- ✅ `app/infrastructure/repositories/preferencias_repo.py:58` · `eliminar_preferencia` usa `sp_preferencias_desactivar`.
- ✅ `app/infrastructure/repositories/preferencias_repo.py:70` · `obtener_resumen_preferencias` migrado a `sp_preferencias_resumen`.
- ✅ `app/infrastructure/repositories/usuarios_repo.py:239` · `anonymize_user_account` usa `sp_usuarios_anonimizar`.
- ✅ `app/infrastructure/repositories/usuarios_repo.py:293` · `get_rol_nombre_by_id` delega en `sp_roles_nombre_por_id`.
- ✅ `app/infrastructure/repositories/ninos_repo.py:426` · `evaluar_estado_nutricional` obtiene recomendaciones vía `sp_evaluaciones_recomendaciones`.

## Endpoints (capa API) con SQL embebido
- ✅ `app/api/v1/endpoints/planes_comidas.py:274` · `eliminar_alergia_nino` canaliza `NinosRepository.eliminar_alergia` (`sp_ninos_alergia_eliminar`).
- ✅ `app/api/v1/endpoints/planes_comidas.py:295` · `obtener_comidas_favoritas_nino` usa `PlanesComidasRepository.listar_comidas_favoritas` (`sp_comidas_favoritas_listar`).
- ✅ `app/api/v1/endpoints/planes_comidas.py:332` · `agregar_comida_favorita_nino` migrado a `sp_comidas_favoritas_agregar`.
- ✅ `app/api/v1/endpoints/planes_comidas.py:351` · `eliminar_comida_favorita_nino` usa `sp_comidas_favoritas_eliminar`.
- ✅ `app/api/v1/endpoints/planes_comidas.py:371` · `buscar_recetas_disponibles` consulta `sp_recetas_buscar`.
- ✅ `app/api/v1/endpoints/planes_comidas.py:421` · `obtener_detalle_receta` se apoya en repositorio (procedimientos `sp_recetas_detalle`, `sp_recetas_ingredientes`, `sp_recetas_nutrientes`).
- ✅ `app/api/v1/endpoints/admin.py:72` · `listar_usuarios` usa `UsuariosService.list_users_admin` (`sp_admin_usuarios_listar`).
- ✅ `app/api/v1/endpoints/admin.py:119` · `resetear_contrasena_usuario` delega en `sp_admin_resetear_contrasena`.
- ✅ `app/api/v1/endpoints/admin.py:161` · `toggle_usuario_activo` usa `sp_admin_toggle_usuario` vía servicio.
- ✅ `app/api/v1/endpoints/ninos.py:274` · `eliminar_alergia_nino` reutiliza `NinosRepository.eliminar_alergia`.

## Recomendaciones operativas
- Centralizar los nuevos procedimientos en `procedimientos.sql` (y subdividir por dominio si es necesario) asegurando pruebas en `BaseDatos/database`.
- Una vez creados los SP, actualizar los repositorios para que cada método llame al procedimiento y exponer esos métodos a los endpoints, eliminando SQL literal de la capa API.
- Mantener consistencia con la arquitectura hexagonal: la API debe depender solo de servicios/aplicación, éstos de interfaces de dominio y únicamente la infraestructura manejará las llamadas a los SP.
- Documentar cada nuevo SP (parámetros, propósito, retorno) para que el equipo de base de datos valide performance, índices y seguridad.
