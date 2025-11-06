import React, { memo, useCallback, useMemo } from 'react';
import { Star } from 'lucide-react';
import { cn } from '../ui/utils';

interface RatingStarsProps {
  rating: number;
  onChange?: (rating: number) => void;
  readonly?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const RatingStarsComponent: React.FC<RatingStarsProps> = ({
  rating,
  onChange,
  readonly = false,
  size = 'md',
}) => {
  // Memoizar el objeto de clases para evitar recrearlo en cada render
  const sizeClasses = useMemo(() => ({
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }), []);

  // Memoizar el handler para evitar recrearlo en cada render
  const handleClick = useCallback((value: number) => {
    if (!readonly && onChange) {
      onChange(value);
    }
  }, [readonly, onChange]);

  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((value) => (
        <button
          key={value}
          type="button"
          onClick={() => handleClick(value)}
          disabled={readonly}
          className={cn(
            'transition-all',
            !readonly && 'hover:scale-110 cursor-pointer',
            readonly && 'cursor-default'
          )}
        >
          <Star
            className={cn(
              sizeClasses[size],
              value <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300',
              'transition-colors'
            )}
          />
        </button>
      ))}
    </div>
  );
};

// Exportar componente memoizado
export const RatingStars = memo(RatingStarsComponent);
