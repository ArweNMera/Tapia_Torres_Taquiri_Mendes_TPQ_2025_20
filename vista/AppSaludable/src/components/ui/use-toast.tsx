/**
 * Hook para usar toasts con sonner
 */
import { toast as sonnerToast } from 'sonner';

interface ToastOptions {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
}

export function useToast() {
  const toast = ({ title, description, variant = 'default' }: ToastOptions) => {
    const message = title || description || '';
    const desc = title && description ? description : undefined;

    switch (variant) {
      case 'destructive':
        sonnerToast.error(message, { description: desc });
        break;
      case 'success':
        sonnerToast.success(message, { description: desc });
        break;
      default:
        sonnerToast(message, { description: desc });
    }
  };

  return { toast };
}
