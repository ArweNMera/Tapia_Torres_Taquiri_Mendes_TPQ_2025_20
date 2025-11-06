// Configuración de URLs para producción
// Este archivo fuerza las URLs de US-EAST1

export const config = {
  API_BASE_URL: 'https://backend.tecno-express.shop',
  ML_API_BASE_URL: 'https://modelo.tecno-express.shop',
  API_VERSION: 'v1',
  TOKEN_KEY: 'auth_token',

  // Información de la app
  APP_NAME: 'App Saludable',
  APP_VERSION: '1.0.0',
};

// Función para obtener la configuración según el entorno
export const getConfig = () => {
  // En desarrollo, usar variables de entorno si están disponibles
  if (import.meta.env.DEV) {
    return {
      API_BASE_URL: import.meta.env.VITE_API_BASE_URL || config.API_BASE_URL,
      ML_API_BASE_URL: import.meta.env.VITE_ML_API_BASE_URL || config.ML_API_BASE_URL,
      API_VERSION: import.meta.env.VITE_API_VERSION || config.API_VERSION,
      TOKEN_KEY: import.meta.env.VITE_TOKEN_KEY || config.TOKEN_KEY,
      APP_NAME: import.meta.env.VITE_APP_NAME || config.APP_NAME,
      APP_VERSION: import.meta.env.VITE_APP_VERSION || config.APP_VERSION,
    };
  }

  // En producción, usar las URLs hardcodeadas (US-EAST1)
  return config;
};
