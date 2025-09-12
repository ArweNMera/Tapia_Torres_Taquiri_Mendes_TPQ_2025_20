import { useState, useRef } from 'react';
import { Camera, Upload, Scan, FileText, Package, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { motion, AnimatePresence } from 'motion/react';

interface ScanResult {
  id: string;
  name: string;
  brand?: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fiber: number;
  sodium: number;
  sugar: number;
  healthScore: number;
  allergens: string[];
  recommendations: string[];
  image: string;
}

interface ScannedItem {
  id: string;
  name: string;
  quantity: string;
  price: number;
  category: string;
}

type ScanMode = 'product' | 'receipt';

export function ScanScreen() {
  const [scanMode, setScanMode] = useState<ScanMode>('product');
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [receiptItems, setReceiptItems] = useState<ScannedItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsScanning(true);
    setScanProgress(0);

    // Simular proceso de escaneo
    const progressInterval = setInterval(() => {
      setScanProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          setIsScanning(false);
          simulateScanResult();
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const simulateScanResult = () => {
    if (scanMode === 'product') {
      setScanResult({
        id: '1',
        name: 'Yogurt Natural sin Azúcar',
        brand: 'Alpura',
        calories: 120,
        protein: 10,
        carbs: 8,
        fats: 6,
        fiber: 0,
        sodium: 85,
        sugar: 6,
        healthScore: 85,
        allergens: ['Lácteos'],
        recommendations: [
          'Excelente fuente de proteína para el crecimiento',
          'Bajo en azúcar añadida, ideal para niños',
          'Rico en calcio para huesos fuertes'
        ],
        image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400'
      });
    } else {
      setReceiptItems([
        { id: '1', name: 'Manzanas Rojas', quantity: '1 kg', price: 45.50, category: 'Frutas' },
        { id: '2', name: 'Pollo Orgánico', quantity: '1.2 kg', price: 185.00, category: 'Proteínas' },
        { id: '3', name: 'Avena Integral', quantity: '500g', price: 35.00, category: 'Cereales' },
        { id: '4', name: 'Yogurt Natural', quantity: '1L', price: 55.00, category: 'Lácteos' },
        { id: '5', name: 'Espinacas Frescas', quantity: '250g', price: 28.00, category: 'Verduras' }
      ]);
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-success';
    if (score >= 60) return 'text-warning';
    return 'text-destructive';
  };

  const getHealthScoreBg = (score: number) => {
    if (score >= 80) return 'bg-success';
    if (score >= 60) return 'bg-warning';
    return 'bg-destructive';
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Frutas': 'bg-accent text-accent-foreground',
      'Proteínas': 'bg-chart-1 text-white',
      'Cereales': 'bg-chart-2 text-white',
      'Lácteos': 'bg-info text-white',
      'Verduras': 'bg-success text-white'
    };
    return colors[category] || 'bg-muted text-muted-foreground';
  };

  const renderProductResult = () => {
    if (!scanResult) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Información del producto */}
        <Card className="p-6">
          <div className="flex items-start space-x-4">
            <div className="w-20 h-20 rounded-lg overflow-hidden bg-muted flex-shrink-0">
              <img 
                src={scanResult.image} 
                alt={scanResult.name}
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-lg">{scanResult.name}</h3>
                <div className={`text-2xl font-bold ${getHealthScoreColor(scanResult.healthScore)}`}>
                  {scanResult.healthScore}/100
                </div>
              </div>
              
              {scanResult.brand && (
                <p className="text-muted-foreground mb-3">{scanResult.brand}</p>
              )}
              
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${getHealthScoreBg(scanResult.healthScore)} text-white`}>
                {scanResult.healthScore >= 80 ? <CheckCircle size={16} className="mr-1" /> : 
                 scanResult.healthScore >= 60 ? <Info size={16} className="mr-1" /> : 
                 <AlertCircle size={16} className="mr-1" />}
                {scanResult.healthScore >= 80 ? 'Muy Saludable' : 
                 scanResult.healthScore >= 60 ? 'Moderadamente Saludable' : 
                 'Poco Saludable'}
              </div>
            </div>
          </div>
        </Card>

        {/* Información nutricional */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4">Información Nutricional (100g)</h4>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">Calorías</p>
              <p className="text-xl font-bold">{scanResult.calories}</p>
            </div>
            <div className="text-center p-3 bg-chart-1/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Proteína</p>
              <p className="text-xl font-bold text-chart-1">{scanResult.protein}g</p>
            </div>
            <div className="text-center p-3 bg-chart-2/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Carbohidratos</p>
              <p className="text-xl font-bold text-chart-2">{scanResult.carbs}g</p>
            </div>
            <div className="text-center p-3 bg-chart-3/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Grasas</p>
              <p className="text-xl font-bold text-chart-3">{scanResult.fats}g</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-muted-foreground">Fibra</p>
              <p className="font-semibold">{scanResult.fiber}g</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-muted-foreground">Sodio</p>
              <p className="font-semibold">{scanResult.sodium}mg</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-muted-foreground">Azúcar</p>
              <p className="font-semibold">{scanResult.sugar}g</p>
            </div>
          </div>
        </Card>

        {/* Alergenos */}
        {scanResult.allergens.length > 0 && (
          <Alert>
            <AlertCircle size={16} />
            <AlertDescription>
              <strong>Contiene alérgenos:</strong> {scanResult.allergens.join(', ')}
            </AlertDescription>
          </Alert>
        )}

        {/* Recomendaciones */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4">Recomendaciones Nutricionales</h4>
          <div className="space-y-3">
            {scanResult.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-3">
                <CheckCircle size={16} className="text-success mt-0.5 flex-shrink-0" />
                <p className="text-sm">{rec}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Acciones */}
        <div className="flex space-x-3">
          <Button className="flex-1 bg-primary hover:bg-primary-dark">
            Agregar a Mi Plan
          </Button>
          <Button variant="outline" className="flex-1">
            Ver Recetas Similares
          </Button>
        </div>
      </motion.div>
    );
  };

  const renderReceiptResult = () => {
    const totalSpent = receiptItems.reduce((sum, item) => sum + item.price, 0);
    const categories = [...new Set(receiptItems.map(item => item.category))];

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Resumen del ticket */}
        <Card className="p-6">
          <h3 className="font-semibold text-lg mb-4">Análisis de tu Compra</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-3 bg-primary/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Gastado</p>
              <p className="text-xl font-bold text-primary">${totalSpent.toFixed(2)}</p>
            </div>
            <div className="text-center p-3 bg-secondary/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Productos</p>
              <p className="text-xl font-bold text-secondary">{receiptItems.length}</p>
            </div>
            <div className="text-center p-3 bg-success/10 rounded-lg">
              <p className="text-sm text-muted-foreground">Categorías</p>
              <p className="text-xl font-bold text-success">{categories.length}</p>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Distribución por categorías:</h4>
            {categories.map(category => {
              const categoryItems = receiptItems.filter(item => item.category === category);
              const categoryTotal = categoryItems.reduce((sum, item) => sum + item.price, 0);
              const percentage = (categoryTotal / totalSpent) * 100;
              
              return (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge className={`text-xs ${getCategoryColor(category)}`}>
                      {category}
                    </Badge>
                    <span className="text-sm">${categoryTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-muted rounded-full h-2">
                      <div 
                        className="bg-primary h-2 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground w-8">{percentage.toFixed(0)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Lista de productos */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4">Productos Escaneados</h4>
          <div className="space-y-3">
            {receiptItems.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{item.name}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge className={`text-xs ${getCategoryColor(item.category)}`}>
                      {item.category}
                    </Badge>
                    <span className="text-sm text-muted-foreground">{item.quantity}</span>
                  </div>
                </div>
                <p className="font-semibold">${item.price.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Sugerencias basadas en la compra */}
        <Card className="p-6">
          <h4 className="font-semibold mb-4">Sugerencias Personalizadas</h4>
          <div className="space-y-3">
            <Alert>
              <Info size={16} />
              <AlertDescription>
                ¡Excelente compra! Has incluido 3 grupos alimentarios principales. 
                Te sugerimos agregar más verduras para una alimentación más balanceada.
              </AlertDescription>
            </Alert>
            
            <Button className="w-full bg-secondary hover:bg-secondary-dark">
              Generar Plan de Comidas con estos Ingredientes
            </Button>
          </div>
        </Card>
      </motion.div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Escaneo Inteligente</h1>
        <p className="text-muted-foreground mt-1">
          Analiza productos y tickets de compra con IA
        </p>
      </div>

      {/* Modo de escaneo */}
      <div className="flex space-x-3">
        <Button
          variant={scanMode === 'product' ? 'default' : 'outline'}
          onClick={() => setScanMode('product')}
          className="flex-1"
        >
          <Package size={16} className="mr-2" />
          Producto
        </Button>
        <Button
          variant={scanMode === 'receipt' ? 'default' : 'outline'}
          onClick={() => setScanMode('receipt')}
          className="flex-1"
        >
          <FileText size={16} className="mr-2" />
          Ticket de Compra
        </Button>
      </div>

      {/* Área de escaneo */}
      {!scanResult && receiptItems.length === 0 && (
        <Card className="p-8">
          <div className="text-center space-y-6">
            <motion.div
              animate={{ rotate: isScanning ? 360 : 0 }}
              transition={{ duration: 2, repeat: isScanning ? Infinity : 0, ease: "linear" }}
              className="mx-auto w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center"
            >
              <Scan size={32} className="text-primary" />
            </motion.div>
            
            <div>
              <h3 className="text-lg font-semibold mb-2">
                {scanMode === 'product' ? 'Escanear Producto' : 'Escanear Ticket de Compra'}
              </h3>
              <p className="text-muted-foreground">
                {scanMode === 'product' 
                  ? 'Toma una foto del producto o etiqueta nutricional'
                  : 'Sube una foto de tu ticket de compra para análisis automático'
                }
              </p>
            </div>

            {isScanning && (
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Analizando con IA...</p>
                <Progress value={scanProgress} className="w-full" />
              </div>
            )}

            {!isScanning && (
              <div className="flex flex-col sm:flex-row gap-3 max-w-sm mx-auto">
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1"
                >
                  <Camera size={16} className="mr-2" />
                  Tomar Foto
                </Button>
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex-1"
                >
                  <Upload size={16} className="mr-2" />
                  Subir Imagen
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Resultados */}
      <AnimatePresence>
        {scanResult && scanMode === 'product' && renderProductResult()}
        {receiptItems.length > 0 && scanMode === 'receipt' && renderReceiptResult()}
      </AnimatePresence>

      {/* Input oculto para archivos */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileUpload}
      />

      {/* Botón para escanear nuevo */}
      {(scanResult || receiptItems.length > 0) && (
        <Button
          variant="outline"
          onClick={() => {
            setScanResult(null);
            setReceiptItems([]);
            setScanProgress(0);
          }}
          className="w-full"
        >
          Escanear Nuevo {scanMode === 'product' ? 'Producto' : 'Ticket'}
        </Button>
      )}
    </div>
  );
}