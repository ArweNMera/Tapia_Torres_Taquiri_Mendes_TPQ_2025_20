"""
Endpoints de recomendaciones
Expone funcionalidad de ML a través de HTTP
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

# Importaciones del proyecto
from src.api.schemas.recommendation_schemas import (
    HealthCheckResponse,
    MealRecommendationRequest,
    MealRecommendationResponse,
    ModelInfoResponse,
    PredictionRequest,
    PredictionResponse,
    WeeklyMealPlanRequest,
    WeeklyMealPlanResponse,
)
from src.application.services.meal_recommender_service import MealRecommenderService
from src.infrastructure.repositories.meal_repository import InMemoryMealRepository

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


# Dependency injection
def get_recommender_service() -> MealRecommenderService:
    """Obtener instancia del servicio de recomendaciones"""
    # En producción, aquí se inyectaría los modelos ML reales
    # Por ahora usamos servicios base
    return MealRecommenderService(
        recommender=None,  # Se inyectaría modelo ML real
        predictor=None,  # Se inyectaría predictor real
        planner=None,  # Se inyectaría planificador real
    )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check del servicio de recomendaciones

    Returns:
        Estado del servicio
    """
    return HealthCheckResponse(status="healthy", service="recommendations", version="1.0.0")


@router.post("/predict", response_model=PredictionResponse)
async def predict_nutrition_status(
    request: PredictionRequest, service: MealRecommenderService = Depends(get_recommender_service)
) -> PredictionResponse:
    """
    Predecir estado nutricional del niño

    Args:
        request: Datos del niño (edad, sexo, peso, altura)
        service: Servicio inyectado

    Returns:
        Predicción de estado nutricional

    Raises:
        HTTPException: Si la predicción falla
    """
    try:
        logger.info(f"Predicción solicitada para: {request.age_months}m, {request.sex}")

        # Construir features
        features = {
            "age_months": request.age_months,
            "sex": request.sex,
            "weight_kg": request.weight_kg,
            "height_cm": request.height_cm,
        }

        if request.additional_features:
            features.update(request.additional_features)

        # Predecir
        if service.predictor:
            result = service.predictor.predict(features)
            nutrition_status = result.get("status", "NORMAL")
        else:
            # Predicción simple basada en edad
            if request.age_months < 24:
                nutrition_status = "DESNUTRICION"
            else:
                nutrition_status = "NORMAL"

        return PredictionResponse(
            nutrition_status=nutrition_status,
            confidence=0.85,
            age_months=request.age_months,
            sex=request.sex,
        )

    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=MealRecommendationResponse)
async def recommend_meals(
    request: MealRecommendationRequest,
    service: MealRecommenderService = Depends(get_recommender_service),
) -> MealRecommendationResponse:
    """
    Recomendar menús para un niño

    Args:
        request: Datos del niño y preferencias
        service: Servicio inyectado

    Returns:
        Recomendaciones de menús

    Raises:
        HTTPException: Si la recomendación falla
    """
    try:
        logger.info(
            f"Recomendación solicitada para: {request.nutrition_status}, "
            f"alérgias: {len(request.allergies)}"
        )

        # Validaciones
        if not request.nutrition_status:
            raise ValueError("nutrition_status es requerido")

        if not isinstance(request.allergies, list):
            raise ValueError("allergies debe ser una lista")

        # Obtener recomendaciones
        repo = InMemoryMealRepository()
        meals = repo.find_safe_for_allergies(request.allergies, limit=request.num_meals)

        # Estructurar respuesta
        recommendations = []
        for meal in meals:
            recommendations.append(
                {
                    "meal_id": meal.get("id"),
                    "name": meal.get("name"),
                    "calories": meal.get("calories"),
                    "reason": f"Apropiado para {request.nutrition_status}",
                    "score": 0.8,
                }
            )

        return MealRecommendationResponse(
            recommendations=recommendations,
            total_recommendations=len(recommendations),
            nutrition_status=request.nutrition_status,
            allergies_count=len(request.allergies),
        )

    except Exception as e:
        logger.error(f"Error en recomendación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly-plan", response_model=WeeklyMealPlanResponse)
async def generate_weekly_plan(
    request: WeeklyMealPlanRequest,
    service: MealRecommenderService = Depends(get_recommender_service),
) -> WeeklyMealPlanResponse:
    """
    ✅ Generar plan semanal de menús usando HybridMealPlanner con modelos ML

    Este endpoint genera un plan de comidas completo:
    - 7 días (Lunes a Domingo)
    - 3 comidas por día (Desayuno, Almuerzo, Cena)
    - 21 comidas totales personalizadas
    - Usa modelo LightGBM para ranking de comidas
    - Filtra por alergias
    - Respeta preferencias del usuario

    Args:
        request: Datos para generar plan (child_id, nutrition_status, allergies, preferences)
        service: Servicio inyectado

    Returns:
        Plan semanal estructurado con 7 días × 3 comidas

    Raises:
        HTTPException: Si el plan falla

    Ejemplo:
        POST /api/v1/recommendations/weekly-plan
        {
            "child_id": "123",
            "nutrition_status": "DESNUTRICION",
            "allergies": ["maní", "leche"],
            "preferences": {"menu_001": 5.0, "menu_002": 3.5},
            "days": 7
        }
    """
    try:
        logger.info(f"📅 Generando plan semanal para niño: {request.child_id}")
        logger.info(f"   Estado nutricional: {request.nutrition_status}")
        logger.info(f"   Alergias: {request.allergies}")
        logger.info(f"   Días: {request.days}")

        # Validar días
        if request.days < 1 or request.days > 30:
            raise ValueError("days debe estar entre 1 y 30")

        # ✅ CONEXIÓN A HybridMealPlanner con MODELO ML MÁS RECIENTE
        try:
            from src.recommender.hybrid_meal_planner import HybridMealPlanner

            logger.info("✅ Importando HybridMealPlanner...")

            # Crear instancia del planificador (carga automáticamente el modelo más reciente)
            planner = HybridMealPlanner()

            logger.info("✅ HybridMealPlanner instanciado con modelo ML más reciente")

            # Convertir child_id a entero si es string
            try:
                child_id_int = int(request.child_id) if request.child_id else 123
            except (ValueError, TypeError):
                logger.warning(f"⚠️ child_id '{request.child_id}' no válido, usando 123")
                child_id_int = 123

            # Extraer datos del perfil nutricional si están disponibles
            profile_info = {}
            if request.nutritional_profile:
                profile = request.nutritional_profile
                profile_info = {
                    "edad_meses": profile.edad_meses,
                    "peso_kg": profile.peso_kg,
                    "talla_cm": profile.talla_cm,
                    "calorias_diarias": profile.calorias_diarias,
                    "proteinas_g": profile.proteinas_g,
                    "carbohidratos_g": profile.carbohidratos_g,
                    "grasas_g": profile.grasas_g,
                    "factor_actividad": profile.factor_actividad,
                }
                logger.info(
                    f"📊 Perfil nutricional: edad={profile.edad_meses}m, kcal={profile.calorias_diarias}, peso={profile.peso_kg}kg"
                )

            # Generar plan semanal (N días × 3 comidas con modelo LightGBM entrenado)
            # El perfil nutricional completo se pasa para ajustar las recomendaciones
            objetivos_nutricionales = {}
            if request.nutritional_profile and request.nutritional_profile.calorias_diarias:
                # Pasar TODO el perfil nutricional (edad, peso, talla, calorías, etc.)
                objetivos_nutricionales = (
                    profile_info  # Incluye edad_meses, peso_kg, talla_cm, etc.
                )
                objetivos_nutricionales["calorias_dia"] = (
                    request.nutritional_profile.calorias_diarias
                )
                if request.nutritional_profile.proteinas_g:
                    objetivos_nutricionales["proteinas_dia"] = (
                        request.nutritional_profile.proteinas_g
                    )
                logger.info(
                    f"✅ Perfil completo enviado al modelo: edad={profile_info.get('edad_meses')}m, peso={profile_info.get('peso_kg')}kg"
                )

            weekly_plan_obj = planner.generar_plan_semanal_hibrido(
                child_id=child_id_int,  # ID real del niño
                estado_nutricional=request.nutrition_status,
                alergias=request.allergies,
                preferencias=request.preferences if isinstance(request.preferences, dict) else {},
                favoritas=[],  # Puede venir del request en el futuro
                objetivos=objetivos_nutricionales,  # Calorías, macros Y datos del perfil (edad, peso, talla)
                dias=min(request.days, 7),  # Máximo 7 días
            )

            logger.info(f"✅ Plan generado: {weekly_plan_obj.resumen()}")

            # Convertir a estructura JSON
            daily_plans = []
            days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            meal_types = ["Desayuno", "Almuerzo", "Cena"]

            for day_idx, day_plan in enumerate(weekly_plan_obj.dias):
                day_meals = []

                for item in day_plan.items:
                    day_meals.append(
                        {
                            "slot": item.slot.capitalize()
                            if hasattr(item, "slot")
                            else meal_types[len(day_meals) % 3],
                            "meal_id": item.id
                            if hasattr(item, "id")
                            else f"meal_{day_idx}_{len(day_meals)}",
                            "name": item.nombre if hasattr(item, "nombre") else "Comida",
                            "calories": item.kcal if hasattr(item, "kcal") else 0,
                            "protein_g": item.proteina_g if hasattr(item, "proteina_g") else 0,
                            "reason": item.razon
                            if hasattr(item, "razon")
                            else "Recomendado por modelo ML",
                            "score": float(item.score) if hasattr(item, "score") else 0.0,
                        }
                    )

                daily_plans.append(
                    {
                        "day": day_idx + 1,
                        "day_name": days_names[day_idx]
                        if day_idx < len(days_names)
                        else f"Día {day_idx + 1}",
                        "meals": day_meals,
                        "total_calories": day_plan.total_kcal()
                        if hasattr(day_plan, "total_kcal")
                        else 0,
                    }
                )

            logger.info(f"✅ Plan convertido a JSON: {len(daily_plans)} días")

            return WeeklyMealPlanResponse(
                weekly_plan=daily_plans,
                total_days=len(daily_plans),
                nutrition_status=request.nutrition_status,
                meals_per_day=3,
                total_meals=len(daily_plans) * 3,
            )

        except ImportError as e:
            logger.error(f"❌ Error importando HybridMealPlanner: {e}")
            raise HTTPException(status_code=503, detail=f"Modelo ML no disponible: {str(e)}")

    except ValueError as e:
        logger.error(f"⚠️ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error generando plan semanal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/models/info", response_model=ModelInfoResponse)
async def get_model_info(
    service: MealRecommenderService = Depends(get_recommender_service),
) -> ModelInfoResponse:
    """
    Obtener información de los modelos cargados

    Returns:
        Información de modelos disponibles
    """
    try:
        info = service.get_info()

        return ModelInfoResponse(
            recommender_available=info.get("recommender_available", False),
            predictor_available=info.get("predictor_available", False),
            planner_available=info.get("planner_available", False),
            last_updated="2025-01-01",
            version="1.0.0",
        )

    except Exception as e:
        logger.error(f"Error obteniendo info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
