import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import type { 
  ApiResponse,
  NinoResponse,
  NinoCreate,
  NinoUpdate,
  AnthropometryResponse,
  AnthropometryCreate,
  NutritionalStatusResponse,
  AlergiaResponse,
  AlergiaCreate,
  TipoAlergiaResponse,
  TipoAlergiaCreate,
  NinoWithAnthropometry,
  CreateChildProfileResponse,
  CreateChildProfileRequest,
  UserResponse,
  UserProfile
} from '../types/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      try {
        const response = await apiFunction(...args);
        
        if (response.success && response.data) {
          setState({
            data: response.data,
            loading: false,
            error: null,
          });
          return response.data;
        } else {
          const errorMessage = response.error || response.message || 'Error desconocido';
          setState({
            data: null,
            loading: false,
            error: errorMessage,
          });
          return null;
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Error de conexión';
        setState({
          data: null,
          loading: false,
          error: errorMessage,
        });
        return null;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hooks específicos para casos comunes
export function useNinosApi() {
  const createNino = useApi<NinoResponse>(apiService.createNino.bind(apiService));
  const getNinos = useApi<NinoResponse[]>(apiService.getNinos.bind(apiService));
  const getNino = useApi<NinoResponse>(apiService.getNino.bind(apiService));
  const updateNino = useApi<NinoResponse>(apiService.updateNino.bind(apiService));
  const deleteNino = useApi<{ message: string }>(apiService.deleteNino.bind(apiService));

  return {
    createNino,
    getNinos,
    getNino,
    updateNino,
    deleteNino,
  };
}

export function useAnthropometryApi() {
  const addAnthropometry = useApi<AnthropometryResponse>(apiService.addAnthropometry.bind(apiService));
  const getAnthropometryHistory = useApi<AnthropometryResponse[]>(apiService.getAnthropometryHistory.bind(apiService));

  return {
    addAnthropometry,
    getAnthropometryHistory,
  };
}

export function useNutritionalEvaluationApi() {
  const evaluateNutritionalStatus = useApi<NutritionalStatusResponse>(apiService.evaluateNutritionalStatus.bind(apiService));

  return {
    evaluateNutritionalStatus,
  };
}

export function useAllergiesApi() {
  const addAllergy = useApi<AlergiaResponse>(apiService.addAllergy.bind(apiService));
  const getAllergies = useApi<AlergiaResponse[]>(apiService.getAllergies.bind(apiService));
  const removeAllergy = useApi<{ message: string }>(apiService.removeAllergy.bind(apiService));
  const getAllergyTypes = useApi<TipoAlergiaResponse[]>(apiService.getAllergyTypes.bind(apiService));
  const createAllergyType = useApi<TipoAlergiaResponse>(apiService.createAllergyType.bind(apiService));

  return {
    addAllergy,
    getAllergies,
    removeAllergy,
    getAllergyTypes,
    createAllergyType,
  };
}

export function useChildProfileApi() {
  const createChildProfile = useApi<CreateChildProfileResponse>(apiService.createChildProfile.bind(apiService));
  const getChildWithData = useApi<NinoWithAnthropometry>(apiService.getChildWithData.bind(apiService));

  return {
    createChildProfile,
    getChildWithData,
  };
}

export function useUserApi() {
  const updateProfile = useApi<UserResponse>(apiService.updateProfile.bind(apiService));
  const getProfile = useApi<UserResponse>(apiService.getProfile.bind(apiService));

  return {
    updateProfile,
    getProfile,
  };
}

export function useSelfAnthropometryApi() {
  const getSelfChild = useApi<NinoResponse>(apiService.getSelfChild.bind(apiService));
  const addSelfAnthropometry = useApi<AnthropometryResponse>(apiService.addSelfAnthropometry.bind(apiService));
  const getSelfAnthropometryHistory = useApi<AnthropometryResponse[]>(apiService.getSelfAnthropometryHistory.bind(apiService));
  const getSelfNutritionalStatus = useApi<NutritionalStatusResponse>(apiService.getSelfNutritionalStatus.bind(apiService));

  return {
    getSelfChild,
    addSelfAnthropometry,
    getSelfAnthropometryHistory,
    getSelfNutritionalStatus,
  };
}

export function useEntitiesApi() {
  const searchEntities = useApi<any[]>(apiService.searchEntities.bind(apiService));
  const getEntityTypes = useApi<any[]>(apiService.getEntityTypes.bind(apiService));
  return { searchEntities, getEntityTypes };
}
