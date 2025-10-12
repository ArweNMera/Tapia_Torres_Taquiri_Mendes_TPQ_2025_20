import React from 'react';
import { LegalLayout } from '../components/static/LegalLayout';

const TermsPage: React.FC = () => {
  return (
    <LegalLayout
      title="Términos y Condiciones de Uso"
      description="Lee atentamente los términos que rigen el uso de la aplicación NutriFamily."
    >
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">1. Aceptación</h2>
        <p className="text-sm text-muted-foreground">
          Al crear una cuenta o utilizar NutriFamily confirmas que eres mayor de edad o cuentas con la autorización de un padre, madre o tutor. Estos términos constituyen un contrato vinculante entre
          tú y NutriFamily, por lo que te pedimos revisarlos con detenimiento.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">2. Uso permitido</h2>
        <p className="text-sm text-muted-foreground">
          NutriFamily proporciona herramientas de educación y seguimiento nutricional para familias y profesionales. No debes reutilizar la plataforma para fines ilícitos, enviar spam, intentar
          obtener acceso no autorizado o vulnerar la seguridad del servicio. Nos reservamos el derecho de suspender cuentas que incumplan estas reglas.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">3. Contenido y precisión</h2>
        <p className="text-sm text-muted-foreground">
          El contenido educativo y las recomendaciones automáticas se basan en datos proporcionados por organismos internacionales y no sustituyen la consulta con un profesional de la salud. Tú eres
          responsable de verificar la exactitud de la información que registras y del uso que hagas de las recomendaciones.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">4. Suscripciones y pagos</h2>
        <p className="text-sm text-muted-foreground">
          El acceso básico es gratuito. Cualquier servicio de pago adicional se comunicará claramente antes de su contratación, indicando precios, periodo de facturación y procedimiento de cancelación.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">5. Propiedad intelectual</h2>
        <p className="text-sm text-muted-foreground">
          Los contenidos, diseños, marcas y código fuente de NutriFamily son propiedad de sus titulares y están protegidos por leyes de derechos de autor. Puedes utilizar la plataforma solo para tus
          necesidades nutricionales personales o familiares.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">6. Limitación de responsabilidad</h2>
        <p className="text-sm text-muted-foreground">
          NutriFamily se ofrece “tal cual”. No garantizamos que el servicio estará libre de interrupciones o errores, aunque trabajamos constantemente para mejorarlo. En la medida permitida por la ley,
          nuestra responsabilidad total por cualquier reclamo no superará los importes que hayas pagado por el servicio durante los 12 meses anteriores.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">7. Rescisión</h2>
        <p className="text-sm text-muted-foreground">
          Puedes dejar de usar NutriFamily en cualquier momento. Si deseas eliminar tu cuenta, sigue las instrucciones publicadas en{' '}
          <a className="text-primary underline" href="/delete-data">
            /delete-data
          </a>
          . También podemos suspender o cerrar tu cuenta ante incumplimientos graves.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">8. Contacto</h2>
        <p className="text-sm text-muted-foreground">
          Puedes contactar con nosotros en{' '}
          <a className="text-primary underline" href="mailto:soporte@nutrifamily.app">
            soporte@nutrifamily.app
          </a>
          . Responderemos a tus consultas en un plazo máximo de 7 días hábiles.
        </p>
        <p className="text-xs text-muted-foreground">Última actualización: {new Date().toLocaleDateString()}</p>
      </section>
    </LegalLayout>
  );
};

export default TermsPage;
