import React from 'react';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { AlimentoConNutrientesResponse } from '../../types/api';

interface AlimentoDetailProps {
  alimento: AlimentoConNutrientesResponse;
}

const AlimentoDetail: React.FC<AlimentoDetailProps> = ({ alimento }) => {
  return (
    <div className="space-y-6">
      {/* Información básica */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            {alimento.ali_nombre}
            <Badge variant={alimento.ali_activo ? "default" : "secondary"}>
              {alimento.ali_activo ? "Activo" : "Inactivo"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alimento.ali_nombre_cientifico && (
              <div>
                <h4 className="font-medium text-sm text-gray-600">Nombre científico</h4>
                <p className="text-sm italic">{alimento.ali_nombre_cientifico}</p>
              </div>
            )}

            {alimento.ali_grupo && (
              <div>
                <h4 className="font-medium text-sm text-gray-600">Grupo alimentario</h4>
                <p className="text-sm">{alimento.ali_grupo}</p>
              </div>
            )}

            <div>
              <h4 className="font-medium text-sm text-gray-600">Unidad de medida</h4>
              <p className="text-sm">{alimento.ali_unidad}</p>
            </div>

            <div>
              <h4 className="font-medium text-sm text-gray-600">ID</h4>
              <p className="text-sm font-mono">{alimento.ali_id}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Información nutricional */}
      {alimento.nutrientes && alimento.nutrientes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Información Nutricional</CardTitle>
            <p className="text-sm text-gray-600">
              Valores por 100{alimento.ali_unidad === 'ml' ? 'ml' : 'g'} de alimento
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {alimento.nutrientes.map((nutriente) => (
                <div
                  key={nutriente.nutri_id}
                  className="p-3 border rounded-lg bg-gray-50"
                >
                  <h4 className="font-medium text-sm">{nutriente.nutri_nombre}</h4>
                  <p className="text-lg font-semibold text-blue-600">
                    {nutriente.an_cantidad_100} {nutriente.nutri_unidad}
                  </p>
                  {nutriente.an_fuente && (
                    <p className="text-xs text-gray-500 mt-1">
                      Fuente: {nutriente.an_fuente}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mensaje si no hay nutrientes */}
      {(!alimento.nutrientes || alimento.nutrientes.length === 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Información Nutricional</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-center py-8">
              No hay información nutricional disponible para este alimento.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AlimentoDetail;
