import { useState } from 'react';
import { ChevronRight, Heart, Users, Target } from 'lucide-react';
import { Button } from '../ui/button';
import { ImageWithFallback } from '../figma/ImageWithFallback';

interface OnboardingScreenProps {
  onComplete: () => void;
}

export function OnboardingScreen({ onComplete }: OnboardingScreenProps) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      title: "Bienvenido a NutriFamily",
      subtitle: "Alimentación saludable para toda la familia",
      description: "Descubre recetas nutritivas y planes personalizados para el crecimiento saludable de tus hijos.",
      image: "https://images.unsplash.com/photo-1670698783848-5cf695a1b308?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZm9vZCUyMGZhbWlseSUyMGNoaWxkcmVuJTIwbnV0cml0aW9ufGVufDF8fHx8MTc1NzIyMDQ1MHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      icon: Heart,
      color: "green"
    },
    {
      title: "Planes Personalizados",
      subtitle: "Adaptados a cada edad y necesidad",
      description: "Menús diseñados específicamente para niños de 0-5 años con ingredientes locales y nutritivos.",
      image: "https://images.unsplash.com/photo-1583506955278-b24cb3b0c9b5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2xvcmZ1bCUyMHZlZ2V0YWJsZXMlMjBmcnVpdHMlMjBraWRzJTIwbWVhbHxlbnwxfHx8fDE3NTcyMjA0NTB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      icon: Users,
      color: "orange"
    },
    {
      title: "Seguimiento del Progreso",
      subtitle: "Monitorea el crecimiento saludable",
      description: "Visualiza el progreso nutricional y recibe recomendaciones de nuestros especialistas.",
      image: "https://images.unsplash.com/photo-1744028982670-67ca067bedfa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb29raW5nJTIwcmVjaXBlJTIwaGVhbHRoeSUyMGluZ3JlZGllbnRzfGVufDF8fHx8MTc1NzIyMDQ1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      icon: Target,
      color: "yellow"
    }
  ];

  const currentSlideData = slides[currentSlide];
  const IconComponent = currentSlideData.icon;

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      onComplete();
    }
  };

  const skipToEnd = () => {
    onComplete();
  };

  return (
    <div className="h-screen bg-gradient-to-br from-green-50 to-orange-50 flex flex-col max-w-md mx-auto lg:max-w-lg">
      {/* Skip Button */}
      <div className="flex justify-end p-4">
        <button 
          onClick={skipToEnd}
          className="text-gray-500 hover:text-gray-700 transition-colors"
        >
          Saltar
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        {/* Icon */}
        <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 ${
          currentSlideData.color === 'green' ? 'bg-green-100' :
          currentSlideData.color === 'orange' ? 'bg-orange-100' : 'bg-yellow-100'
        }`}>
          <IconComponent size={40} className={`${
            currentSlideData.color === 'green' ? 'text-green-600' :
            currentSlideData.color === 'orange' ? 'text-orange-600' : 'text-yellow-600'
          }`} />
        </div>

        {/* Image */}
        <div className="w-64 h-48 rounded-2xl overflow-hidden mb-6 shadow-lg">
          <ImageWithFallback
            src={currentSlideData.image}
            alt={currentSlideData.title}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Text Content */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-800 mb-2">
            {currentSlideData.title}
          </h1>
          <h2 className="text-lg text-green-600 mb-4">
            {currentSlideData.subtitle}
          </h2>
          <p className="text-gray-600 leading-relaxed max-w-sm">
            {currentSlideData.description}
          </p>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="p-6">
        {/* Dots Indicator */}
        <div className="flex justify-center mb-6">
          {slides.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full mx-1 transition-colors ${
                index === currentSlide ? 'bg-green-600' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>

        {/* Next Button */}
        <Button 
          onClick={nextSlide}
          className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-xl flex items-center justify-center"
        >
          {currentSlide === slides.length - 1 ? 'Comenzar' : 'Siguiente'}
          <ChevronRight size={20} className="ml-2" />
        </Button>
      </div>
    </div>
  );
}