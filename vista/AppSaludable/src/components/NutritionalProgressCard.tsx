import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';

interface NutritionalProgressCardProps {
  title: string;
  current: number;
  target: number;
  unit: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  status?: 'optimal' | 'warning' | 'critical';
  description?: string;
  color?: string;
}

export function NutritionalProgressCard({
  title,
  current,
  target,
  unit,
  trend,
  trendValue,
  status = 'optimal',
  description,
  color = 'bg-primary'
}: NutritionalProgressCardProps) {
  const percentage = Math.min((current / target) * 100, 100);
  
  const getStatusColor = () => {
    switch (status) {
      case 'optimal': return 'bg-success text-white';
      case 'warning': return 'bg-warning text-white';
      case 'critical': return 'bg-destructive text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'optimal': return 'Óptimo';
      case 'warning': return 'Atención';
      case 'critical': return 'Crítico';
      default: return 'Normal';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return <TrendingUp size={14} className="text-success" />;
      case 'down': return <TrendingDown size={14} className="text-destructive" />;
      case 'stable': return <Minus size={14} className="text-muted-foreground" />;
      default: return null;
    }
  };

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-sm mb-1">{title}</h3>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold">{current}</span>
            <span className="text-sm text-muted-foreground">/ {target} {unit}</span>
          </div>
        </div>
        
        <Badge className={`text-xs ${getStatusColor()}`}>
          {getStatusLabel()}
        </Badge>
      </div>

      <div className="space-y-2 mb-3">
        <Progress value={percentage} className="h-2" />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0</span>
          <span>{percentage.toFixed(0)}%</span>
          <span>{target}</span>
        </div>
      </div>

      {(trend && trendValue !== undefined) && (
        <div className="flex items-center space-x-2 mb-2">
          {getTrendIcon()}
          <span className="text-xs text-muted-foreground">
            {trend === 'up' ? '+' : trend === 'down' ? '-' : ''}{trendValue}{unit} vs. ayer
          </span>
        </div>
      )}

      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </Card>
  );
}