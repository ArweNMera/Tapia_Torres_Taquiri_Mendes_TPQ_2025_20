import { useState, useCallback, useMemo } from 'react';
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
  const createNinoFn = useMemo(() => apiService.createNino.bind(apiService), []);
  const getNinosFn = useMemo(() => apiService.getNinos.bind(apiService), []);
  const getNinoFn = useMemo(() => apiService.getNino.bind(apiService), []);
  const updateNinoFn = useMemo(() => apiService.updateNino.bind(apiService), []);
  const deleteNinoFn = useMemo(() => apiService.deleteNino.bind(apiService), []);
  const assignTutorFn = useMemo(() => apiService.assignTutorToChild.bind(apiService), []);

  const createNino = useApi<NinoResponse>(createNinoFn);
  const getNinos = useApi<NinoWithAnthropometry[]>(getNinosFn);
  const getNino = useApi<NinoResponse>(getNinoFn);
  const updateNino = useApi<NinoResponse>(updateNinoFn);
  const deleteNino = useApi<{ message: string }>(deleteNinoFn);
  const assignTutor = useApi<NinoResponse>(assignTutorFn);

  return {
    createNino,
    getNinos,
    getNino,
    updateNino,
    deleteNino,
    assignTutor,
  };
}

export function useAnthropometryApi() {
  const addAnthropometryFn = useMemo(() => apiService.addAnthropometry.bind(apiService), []);
  const getAnthropometryHistoryFn = useMemo(() => apiService.getAnthropometryHistory.bind(apiService), []);

  const addAnthropometry = useApi<AnthropometryResponse>(addAnthropometryFn);
  const getAnthropometryHistory = useApi<AnthropometryResponse[]>(getAnthropometryHistoryFn);

  return {
    addAnthropometry,
    getAnthropometryHistory,
  };
}

export function useNutritionalEvaluationApi() {
  const evaluateStatusFn = useMemo(() => apiService.evaluateNutritionalStatus.bind(apiService), []);
  const evaluateNutritionalStatus = useApi<NutritionalStatusResponse>(evaluateStatusFn);

  return {
    evaluateNutritionalStatus,
  };
}

export function useAllergiesApi() {
  const addAllergyFn = useMemo(() => apiService.addAllergy.bind(apiService), []);
  const getAllergiesFn = useMemo(() => apiService.getAllergies.bind(apiService), []);
  const removeAllergyFn = useMemo(() => apiService.removeAllergy.bind(apiService), []);
  const getAllergyTypesFn = useMemo(() => apiService.getAllergyTypes.bind(apiService), []);
  const createAllergyTypeFn = useMemo(() => apiService.createAllergyType.bind(apiService), []);

  const addAllergy = useApi<AlergiaResponse>(addAllergyFn);
  const getAllergies = useApi<AlergiaResponse[]>(getAllergiesFn);
  const removeAllergy = useApi<{ message: string }>(removeAllergyFn);
  const getAllergyTypes = useApi<TipoAlergiaResponse[]>(getAllergyTypesFn);
  const createAllergyType = useApi<TipoAlergiaResponse>(createAllergyTypeFn);

  return {
    addAllergy,
    getAllergies,
    removeAllergy,
    getAllergyTypes,
    createAllergyType,
  };
}

export function useChildProfileApi() {
  const createChildProfileFn = useMemo(() => apiService.createChildProfile.bind(apiService), []);
  const getChildWithDataFn = useMemo(() => apiService.getChildWithData.bind(apiService), []);

  const createChildProfile = useApi<CreateChildProfileResponse>(createChildProfileFn);
  const getChildWithData = useApi<NinoWithAnthropometry>(getChildWithDataFn);

  return {
    createChildProfile,
    getChildWithData,
  };
}

export function useUserApi() {
  const updateProfileFn = useMemo(() => apiService.updateProfile.bind(apiService), []);
  const getProfileFn = useMemo(() => apiService.getProfile.bind(apiService), []);

  const updateProfile = useApi<UserResponse>(updateProfileFn);
  const getProfile = useApi<UserResponse>(getProfileFn);

  return {
    updateProfile,
    getProfile,
  };
}

export function useSelfAnthropometryApi() {
  const getSelfChildFn = useMemo(() => apiService.getSelfChild.bind(apiService), []);
  const addSelfAnthropometryFn = useMemo(() => apiService.addSelfAnthropometry.bind(apiService), []);
  const getSelfHistoryFn = useMemo(() => apiService.getSelfAnthropometryHistory.bind(apiService), []);
  const getSelfStatusFn = useMemo(() => apiService.getSelfNutritionalStatus.bind(apiService), []);

  const getSelfChild = useApi<NinoResponse>(getSelfChildFn);
  const addSelfAnthropometry = useApi<AnthropometryResponse>(addSelfAnthropometryFn);
  const getSelfAnthropometryHistory = useApi<AnthropometryResponse[]>(getSelfHistoryFn);
  const getSelfNutritionalStatus = useApi<NutritionalStatusResponse>(getSelfStatusFn);

  return {
    getSelfChild,
    addSelfAnthropometry,
    getSelfAnthropometryHistory,
    getSelfNutritionalStatus,
  };
}

export function useEntitiesApi() {
  const searchEntitiesFn = useMemo(() => apiService.searchEntities.bind(apiService), []);
  const getEntityTypesFn = useMemo(() => apiService.getEntityTypes.bind(apiService), []);

  const searchEntities = useApi<any[]>(searchEntitiesFn);
  const getEntityTypes = useApi<any[]>(getEntityTypesFn);
  return { searchEntities, getEntityTypes };
}
