"""
Servicio de aplicación para gestión de niños.
Contiene los casos de uso relacionados con niños y su información nutricional.
"""
from typing import Optional, List, Dict, Any
from datetime import date
from fastapi import HTTPException

from app.domain.interfaces.ninos_repository import INinosRepository
from app.domain.interfaces.usuarios_repository import IUsuariosRepository
from app.domain.utils.nutrition_recommendations import generar_recomendaciones_nutricionales
from app.schemas.ninos import NinoCreate, NinoUpdate, AnthropometryCreate, AlergiaCreate


class NinosService:
    """
    Servicio de aplicación para casos de uso de niños.
    Coordina entre repositorios y aplica reglas de negocio.
    """
    
    def __init__(
        self, 
        ninos_repository: INinosRepository,
        usuarios_repository: IUsuariosRepository
    ):
        self.ninos_repo = ninos_repository
        self.usuarios_repo = usuarios_repository
    
    def crear_nino(
        self, 
        nino_data: NinoCreate, 
        usr_id_tutor: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Crear un nuevo niño.
        
        Args:
            nino_data: Datos del niño a crear
            usr_id_tutor: ID del tutor del niño
            
        Returns:
            Niño creado con su información
            
        Raises:
            HTTPException: Si el tutor no existe o no tiene permisos
        """
        # Validar que el tutor existe y está activo
        tutor = self.usuarios_repo.get_user_by_id(usr_id_tutor)
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor no encontrado")
        
        if not tutor.usr_activo:
            raise HTTPException(status_code=403, detail="Tutor inactivo")
        
        # Validar rol del tutor
        rol_codigo = self.usuarios_repo.get_role_code_by_id(tutor.rol_id)
        roles_validos = ("PADRE", "PADRES", "TUTOR", "ADMIN", "SUPERADMIN")
        
        if rol_codigo not in roles_validos:
            raise HTTPException(
                status_code=403, 
                detail="El usuario no tiene permisos para crear niños"
            )
        
        # Calcular si el niño puede autogestionar (>= 13 años)
        today = date.today()
        edad_anios = today.year - nino_data.nin_fecha_nac.year - (
            (today.month, today.day) < (nino_data.nin_fecha_nac.month, nino_data.nin_fecha_nac.day)
        )
        
        # Preparar datos con autogestión
        nino_dict = nino_data.model_dump()
        nino_dict["usr_id_tutor"] = usr_id_tutor
        nino_dict["nin_autogestiona"] = edad_anios >= 13
        
        try:
            return self.ninos_repo.crear_nino(nino_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al crear niño: {str(e)}"
            )
    
    def actualizar_nino(
        self, 
        nin_id: int, 
        nino_data: NinoUpdate,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Actualizar datos de un niño.
        
        Args:
            nin_id: ID del niño
            nino_data: Datos a actualizar
            usr_id_solicitante: ID del usuario que solicita la actualización
            
        Returns:
            Niño actualizado
            
        Raises:
            HTTPException: Si no tiene permisos o el niño no existe
        """
        # Obtener niño actual
        nino_actual = self.ninos_repo.obtener_nino(nin_id)
        if not nino_actual:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        # Validar permisos: debe ser el tutor o admin
        if not self._puede_gestionar_nino(usr_id_solicitante, nino_actual.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para actualizar este niño"
            )
        
        try:
            nino_dict = nino_data.model_dump(exclude_unset=True)
            return self.ninos_repo.actualizar_nino(nin_id, nino_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al actualizar niño: {str(e)}"
            )
    
    def obtener_nino(
        self, 
        nin_id: int,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Obtener información de un niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita la información
            
        Returns:
            Información del niño
            
        Raises:
            HTTPException: Si no tiene permisos o el niño no existe
        """
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        # Validar permisos
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver este niño"
            )
        
        return nino
    
    def listar_ninos_tutor(self, usr_id_tutor: int) -> List[Dict[str, Any]]:
        """
        Caso de uso: Listar niños de un tutor.
        
        Args:
            usr_id_tutor: ID del tutor
            
        Returns:
            Lista de niños del tutor con estructura anidada
        """
        try:
            ninos_data = self.ninos_repo.listar_ninos_tutor(usr_id_tutor)
            
            # Transformar a estructura esperada por el frontend
            result = []
            for nino_data in ninos_data:
                # Obtener antropometrías del niño
                antropometrias = self.ninos_repo.get_antropometrias_by_nino(nino_data['nin_id'], limit=10)
                
                # Obtener alergias del niño
                alergias = self.ninos_repo.obtener_alergias(nino_data['nin_id'])
                
                # Obtener último estado nutricional y transformar
                ultimo_estado = None
                if antropometrias:
                    try:
                        estado_raw = self.ninos_repo.evaluar_estado_nutricional(nino_data['nin_id'])
                        if estado_raw:
                            # Transformar al formato esperado por NutritionalStatusResponse
                            clasificacion = estado_raw.get("en_clasificacion", "")
                            imc = estado_raw.get("imc_calculado", 0)
                            edad_meses = nino_data.get("nin_edad_meses", 0)
                            
                            ultimo_estado = {
                                "imc": imc,
                                "z_score_imc": estado_raw.get("en_z_score_imc"),
                                "classification": clasificacion,
                                "percentile": estado_raw.get("percentil_calculado"),
                                "recommendations": generar_recomendaciones_nutricionales(clasificacion, imc, edad_meses),
                                "risk_level": estado_raw.get("en_nivel_riesgo")
                            }
                    except:
                        pass
                
                # Crear estructura anidada
                nino_completo = {
                    "nino": nino_data,
                    "antropometrias": antropometrias,
                    "alergias": alergias,
                    "ultimo_estado_nutricional": ultimo_estado
                }
                result.append(nino_completo)
            
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al listar niños: {str(e)}"
            )
    
    def agregar_antropometria(
        self,
        nin_id: int,
        ant_data: AnthropometryCreate,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Agregar medidas antropométricas a un niño.
        
        Args:
            nin_id: ID del niño
            ant_data: Datos antropométricos
            usr_id_solicitante: ID del usuario que agrega los datos
            
        Returns:
            Antropometría agregada
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar que el niño existe y el usuario tiene permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para agregar datos antropométricos"
            )
        
        try:
            ant_dict = ant_data.model_dump()
            return self.ninos_repo.agregar_antropometria(nin_id, ant_dict)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al agregar antropometría: {str(e)}"
            )
    
    def evaluar_estado_nutricional(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Evaluar estado nutricional del niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita la evaluación
            
        Returns:
            Evaluación nutricional
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para evaluar este niño"
            )
        
        try:
            estado_raw = self.ninos_repo.evaluar_estado_nutricional(nin_id)
            
            # Transformar al formato esperado por NutritionalStatusResponse
            if estado_raw:
                clasificacion = estado_raw.get("en_clasificacion", "")
                imc = estado_raw.get("imc_calculado", 0)
                edad_meses = nino.get("nin_edad_meses", 0)
                
                return {
                    "imc": imc,
                    "z_score_imc": estado_raw.get("en_z_score_imc"),
                    "classification": clasificacion,
                    "percentile": estado_raw.get("percentil_calculado"),
                    "recommendations": generar_recomendaciones_nutricionales(clasificacion, imc, edad_meses),
                    "risk_level": estado_raw.get("en_nivel_riesgo")
                }
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al evaluar estado nutricional: {str(e)}"
            )
    
    def obtener_perfil_completo(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Obtener perfil completo del niño con última antropometría.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita el perfil
            
        Returns:
            Perfil completo del niño
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver el perfil de este niño"
            )
        
        try:
            return self.ninos_repo.get_perfil_completo(nin_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al obtener perfil: {str(e)}"
            )
    
    def agregar_alergia(
        self,
        nin_id: int,
        alergia_data: AlergiaCreate,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Agregar alergia a un niño.
        
        Args:
            nin_id: ID del niño
            alergia_data: Datos de la alergia (AlergiaCreate schema)
            usr_id_solicitante: ID del usuario que agrega la alergia
            
        Returns:
            Alergia agregada
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para agregar alergias a este niño"
            )
        
        try:
            # Extraer campos del schema para pasarlos al repositorio
            ta_codigo = alergia_data.ta_codigo
            severidad = alergia_data.severidad if hasattr(alergia_data, 'severidad') else "LEVE"
            
            # El repositorio devuelve una lista de alergias, tomamos la primera (recién agregada)
            alergias = self.ninos_repo.agregar_alergia(nin_id, ta_codigo, severidad)
            
            if alergias and len(alergias) > 0:
                # Buscar la alergia con el código que acabamos de agregar
                for alergia in alergias:
                    if alergia.get("ta_codigo") == ta_codigo:
                        return alergia
                # Si no la encontramos, devolver la primera
                return alergias[0]
            
            raise HTTPException(
                status_code=500,
                detail="No se pudo recuperar la alergia agregada"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al agregar alergia: {str(e)}"
            )
    
    def obtener_ultima_antropometria(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> Optional[Dict[str, Any]]:
        """
        Caso de uso: Obtener la última medición antropométrica de un niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita los datos
            
        Returns:
            Última antropometría o None si no tiene
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver los datos antropométricos de este niño"
            )
        
        try:
            antropometrias = self.ninos_repo.get_antropometrias_by_nino(nin_id, limit=1)
            return antropometrias[0] if antropometrias else None
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al obtener última antropometría: {str(e)}"
            )
    
    def obtener_alergias(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> List[Dict[str, Any]]:
        """
        Caso de uso: Obtener alergias de un niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita las alergias
            
        Returns:
            Lista de alergias
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para ver las alergias de este niño"
            )
        
        try:
            return self.ninos_repo.obtener_alergias(nin_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al obtener alergias: {str(e)}"
            )
    
    def eliminar_alergia(
        self,
        nin_id: int,
        na_id: int,
        usr_id_solicitante: int
    ) -> List[Dict[str, Any]]:
        """
        Caso de uso: Eliminar una alergia de un niño.
        
        Args:
            nin_id: ID del niño
            na_id: ID de la alergia a eliminar
            usr_id_solicitante: ID del usuario que solicita la eliminación
            
        Returns:
            Lista de alergias activas restantes del niño
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar permisos
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        if not self._puede_gestionar_nino(usr_id_solicitante, nino.get("usr_id_tutor")):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para eliminar alergias de este niño"
            )
        
        try:
            return self.ninos_repo.eliminar_alergia(na_id, nin_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al eliminar alergia: {str(e)}"
            )
    
    def buscar_tipos_alergias(
        self,
        query: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Caso de uso: Buscar tipos de alergias disponibles.
        
        Args:
            query: Texto de búsqueda (opcional)
            limit: Límite de resultados
            
        Returns:
            Lista de tipos de alergias
        """
        try:
            return self.ninos_repo.obtener_tipos_alergias(query, limit)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al buscar tipos de alergias: {str(e)}"
            )
    
    def asignar_tutor(
        self,
        nin_id: int,
        nuevo_tutor_id: int,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Asignar o cambiar tutor de un niño.
        
        Args:
            nin_id: ID del niño
            nuevo_tutor_id: ID del nuevo tutor
            usr_id_solicitante: ID del usuario que solicita el cambio
            
        Returns:
            Niño con tutor actualizado
            
        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Validar que el niño existe
        nino = self.ninos_repo.obtener_nino(nin_id)
        if not nino:
            raise HTTPException(status_code=404, detail="Niño no encontrado")
        
        # Solo el tutor actual o admin puede cambiar el tutor
        es_admin = self._es_admin(usr_id_solicitante)
        es_tutor_actual = nino.get("usr_id_tutor") == usr_id_solicitante
        
        if not (es_admin or es_tutor_actual):
            raise HTTPException(
                status_code=403, 
                detail="No tienes permisos para cambiar el tutor de este niño"
            )
        
        # Validar que el nuevo tutor existe y tiene rol válido
        nuevo_tutor = self.usuarios_repo.get_user_by_id(nuevo_tutor_id)
        if not nuevo_tutor:
            raise HTTPException(status_code=404, detail="Nuevo tutor no encontrado")
        
        if not nuevo_tutor.usr_activo:
            raise HTTPException(status_code=403, detail="El nuevo tutor está inactivo")
        
        rol_codigo = self.usuarios_repo.get_role_code_by_id(nuevo_tutor.rol_id)
        roles_validos = ("PADRE", "PADRES", "TUTOR", "ADMIN", "SUPERADMIN")
        
        if rol_codigo not in roles_validos:
            raise HTTPException(
                status_code=403, 
                detail="El usuario no tiene un rol válido para ser tutor"
            )
        
        try:
            return self.ninos_repo.asignar_tutor(nin_id, nuevo_tutor_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al asignar tutor: {str(e)}"
            )
    
    def obtener_nino_completo(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> Dict[str, Any]:
        """
        Caso de uso: Obtener un niño con todos sus datos antropométricos,
        alergias y estado nutricional.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita
            
        Returns:
            Dict con todos los datos del niño
            
        Raises:
            HTTPException: Si no tiene permisos o no existe
        """
        # Validar acceso
        nino = self.obtener_nino(nin_id, usr_id_solicitante)
        
        # Obtener datos relacionados
        antropometrias = self.ninos_repo.get_antropometrias_by_nino(nin_id, limit=10)
        alergias = self.ninos_repo.obtener_alergias(nin_id)
        estado_nutricional_raw = self.ninos_repo.evaluar_estado_nutricional(nin_id)
        
        # Transformar estado nutricional para coincidir con NutritionalStatusResponse schema
        estado_nutricional = None
        if estado_nutricional_raw:
            clasificacion = estado_nutricional_raw.get("en_clasificacion", "")
            imc = estado_nutricional_raw.get("imc_calculado", 0)
            edad_meses = nino.get("nin_edad_meses", 0)
            
            estado_nutricional = {
                "imc": imc,
                "z_score_imc": estado_nutricional_raw.get("en_z_score_imc"),
                "classification": clasificacion,
                "percentile": estado_nutricional_raw.get("percentil_calculado"),
                "recommendations": generar_recomendaciones_nutricionales(clasificacion, imc, edad_meses),
                "risk_level": estado_nutricional_raw.get("en_nivel_riesgo")
            }
        
        return {
            "nino": nino,
            "antropometrias": antropometrias,
            "alergias": alergias,
            "ultimo_estado_nutricional": estado_nutricional
        }
    
    def obtener_historial_antropometrico(
        self,
        nin_id: int,
        usr_id_solicitante: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Caso de uso: Obtener historial de medidas antropométricas de un niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita
            limit: Número máximo de registros
            
        Returns:
            Lista de medidas antropométricas ordenadas por fecha
            
        Raises:
            HTTPException: Si no tiene permisos
        """
        # Validar acceso
        _ = self.obtener_nino(nin_id, usr_id_solicitante)
        
        try:
            return self.ninos_repo.get_antropometrias_by_nino(nin_id, limit=limit)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener historial antropométrico: {str(e)}"
            )
    
    def obtener_alergias_nino(
        self,
        nin_id: int,
        usr_id_solicitante: int
    ) -> List[Dict[str, Any]]:
        """
        Caso de uso: Obtener todas las alergias de un niño.
        
        Args:
            nin_id: ID del niño
            usr_id_solicitante: ID del usuario que solicita
            
        Returns:
            Lista de alergias del niño
            
        Raises:
            HTTPException: Si no tiene permisos
        """
        # Validar acceso
        _ = self.obtener_nino(nin_id, usr_id_solicitante)
        
        try:
            return self.ninos_repo.obtener_alergias(nin_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener alergias: {str(e)}"
            )
    
    # ========== Métodos privados de validación ==========
    
    def _puede_gestionar_nino(self, usr_id: int, tutor_id: Optional[int]) -> bool:
        """
        Verifica si un usuario puede gestionar un niño.
        Puede si es el tutor o es admin.
        """
        if usr_id == tutor_id:
            return True
        
        return self._es_admin(usr_id)
    
    def _es_admin(self, usr_id: int) -> bool:
        """Verifica si un usuario es administrador"""
        user = self.usuarios_repo.get_user_by_id(usr_id)
        if not user:
            return False
        
        rol_codigo = self.usuarios_repo.get_role_code_by_id(user.rol_id)
        return rol_codigo in ("ADMIN", "SUPERADMIN")
