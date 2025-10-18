import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Paperclip, Bot, User } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Badge } from './ui/badge';
import { motion, AnimatePresence } from 'motion/react';
import { apiService } from '../services/api';
import { toast } from 'sonner';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  file?: {
    name: string;
    type: string;
    size: number;
  };
}

interface ChatBotProps {
  className?: string;
}

export function ChatBot({ className = '' }: ChatBotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: '¡Hola! Soy tu asistente nutricional de NutriFamily 🍎\n\nPuedo recomendarte recetas personalizadas para tus hijos. Solo escribe algo como:\n\n"¿Qué le puedo dar a Juan para el desayuno?"\n"Recomiéndame algo para María en el almuerzo"\n\n¿En qué puedo ayudarte hoy?',
      sender: 'bot',
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const userQuestion = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    try {
      // Extraer nombre del niño del mensaje
      const nombreNino = extraerNombreNino(userQuestion);

      if (nombreNino) {
        // Detectar tipo de comida en el mensaje
        const tipoComida = detectarTipoComida(userQuestion);

        // Llamar al servicio de recomendaciones con el nombre
        const response = await apiService.getChatBotRecommendation(
          nombreNino,
          tipoComida,
          userQuestion
        );

        if (response.success && response.data) {
          const botMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: response.data.recomendacion,
            sender: 'bot',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, botMessage]);
          setIsTyping(false);
          return;
        }
      }

      // Fallback: usar respuesta simulada (modo general)
      const botResponse = generateBotResponse(userQuestion);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error al obtener recomendación:', error);
      // En caso de error, usar respuesta simulada
      const botResponse = generateBotResponse(userQuestion);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: botResponse,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const detectarTipoComida = (mensaje: string): string => {
    const mensajeLower = mensaje.toLowerCase();
    if (mensajeLower.includes('desayuno') || mensajeLower.includes('mañana')) {
      return 'DESAYUNO';
    }
    if (mensajeLower.includes('almuerzo') || mensajeLower.includes('comida') || mensajeLower.includes('mediodía')) {
      return 'ALMUERZO';
    }
    if (mensajeLower.includes('cena') || mensajeLower.includes('noche')) {
      return 'CENA';
    }
    // Por defecto, usar DESAYUNO
    return 'DESAYUNO';
  };

  const extraerNombreNino = (mensaje: string): string | null => {
    // Patrones comunes para extraer nombres
    const patrones = [
      /para\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,  // "para Juan"
      /de\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,    // "de María"
      /a\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,     // "a Pedro"
      /mi\s+hijo\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,  // "mi hijo Carlos"
      /mi\s+hija\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,  // "mi hija Ana"
      /niño\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,  // "niño Luis"
      /niña\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)/i,  // "niña Sofia"
    ];

    for (const patron of patrones) {
      const match = mensaje.match(patron);
      if (match && match[1]) {
        return match[1];
      }
    }

    return null;
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileMessage: Message = {
      id: Date.now().toString(),
      text: `Archivo enviado: ${file.name}`,
      sender: 'user',
      timestamp: new Date(),
      file: {
        name: file.name,
        type: file.type,
        size: file.size,
      },
    };

    setMessages(prev => [...prev, fileMessage]);
    setIsTyping(true);

    // Simular análisis del archivo
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getFileAnalysisResponse(file),
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 2000);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const generateBotResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('receta') || lowerMessage.includes('cocinar')) {
      return '¡Perfecto! Te recomiendo revisar nuestra sección de recetas. ¿Buscas algo específico? Puedo sugerir recetas según las alergias de tu pequeño/a y sus preferencias 👶🍽️';
    }

    if (lowerMessage.includes('peso') || lowerMessage.includes('crecimiento')) {
      return 'El seguimiento del peso es muy importante. He notado que Sofía ha ganado 200g esta semana, ¡excelente progreso! ¿Te gustaría ver sus gráficos de crecimiento detallados? 📈';
    }

    if (lowerMessage.includes('alergia') || lowerMessage.includes('intolerancia')) {
      return 'Las alergias alimentarias requieren mucha atención. Tengo registro de las alergias de tu hijo/a. ¿Necesitas ayuda para encontrar recetas que eviten alérgenos específicos? 🚫🥜';
    }

    if (lowerMessage.includes('nutrición') || lowerMessage.includes('vitaminas')) {
      return 'La nutrición balanceada es clave en esta etapa. Según los datos, Sofía ha consumido el 85% de proteínas hoy. ¿Te gustaría consejos para completar los macronutrientes del día? 🥗';
    }

    if (lowerMessage.includes('hola') || lowerMessage.includes('hi')) {
      return '¡Hola! Me alegra verte por aquí. ¿En qué aspecto de la alimentación de tu pequeño/a puedo ayudarte hoy? 😊';
    }

    return 'Entiendo tu pregunta. Como especialista en nutrición infantil, puedo ayudarte con recetas saludables, seguimiento nutricional, alergias alimentarias y consejos personalizados. ¿Podrías ser más específico/a sobre qué necesitas? 🤔💭';
  };

  const getFileAnalysisResponse = (file: File): string => {
    if (file.type.startsWith('image/')) {
      return '📸 He analizado la imagen. Si es una foto de comida, puedo ayudarte a identificar ingredientes y calcular valores nutricionales aproximados. También puedo sugerir modificaciones para hacerla más saludable para tu pequeño/a.';
    }

    if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      return '📄 He recibido tu documento PDF. Si contiene informes médicos o análisis nutricionales, puedo ayudarte a interpretarlos y crear un plan alimentario personalizado basado en esta información.';
    }

    return '📎 Archivo recibido correctamente. Puedo analizar imágenes de comida, documentos médicos, y listas de ingredientes. ¿Podrías contarme qué tipo de información contiene para darte la mejor ayuda posible?';
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return '🖼️';
    if (type === 'application/pdf') return '📄';
    if (type.startsWith('text/')) return '📝';
    return '📎';
  };

  return (
    <>
      {/* Floating Chat Button */}
      <motion.div
        className={`fixed bottom-6 right-6 z-50 ${className}`}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <Button
          onClick={toggleChat}
          size="lg"
          className={`h-14 w-14 rounded-full shadow-lg transition-all duration-300 ${isOpen
            ? 'bg-red-500 hover:bg-red-600'
            : 'bg-green-600 hover:bg-green-700'
            }`}
        >
          <AnimatePresence mode="wait">
            {isOpen ? (
              <motion.div
                key="close"
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <X size={24} />
              </motion.div>
            ) : (
              <motion.div
                key="chat"
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="relative"
              >
                <MessageCircle size={24} />
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </Button>
      </motion.div>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed bottom-24 right-6 z-40 w-80 lg:w-96"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <Card className="shadow-xl border-0 overflow-hidden bg-white/95 backdrop-blur-sm">
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-green-600 to-green-500 p-4 text-white">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <Bot size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold">Asistente Nutricional</h3>
                    <p className="text-xs text-green-100">
                      Especialista en alimentación infantil
                    </p>
                  </div>
                </div>
              </div>

              {/* Chat Messages */}
              <ScrollArea className="h-80 p-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                    >
                      <div
                        className={`max-w-[85%] rounded-lg p-3 ${message.sender === 'user'
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-100 text-gray-800'
                          }`}
                      >
                        {message.file && (
                          <div className="mb-2 p-2 bg-white/20 rounded text-xs">
                            <div className="flex items-center space-x-2">
                              <span>{getFileIcon(message.file.type)}</span>
                              <span className="truncate">{message.file.name}</span>
                            </div>
                            <span className="text-xs opacity-75">
                              {(message.file.size / 1024).toFixed(1)} KB
                            </span>
                          </div>
                        )}
                        <p className="text-sm">{message.text}</p>
                        <p
                          className={`text-xs mt-1 opacity-75 ${message.sender === 'user' ? 'text-right' : 'text-left'
                            }`}
                        >
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex space-x-1">
                          {[0, 1, 2].map((i) => (
                            <motion.div
                              key={i}
                              className="w-2 h-2 bg-gray-400 rounded-full"
                              animate={{ opacity: [0.4, 1, 0.4] }}
                              transition={{
                                repeat: Infinity,
                                duration: 1.5,
                                delay: i * 0.2,
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* Chat Input */}
              <div className="p-4 border-t bg-gray-50/50">
                <div className="flex space-x-2">
                  <div className="flex-1 relative">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      placeholder="Escribe tu consulta nutricional..."
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handleSendMessage();
                        }
                      }}
                      className="pr-10"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1 h-8 w-8"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Paperclip size={16} />
                    </Button>
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim()}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Send size={16} />
                  </Button>
                </div>

                {/* Hidden File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept="image/*,.pdf,.txt,.doc,.docx"
                  onChange={handleFileUpload}
                />

                {/* Quick Actions */}
                <div className="flex flex-wrap gap-2 mt-3">
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-green-50 text-xs"
                    onClick={() => setInputMessage('¿Qué me recomiendas para el desayuno?')}
                  >
                    🌅 Desayuno
                  </Badge>
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-green-50 text-xs"
                    onClick={() => setInputMessage('¿Qué me recomiendas para el almuerzo?')}
                  >
                    🍽️ Almuerzo
                  </Badge>
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-green-50 text-xs"
                    onClick={() => setInputMessage('¿Qué me recomiendas para la cena?')}
                  >
                    🌙 Cena
                  </Badge>
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
