import React, { ReactNode } from 'react';

interface LegalLayoutProps {
  title: string;
  description: string;
  children: ReactNode;
}

export const LegalLayout: React.FC<LegalLayoutProps> = ({ title, description, children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/10 via-accent/5 to-primary/10 text-foreground">
      <header className="border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-6">
          <a href="/" className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-semibold text-primary-foreground">
              NF
            </div>
            <div>
              <p className="text-lg font-semibold">NutriFamily</p>
              <p className="text-sm text-muted-foreground">{title}</p>
            </div>
          </a>
          <a
            href="/"
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:border-primary hover:text-primary"
          >
            Volver a la app
          </a>
        </div>
      </header>

      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <div className="mb-10 space-y-3">
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        <div className="space-y-8 rounded-2xl border border-border bg-background/90 p-8 shadow-sm">
          {children}
        </div>
        <footer className="mt-10 text-sm text-muted-foreground">
          © {new Date().getFullYear()} NutriFamily. Todos los derechos reservados.
        </footer>
      </main>
    </div>
  );
};
