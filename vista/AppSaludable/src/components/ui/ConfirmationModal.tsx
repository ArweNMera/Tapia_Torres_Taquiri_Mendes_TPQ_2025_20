import React from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogFooter,
  AlertDialogAction,
} from "./alert-dialog";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react@0.487.0";

export type ModalType = "success" | "error" | "warning";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  type: ModalType;
  title: string;
  message?: string;
  buttonText?: string;
}

const ConfirmationModal: React.FC<Props> = ({
  isOpen,
  onClose,
  type,
  title,
  message,
  buttonText = "Aceptar",
}) => {
  const borderColors = {
    success: "border-emerald-500",
    error: "border-red-500",
    warning: "border-amber-500",
  } as const;

  const textColors = {
    success: "text-emerald-600",
    error: "text-red-600",
    warning: "text-amber-600",
  } as const;

  const icon = {
    success: <CheckCircle2 className="h-14 w-14 text-emerald-500" />,
    error: <XCircle className="h-14 w-14 text-red-500" />,
    warning: <AlertCircle className="h-14 w-14 text-amber-500" />,
  }[type];

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent className={`w-[30vw] max-w-[480px] min-w-[280px] border-4 ${borderColors[type]} rounded-3xl p-6 !bg-white`}>
        <div className="flex flex-col items-center text-center space-y-6 py-2">
          <div className="flex items-center justify-center">{icon}</div>
          <AlertDialogHeader className="space-y-2">
            <AlertDialogTitle className={`text-2xl font-bold ${textColors[type]}`}>
              {title}
            </AlertDialogTitle>
          </AlertDialogHeader>
          {message && <p className="text-base text-gray-700 px-2 leading-relaxed">{message}</p>}
        </div>

        <AlertDialogFooter className="sm:justify-center pt-1">
          <AlertDialogAction
            className="rounded-xl px-10 py-3 text-base"
            onClick={onClose}
            style={{ backgroundColor: '#10b981', color: '#000000' }}
          >
            {buttonText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default ConfirmationModal;
