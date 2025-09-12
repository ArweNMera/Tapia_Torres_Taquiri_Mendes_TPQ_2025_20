import { ReactNode } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { motion } from 'motion/react';

interface HealthMetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: ReactNode;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    value: string;
    period: string;
  };
  status?: 'excellent' | 'good' | 'fair' | 'poor';
  description?: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export function HealthMetricCard({
  title,
  value,
  unit,
  icon,
  trend,
  status = 'good',
  description,
  actionText,
  onAction,
  className = ''
}: HealthMetricCardProps) {
  const getStatusColor = () => {
    switch (status) {
      case 'excellent': return 'bg-success text-white';
      case 'good': return 'bg-primary text-white';
      case 'fair': return 'bg-warning text-white';
      case 'poor': return 'bg-destructive text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'excellent': return 'Excelente';
      case 'good': return 'Bueno';
      case 'fair': return 'Regular';
      case 'poor': return 'Necesita atención';
      default: return 'Normal';
    }
  };

  const getTrendColor = () => {
    if (!trend) return '';
    switch (trend.direction) {
      case 'up': return 'text-success';
      case 'down': return 'text-destructive';
      case 'stable': return 'text-muted-foreground';
      default: return '';
    }
  };

  const getTrendSymbol = () => {
    if (!trend) return '';
    switch (trend.direction) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Card className={`p-6 hover:shadow-lg transition-all duration-200 ${className}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-primary/10 rounded-lg">
              {icon}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{title}</h3>
              <Badge className={`mt-1 text-xs ${getStatusColor()}`}>
                {getStatusLabel()}
              </Badge>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-gray-900">{value}</span>
            {unit && <span className="text-lg text-muted-foreground">{unit}</span>}
          </div>

          {trend && (
            <div className={`flex items-center space-x-2 text-sm ${getTrendColor()}`}>
              <span>{getTrendSymbol()}</span>
              <span>{trend.value} {trend.period}</span>
            </div>
          )}

          {description && (
            <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
          )}

          {actionText && onAction && (
            <button
              onClick={onAction}
              className="text-sm text-primary hover:text-primary-dark font-medium transition-colors"
            >
              {actionText} →
            </button>
          )}
        </div>
      </Card>
    </motion.div>
  );
}