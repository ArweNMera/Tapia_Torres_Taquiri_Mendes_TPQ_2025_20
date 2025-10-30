import React from 'react';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { RecetaCompletaResponse } from '../../types/api';

interface RecetaDetailProps {
  receta: RecetaCompletaResponse;
}

const RecetaDetail: React.FC<RecetaDetailProps> = ({ receta }) => {
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
      {receta.informacion_nutricional && Object.keys(receta.informacion_nutricional).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Información Nutricional</CardTitle>
            <p className="text-sm text-gray-600">
              Valores aproximados por porción
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(receta.informacion_nutricional).map(([nutriente, valor]) => (
                <div
                  key={nutriente}
                  className="p-3 border rounded-lg bg-gray-50"
                >
                  <h4 className="font-medium text-sm capitalize">
                    {nutriente.replace('_', ' ')}
                  </h4>
                  <p className="text-lg font-semibold text-green-600">
                    {typeof valor === 'number' ? valor.toFixed(2) : valor}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mensajes si no hay datos */}
      {(!receta.ingredientes || receta.ingredientes.length === 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Ingredientes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-center py-8">
              No hay ingredientes registrados para esta receta.
            </p>
          </CardContent>
        </Card>
      )}

      {(!receta.informacion_nutricional || Object.keys(receta.informacion_nutricional).length === 0) && (
        <Card>
          <CardHeader>
            <CardTitle>Información Nutricional</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500 text-center py-8">
              No hay información nutricional disponible para esta receta.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RecetaDetail;
