/**
 * Wizard de 4 pasos para configurar preferencias alimentarias
 */
import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { X, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Preferencias, TipoComida } from '../../types/mealPlan';

interface PreferenciasWizardProps {
    preferenciasIniciales: Preferencias;
    onSave: (preferencias: Preferencias) => void;
    onCancel: () => void;
}

const PASOS: { tipo: TipoComida; titulo: string; opciones: string[] }[] = [
    {
        tipo: 'DESAYUNO',
        titulo: 'Desayuno',
        opciones: ['Avena', 'Huevos', 'Frutas', 'Pan tostado', 'Cereal', 'Yogurt'],
    },
    {
        tipo: 'ALMUERZO',
        titulo: 'Almuerzo',
        opciones: ['Arroz', 'Pollo', 'Pasta', 'Verduras', 'Legumbres', 'Pescado'],
    },
    {
        tipo: 'CENA',
        titulo: 'Cena',
        opciones: ['Sopa', 'Ensalada', 'Carne', 'Verduras cocidas', 'Quinoa', 'Tofu'],
    },
    {
        tipo: 'SNACKS',
        titulo: 'Snacks',
        opciones: ['Frutas', 'Frutos secos', 'Galletas', 'Yogurt', 'Verduras crudas'],
    },
];

export const PreferenciasWizard: React.FC<PreferenciasWizardProps> = ({
    preferenciasIniciales,
    onSave,
    onCancel,
}) => {
    const [paso, setPaso] = useState(0);
    const [preferencias, setPreferencias] = useState<Preferencias>(preferenciasIniciales);
    const [nuevaPreferencia, setNuevaPreferencia] = useState('');

    // Actualizar preferencias cuando cambien las iniciales
    useEffect(() => {
        console.log('🔄 Actualizando preferencias en wizard:', preferenciasIniciales);
        setPreferencias(preferenciasIniciales);
    }, [preferenciasIniciales]);

    const pasoActual = PASOS[paso];
    const tipoActual = pasoActual.tipo.toLowerCase() as keyof Preferencias;
    const preferenciasActuales = preferencias[tipoActual];

    // Debug
    console.log('🔍 Wizard Debug:', {
        paso,
        pasoActual: pasoActual.tipo,
        tipoActual,
        preferencias,
        preferenciasActuales,
    });

    const agregarPreferencia = (pref: string) => {
        if (!preferenciasActuales.includes(pref)) {
            setPreferencias({
                ...preferencias,
                [tipoActual]: [...preferenciasActuales, pref],
            });
        }
    };

    const eliminarPreferencia = (pref: string) => {
        setPreferencias({
            ...preferencias,
            [tipoActual]: preferenciasActuales.filter((p) => p !== pref),
        });
    };

    const agregarPersonalizada = () => {
        if (nuevaPreferencia.trim() && !preferenciasActuales.includes(nuevaPreferencia.trim())) {
            agregarPreferencia(nuevaPreferencia.trim());
            setNuevaPreferencia('');
        }
    };

    const siguiente = () => {
        if (paso < PASOS.length - 1) {
            setPaso(paso + 1);
        } else {
            onSave(preferencias);
        }
    };

    const anterior = () => {
        if (paso > 0) {
            setPaso(paso - 1);
        }
    };

    const progreso = ((paso + 1) / PASOS.length) * 100;

    return (
        <div className="space-y-6">
            {/* Header con progreso */}
            <div>
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">
                        Paso {paso + 1} de {PASOS.length}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{progreso.toFixed(0)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                        className="bg-green-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progreso}%` }}
                    />
                </div>
            </div>

            {/* Título */}
            <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    ¿Qué sueles comer actualmente?
                </h3>
                <p className="text-gray-600">
                    Cuéntanos tus comidas habituales para generar recomendaciones personalizadas
                </p>
            </div>

            {/* Tabs de tipos de comida */}
            <div className="flex gap-2 justify-center">
                {PASOS.map((p, idx) => (
                    <button
                        key={p.tipo}
                        onClick={() => setPaso(idx)}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${idx === paso
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                            }`}
                    >
                        {p.titulo}
                    </button>
                ))}
            </div>

            {/* Preferencias actuales */}
            <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">{pasoActual.titulo} actual:</h4>
                <div className="flex flex-wrap gap-2">
                    {preferenciasActuales.length > 0 ? (
                        preferenciasActuales.map((pref) => (
                            <Badge
                                key={pref}
                                className="bg-green-600 text-white hover:bg-green-700 cursor-pointer"
                                onClick={() => eliminarPreferencia(pref)}
                            >
                                {pref}
                                <X className="w-3 h-3 ml-1" />
                            </Badge>
                        ))
                    ) : (
                        <p className="text-sm text-gray-500">No has seleccionado preferencias aún</p>
                    )}
                </div>
            </div>

            {/* Opciones comunes */}
            <div>
                <h4 className="font-medium text-gray-900 mb-3">Opciones comunes:</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {pasoActual.opciones.map((opcion) => {
                        const seleccionada = preferenciasActuales.includes(opcion);
                        return (
                            <button
                                key={opcion}
                                onClick={() =>
                                    seleccionada ? eliminarPreferencia(opcion) : agregarPreferencia(opcion)
                                }
                                className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors ${seleccionada
                                    ? 'border-green-600 bg-green-50 text-green-700'
                                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                                    }`}
                            >
                                <Plus className="w-4 h-4" />
                                {opcion}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Agregar personalizada */}
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    ¿Otra comida que no aparece?
                </label>
                <div className="flex gap-2">
                    <Input
                        value={nuevaPreferencia}
                        onChange={(e) => setNuevaPreferencia(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && agregarPersonalizada()}
                        placeholder="Escribe aquí..."
                        className="flex-1"
                    />
                    <Button onClick={agregarPersonalizada} variant="outline">
                        <Plus className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            {/* Botones de navegación */}
            <div className="flex items-center justify-between pt-4 border-t">
                <Button variant="ghost" onClick={onCancel}>
                    Omitir configuración
                </Button>
                <div className="flex gap-2">
                    {paso > 0 && (
                        <Button variant="outline" onClick={anterior}>
                            <ChevronLeft className="w-4 h-4 mr-1" />
                            Anterior
                        </Button>
                    )}
                    <Button onClick={siguiente} className="bg-green-600 hover:bg-green-700">
                        {paso < PASOS.length - 1 ? (
                            <>
                                Siguiente
                                <ChevronRight className="w-4 h-4 ml-1" />
                            </>
                        ) : (
                            'Guardar'
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
};
