import { Toaster as Sonner } from "sonner";

export function Toaster() {
  return (
    <Sonner
      position="top-right"
      toastOptions={{
        classNames: {
          toast: "rounded-xl shadow-lg border",
          title: "font-semibold",
          description: "text-sm",
          success: "bg-emerald-50 border-emerald-200 text-emerald-900",
          error: "bg-red-50 border-red-200 text-red-900",
          warning: "bg-amber-50 border-amber-200 text-amber-900",
          info: "bg-blue-50 border-blue-200 text-blue-900",
        },
      }}
      richColors
    />
  );
}
