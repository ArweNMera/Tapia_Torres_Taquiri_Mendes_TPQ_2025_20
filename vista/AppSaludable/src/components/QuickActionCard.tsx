import { ReactNode } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { motion } from 'motion/react';

interface QuickActionCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  actionText: string;
  onAction: () => void;
  priority?: 'high' | 'medium' | 'low';
  category?: string;
  estimatedTime?: string;
  gradient?: string;
}

export function QuickActionCard({
  title,
  description,
  icon,
  actionText,
  onAction,
  priority = 'medium',
  category,
  estimatedTime,
  gradient = 'from-primary/5 to-secondary/5'
}: QuickActionCardProps) {
  const getPriorityColor = () => {
    switch (priority) {
      case 'high': return 'bg-destructive text-white';
      case 'medium': return 'bg-warning text-white';
      case 'low': return 'bg-success text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getPriorityLabel = () => {
    switch (priority) {
      case 'high': return 'Urgente';
      case 'medium': return 'Moderado';
      case 'low': return 'Opcional';
      default: return 'Normal';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Card 
        className={`p-6 cursor-pointer hover:shadow-lg transition-all duration-200 bg-gradient-to-br ${gradient} border-l-4 border-l-primary`}
        onClick={onAction}
      >
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-white rounded-lg shadow-sm">
            {icon}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-gray-900 truncate">{title}</h3>
              <Badge className={`text-xs ml-2 ${getPriorityColor()}`}>
                {getPriorityLabel()}
              </Badge>
            </div>
            
            <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
              {description}
            </p>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                {category && (
                  <span className="px-2 py-1 bg-white/50 rounded">{category}</span>
                )}
                {estimatedTime && (
                  <span className="flex items-center">
                    🕒 {estimatedTime}
                  </span>
                )}
              </div>
              
              <span className="text-sm font-medium text-primary group-hover:text-primary-dark transition-colors">
                {actionText} →
              </span>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}