import React, { useState } from 'react';
import { Apple, ChefHat } from 'lucide-react';
import AlimentosPage from './AlimentosPage';
import RecetasPage from './RecetasPage';

const ComidasPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'alimentos' | 'recetas'>('alimentos');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con Tabs */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Comidas</h1>

            {/* Tabs Navigation */}
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
              <button
                onClick={() => setActiveTab('alimentos')}
                className={`
                  flex items-center gap-2 px-6 py-2.5 rounded-md font-medium transition-all duration-200
                  ${activeTab === 'alimentos'
                    ? 'bg-white text-green-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <Apple className="w-5 h-5" />
                Alimentos
              </button>

              <button
                onClick={() => setActiveTab('recetas')}
                className={`
                  flex items-center gap-2 px-6 py-2.5 rounded-md font-medium transition-all duration-200
                  ${activeTab === 'recetas'
                    ? 'bg-white text-green-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                <ChefHat className="w-5 h-5" />
                Recetas
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'alimentos' && <AlimentosPage embedded />}
        {activeTab === 'recetas' && <RecetasPage embedded />}
      </div>
    </div>
  );
};

export default ComidasPage;
