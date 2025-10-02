import React from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel,
} from "./alert-dialog";
import { AlertTriangle } from "lucide-react@0.487.0";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  isLoading?: boolean;
}

const ActionConfirmModal: React.FC<Props> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  isLoading = false,
}) => {
  return (
    <AlertDialog open={isOpen} onOpenChange={(o) => !isLoading && !o && onClose()}>
      <AlertDialogContent className="w-[30vw] max-w-[480px] min-w-[280px] rounded-3xl border-4 border-red-500 p-6 !bg-white">
        <div className="flex flex-col items-center text-center space-y-3 py-2">
          <AlertTriangle className="h-12 w-12 text-red-500" />
          <AlertDialogHeader className="space-y-2">
            <AlertDialogTitle className="text-xl font-bold text-gray-900">
              {title}
            </AlertDialogTitle>
            {description && (
              <AlertDialogDescription className="text-sm text-gray-700">
                {description}
              </AlertDialogDescription>
            )}
          </AlertDialogHeader>
        </div>

        <AlertDialogFooter className="sm:justify-center gap-2 pt-3 flex-col sm:flex-row">
          <AlertDialogAction
            onClick={onConfirm}
            disabled={isLoading}
            className="w-full rounded-xl px-8 py-2.5 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ backgroundColor: '#dc2626', color: '#000000' }}
          >
            {isLoading ? "Procesando..." : confirmText}
          </AlertDialogAction>
          <AlertDialogCancel
            onClick={onClose}
            disabled={isLoading}
            className="w-full rounded-xl"
          >
            {cancelText}
          </AlertDialogCancel>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default ActionConfirmModal;