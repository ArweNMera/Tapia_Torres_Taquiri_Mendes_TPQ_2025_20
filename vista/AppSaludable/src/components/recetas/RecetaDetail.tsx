import React, { useMemo } from 'react';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { RecetaCompletaResponse } from '../../types/api';

interface RecetaDetailProps {
  receta: RecetaCompletaResponse;
}

const RecetaDetail: React.FC<RecetaDetailProps> = ({ receta }) => {
  // Calcular información nutricional aproximada basada en ingredientes
  const nutricionCalculada = useMemo(() => {
    if (!receta.ingredientes || receta.ingredientes.length === 0) {
      return null;
    }

    // Estimación simple basada en promedios
    // En un sistema real, esto vendría de la base de datos con valores exactos por alimento
    let totalKcal = 0;
    let totalProteinas = 0;
    let totalCarbohidratos = 0;
    let totalGrasas = 0;

    receta.ingredientes.forEach(ing => {
      const cantidadEnGramos = ing.ri_cantidad;

      // Valores promedio por 100g (estos son estimaciones)
      // En producción deberían venir de la tabla alimentos_nutrientes
      const kcalPor100g = 150; // Promedio
      const proteinaPor100g = 10; // Promedio
      const carboPor100g = 20; // Promedio
      const grasaPor100g = 5; // Promedio

      totalKcal += (cantidadEnGramos / 100) * kcalPor100g;
      totalProteinas += (cantidadEnGramos / 100) * proteinaPor100g;
      totalCarbohidratos += (cantidadEnGramos / 100) * carboPor100g;
      totalGrasas += (cantidadEnGramos / 100) * grasaPor100g;
    });

    return {
      'Calorías': `${Math.round(totalKcal)} kcal`,
      'Proteínas': `${totalProteinas.toFixed(1)} g`,
      'Carbohidratos': `${totalCarbohidratos.toFixed(1)} g`,
      'Grasas': `${totalGrasas.toFixed(1)} g`,
    };
  }, [receta.ingredientes]);

  // Usar información nutricional del backend si existe y no está vacía, sino usar calculada
  const informacionNutricional =
    receta.informacion_nutricional && Object.keys(receta.informacion_nutricional).length > 0
      ? receta.informacion_nutricional
      : nutricionCalculada;

  return (
    <div className="space-y-6">
      {/* Información básica */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            {receta.rec_nombre}
            <Badge variant={receta.rec_activo ? "default" : "secondary"}>
              {receta.rec_activo ? "Activa" : "Inactiva"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-sm text-gray-600">ID de la receta</h4>
              <p className="text-sm font-mono">{receta.rec_id}</p>
            </div>

            {receta.tipos_comida && receta.tipos_comida.length > 0 && (
              <div>
                <h4 className="font-medium text-sm text-gray-600">Tipos de comida</h4>
                <div className="flex flex-wrap gap-1 mt-1">
                  {receta.tipos_comida.map((tipo, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tipo}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {receta.rec_instrucciones && (
            <div>
              <h4 className="font-medium text-sm text-gray-600 mb-2">Instrucciones</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{receta.rec_instrucciones}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Ingredientes */}
      {receta.ingredientes && receta.ingredientes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Ingredientes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {receta.ingredientes.map((ingrediente, index) => (
                <div
                  key={`${ingrediente.ali_id}-${index}`}
                  className="flex items-center justify-between p-3 border rounded-lg bg-gray-50"
                >
                  <div>
                    <h4 className="font-medium text-sm">
                      {ingrediente.ali_nombre || `Alimento ID: ${ingrediente.ali_id}`}
                    </h4>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-blue-600">
                      {ingrediente.ri_cantidad} {ingrediente.ri_unidad}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Información nutricional */}
      {informacionNutricional && Object.keys(informacionNutricional).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Información Nutricional</CardTitle>
            <p className="text-sm text-gray-600">
              Valores aproximados por receta completa {!receta.informacion_nutricional && '(estimación)'}
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(informacionNutricional).map(([nutriente, valor]) => (
                <div
                  key={nutriente}
                  className="p-4 border rounded-lg bg-gradient-to-br from-green-50 to-white text-center"
                >
                  <h4 className="font-medium text-xs text-gray-600 uppercase mb-1">
                    {nutriente}
                  </h4>
                  <p className="text-xl font-bold text-green-600">
                    {valor}
                  </p>
                </div>
              ))}
            </div>
            {!receta.informacion_nutricional && (
              <p className="text-xs text-gray-500 mt-4 text-center">
                * Valores calculados automáticamente basados en promedios. Para información precisa, consulte con un nutricionista.
              </p>
            )}
          </CardContent>
        </Card>
      )}

    </div>
  );
};


export default RecetaDetail;
