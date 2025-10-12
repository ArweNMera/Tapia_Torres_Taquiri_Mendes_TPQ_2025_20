import { ReactNode } from 'react';
import { Card } from './ui/card';

interface NutritionCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: ReactNode;
  color?: 'green' | 'orange' | 'yellow' | 'blue';
  className?: string;
}

export function NutritionCard({
  title,
  value,
  subtitle,
  icon,
  color = 'green',
  className = ''
}: NutritionCardProps) {
  const colorClasses = {
    green: 'bg-gradient-to-br from-green-100 to-green-50 border-green-200',
    orange: 'bg-gradient-to-br from-orange-100 to-orange-50 border-orange-200',
    yellow: 'bg-gradient-to-br from-yellow-100 to-yellow-50 border-yellow-200',
    blue: 'bg-gradient-to-br from-blue-100 to-blue-50 border-blue-200',
  };

  const iconColors = {
    green: 'text-green-600',
    orange: 'text-orange-600',
    yellow: 'text-yellow-600',
    blue: 'text-blue-600',
  };

  return (
    <Card className={`p-4 ${colorClasses[color]} ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-xl font-semibold text-gray-800">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`ml-3 ${iconColors[color]}`}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
