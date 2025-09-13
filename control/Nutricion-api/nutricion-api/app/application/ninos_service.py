from sqlalchemy.orm import Session
from app.schemas.usuarios import UserRegister
from app.schemas.auth import Token
from app.schemas.ninos import (
    NinoCreate, NinoUpdate, NinoResponse, AnthropometryCreate, 
    AnthropometryResponse, NutritionalStatusResponse, 
    CreateChildProfileRequest, CreateChildProfileResponse,
    NinoWithAnthropometry, AlergiaCreate, AlergiaResponse,
    TipoAlergiaCreate, TipoAlergiaResponse
)
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.infrastructure.repositories.ninos_repo import NinosRepository
from app.application.auth_service import create_access_token
from typing import List, Dict, Any
from datetime import date, datetime
from fastapi import HTTPException

def register_user(db: Session, user_register: UserRegister):
    repo = UsuariosRepository(db)
    result = repo.insert_user(user_register)
    
    # Generar token automáticamente después del registro
    access_token = create_access_token(data={"sub": user_register.usuario})
    
    return Token(access_token=access_token, token_type="bearer")

def calculate_nutritional_status_who(db: Session, nin_id: int) -> NutritionalStatusResponse:
    """
    Calcula el estado nutricional usando estándares WHO 2006/2007 
    mediante procedimiento almacenado sp_evaluar_estado_nutricional
    """
    repo = NinosRepository(db)
    
    try:
        resultado = repo.evaluar_estado_nutricional(nin_id)
        if not resultado:
            raise HTTPException(status_code=400, detail="No se pudo evaluar el estado nutricional")
        
        # Mapear clasificación a recomendaciones
        clasificacion = resultado["en_clasificacion"]
        nivel_riesgo = resultado["en_nivel_riesgo"]
        
        recommendations = []
        if clasificacion == "DESNUTRICION_SEVERA":
            recommendations = [
                "Consultar inmediatamente con un pediatra especialista",
                "Evaluación médica integral urgente",
                "Plan de recuperación nutricional supervisado"
            ]
        elif clasificacion == "DESNUTRICION":
            recommendations = [
                "Consultar con pediatra y nutricionista",
                "Incrementar aporte calórico y proteico",
                "Seguimiento médico frecuente"
            ]
        elif clasificacion == "RIESGO_DESNUTRICION":
            recommendations = [
                "Mejorar calidad de la alimentación",
                "Aumentar frecuencia de comidas",
                "Controles médicos regulares"
            ]
        elif clasificacion == "NORMAL":
            recommendations = [
                "Mantener alimentación balanceada",
                "Promover actividad física apropiada",
                "Controles de crecimiento regulares"
            ]
        elif clasificacion == "SOBREPESO":
            recommendations = [
                "Reducir alimentos procesados y azúcares",
                "Aumentar consumo de frutas y verduras",
                "Incrementar actividad física diaria"
            ]
        elif clasificacion == "OBESIDAD":
            recommendations = [
                "Evaluación médica especializada",
                "Plan nutricional personalizado",
                "Programa de ejercicio supervisado"
            ]
        else:
            recommendations = ["Consultar con profesional de la salud"]
        
        return NutritionalStatusResponse(
            imc=resultado["imc_calculado"],
            z_score_imc=resultado["en_z_score_imc"],
            classification=clasificacion,
            percentile=resultado["percentil_calculado"],
            recommendations=recommendations,
            risk_level=nivel_riesgo
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al evaluar estado nutricional: {str(e)}")

def calculate_nutritional_status(weight_kg: float, height_cm: float, age_months: int, sex: str) -> NutritionalStatusResponse:
    """
    Calcula el estado nutricional usando estándares básicos
    (DEPRECATED - usar calculate_nutritional_status_who para WHO standards)
    """
    # Calcular IMC
    height_m = height_cm / 100
    imc = weight_kg / (height_m ** 2)
    
    # Clasificación simplificada por edad y sexo
    if age_months < 24:  # Menores de 2 años
        if imc < 13:
            classification = "bajo_peso"
            risk_level = "ALTO"
            recommendations = [
                "Consultar inmediatamente con un pediatra",
                "Aumentar frecuencia de comidas nutritivas",
                "Evaluar causas de desnutrición"
            ]
        elif imc <= 17:
            classification = "normal"
            risk_level = "BAJO"
            recommendations = [
                "Mantener alimentación balanceada",
                "Seguimiento regular del crecimiento",
                "Continuar lactancia materna si aplica"
            ]
        elif imc <= 19:
            classification = "sobrepeso"
            risk_level = "MODERADO"
            recommendations = [
                "Controlar ingesta de azúcares",
                "Aumentar actividad física apropiada para la edad",
                "Consultar con nutricionista"
            ]
        else:
            classification = "obesidad"
            risk_level = "ALTO"
            recommendations = [
                "Evaluación médica integral",
                "Plan de alimentación especializado",
                "Actividad física supervisada"
            ]
    else:  # Mayores de 2 años
        if imc < 14:
            classification = "bajo_peso"
            risk_level = "ALTO"
            recommendations = [
                "Evaluación médica urgente",
                "Incrementar aporte calórico y proteico",
                "Suplementación nutricional si es necesaria"
            ]
        elif imc <= 18:
            classification = "normal"
            risk_level = "BAJO"
            recommendations = [
                "Alimentación variada y balanceada",
                "Actividad física regular",
                "Controles de crecimiento periódicos"
            ]
        elif imc <= 20:
            classification = "sobrepeso"
            risk_level = "MODERADO"
            recommendations = [
                "Reducir alimentos procesados",
                "Aumentar consumo de frutas y verduras",
                "Promover actividad física diaria"
            ]
        else:
            classification = "obesidad"
            risk_level = "ALTO"
            recommendations = [
                "Evaluación médica especializada",
                "Plan nutricional personalizado",
                "Programa de ejercicio supervisado"
            ]
    
    # Z-score simplificado (en el futuro usar tablas OMS reales)
    if age_months < 24:
        z_score_ref = 15.5
    else:
        z_score_ref = 16.0
    
    z_score = (imc - z_score_ref) / 1.5
    percentile = min(95, max(5, 50 + (z_score * 15)))
    
    return NutritionalStatusResponse(
        imc=round(imc, 2),
        z_score_imc=round(z_score, 2),
        classification=classification,
        percentile=round(percentile, 1),
        recommendations=recommendations,
        risk_level=risk_level
    )

def create_child_profile(db: Session, profile_data: CreateChildProfileRequest, usr_id_tutor: int) -> CreateChildProfileResponse:
    """Crear perfil completo de niño con datos antropométricos iniciales"""
    repo = NinosRepository(db)
    
    try:
        # Crear el niño
        nino_dict = repo.create_nino(profile_data.nino, usr_id_tutor)
        if not nino_dict:
            raise HTTPException(status_code=400, detail="Error al crear el perfil del niño")
        
        nino_response = NinoResponse(**nino_dict)
        
        # Agregar antropometría inicial
        antropo_dict = repo.create_antropometria(nino_dict["nin_id"], profile_data.antropometria)
        if not antropo_dict:
            raise HTTPException(status_code=400, detail="Error al agregar datos antropométricos")
        
        antropo_response = AnthropometryResponse(**antropo_dict)
        
        # Calcular estado nutricional usando WHO standards
        estado_nutricional = calculate_nutritional_status_who(db, nino_dict["nin_id"])
        
        return CreateChildProfileResponse(
            nino=nino_response,
            antropometria=antropo_response,
            estado_nutricional=estado_nutricional
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

def get_children_by_tutor(db: Session, usr_id_tutor: int) -> List[NinoWithAnthropometry]:
    """Obtener todos los niños de un tutor con sus datos antropométricos"""
    repo = NinosRepository(db)
    
    ninos_dict = repo.get_ninos_by_tutor(usr_id_tutor)
    result = []
    
    for nino_dict in ninos_dict:
        nino_response = NinoResponse(**nino_dict)
        
        # Obtener antropometrías del niño
        antropometrias_dict = repo.get_antropometrias_by_nino(nino_dict["nin_id"])
        antropometrias = [AnthropometryResponse(**ant) for ant in antropometrias_dict]
        
        # Obtener alergias del niño
        alergias_dict = repo.obtener_alergias(nino_dict["nin_id"])
        alergias = [AlergiaResponse(**alergia) for alergia in alergias_dict]
        
        # Calcular estado nutricional actual si hay datos
        estado_nutricional = None
        if antropometrias:
            # Usar evaluación WHO para el último registro
            estado_nutricional = calculate_nutritional_status_who(db, nino_dict["nin_id"])
        
        result.append(NinoWithAnthropometry(
            nino=nino_response,
            antropometrias=antropometrias,
            alergias=alergias,
            ultimo_estado_nutricional=estado_nutricional
        ))
    
    return result

def get_child_by_id(db: Session, nin_id: int, usr_id_tutor: int) -> NinoWithAnthropometry:
    """Obtener un niño específico con sus datos antropométricos"""
    repo = NinosRepository(db)
    
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    # Verificar que el niño pertenezca al tutor o sea de su propiedad (self)
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este niño")
    
    nino_response = NinoResponse(**nino_dict)
    
    # Obtener antropometrías
    antropometrias_dict = repo.get_antropometrias_by_nino(nin_id)
    antropometrias = [AnthropometryResponse(**ant) for ant in antropometrias_dict]
    
    # Obtener alergias
    alergias_dict = repo.obtener_alergias(nin_id)
    alergias = [AlergiaResponse(**alergia) for alergia in alergias_dict]
    
    # Calcular estado nutricional actual
    estado_nutricional = None
    if antropometrias:
        # Usar evaluación WHO 
        estado_nutricional = calculate_nutritional_status_who(db, nin_id)
    
    return NinoWithAnthropometry(
        nino=nino_response,
        antropometrias=antropometrias,
        alergias=alergias,
        ultimo_estado_nutricional=estado_nutricional
    )

def add_anthropometry(db: Session, nin_id: int, antropo_data: AnthropometryCreate, usr_id_tutor: int) -> AnthropometryResponse:
    """Agregar nuevos datos antropométricos a un niño"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario (self)
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este niño")
    
    # Agregar los datos antropométricos
    antropo_dict = repo.create_antropometria(nin_id, antropo_data)
    if not antropo_dict:
        raise HTTPException(status_code=400, detail="Error al agregar datos antropométricos")
    
    return AnthropometryResponse(**antropo_dict)

def update_child(db: Session, nin_id: int, nino_data: NinoUpdate, usr_id_tutor: int) -> NinoResponse:
    """Actualizar datos de un niño"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este niño")
    
    # Actualizar los datos
    updated_nino_dict = repo.update_nino(nin_id, nino_data)
    if not updated_nino_dict:
        raise HTTPException(status_code=400, detail="Error al actualizar el niño")
    
    return NinoResponse(**updated_nino_dict)

def delete_child(db: Session, nin_id: int, usr_id_tutor: int) -> Dict[str, str]:
    """Eliminar un niño"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este niño")
    
    # Eliminar el niño
    success = repo.delete_nino(nin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar el niño")
    
    return {"message": f"Niño {nino_dict['nin_nombres']} eliminado exitosamente"}

def evaluate_nutritional_status(db: Session, nin_id: int, usr_id_tutor: int) -> NutritionalStatusResponse:
    """Endpoint POST /ninos/{id}/evaluar - Evaluar estado nutricional con WHO standards"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para evaluar este niño")
    
    # Verificar que tiene antropometrías
    antropometrias = repo.get_antropometrias_by_nino(nin_id, limit=1)
    if not antropometrias:
        raise HTTPException(status_code=400, detail="El niño no tiene datos antropométricos para evaluar")
    
    # Realizar evaluación con estándares WHO
    return calculate_nutritional_status_who(db, nin_id)

# ========== FUNCIONES PARA MANEJO DE ALERGIAS ==========

def agregar_alergia_nino(db: Session, nin_id: int, alergia_data: AlergiaCreate, usr_id_tutor: int) -> List[AlergiaResponse]:
    """Agregar alergia a un niño"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este niño")
    
    # Agregar la alergia
    alergias_dict = repo.agregar_alergia(nin_id, alergia_data.ta_codigo, alergia_data.severidad)
    return [AlergiaResponse(**alergia) for alergia in alergias_dict]

def obtener_alergias_nino(db: Session, nin_id: int, usr_id_tutor: int) -> List[AlergiaResponse]:
    """Obtener alergias de un niño"""
    repo = NinosRepository(db)
    
    # Verificar que el niño existe y pertenece al tutor o es del propietario
    nino_dict = repo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    if nino_dict.get("usr_id_tutor") != usr_id_tutor and nino_dict.get("usr_id_propietario") != usr_id_tutor:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este niño")
    
    # Obtener alergias
    alergias_dict = repo.obtener_alergias(nin_id)
    return [AlergiaResponse(**alergia) for alergia in alergias_dict]

def crear_tipo_alergia(db: Session, tipo_data: TipoAlergiaCreate) -> TipoAlergiaResponse:
    """Crear nuevo tipo de alergia (admin only)"""
    repo = NinosRepository(db)
    
    try:
        tipo_dict = repo.crear_tipo_alergia(tipo_data.ta_codigo, tipo_data.ta_nombre, tipo_data.ta_categoria)
        return TipoAlergiaResponse(**tipo_dict)
    except Exception as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="El código de alergia ya existe")
        raise HTTPException(status_code=500, detail=f"Error al crear tipo de alergia: {str(e)}")

def obtener_tipos_alergias(db: Session) -> List[TipoAlergiaResponse]:
    """Obtener todos los tipos de alergias disponibles"""
    repo = NinosRepository(db)
    
    tipos_dict = repo.obtener_tipos_alergias()
    return [TipoAlergiaResponse(**tipo) for tipo in tipos_dict]
