import React from 'react';
import { LegalLayout } from '../components/static/LegalLayout';

const PrivacyPolicyPage: React.FC = () => {
  return (
    <LegalLayout
      title="Política de Privacidad"
      description="Transparencia sobre cómo recolectamos, usamos y protegemos tu información personal en NutriFamily."
    >
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Información que recopilamos</h2>
        <p>
          Cuando usas NutriFamily recopilamos datos básicos para brindarte una experiencia personalizada:
        </p>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground">
          <li>Datos de registro como nombre, apellidos, usuario y correo electrónico.</li>
          <li>Datos proporcionados voluntariamente sobre tu familia, niños y preferencias nutricionales.</li>
          <li>Registros de progreso, evaluaciones antropométricas y hábitos alimenticios que ingreses.</li>
          <li>Identificadores técnicos (cookies, dirección IP abreviada, tipo de dispositivo) para mantener tu sesión segura.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Cómo usamos tus datos</h2>
        <p className="text-sm text-muted-foreground">
          Utilizamos tu información para ofrecer recomendaciones personalizadas, generar reportes de progreso y facilitar la comunicación con profesionales de la salud que tú autorices. Nunca
          vendemos tus datos a terceros. Solo compartimos información con proveedores necesarios para operar la plataforma (por ejemplo, Firebase Authentication) y siempre bajo acuerdos de
          confidencialidad.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Bases legales y derechos</h2>
        <p className="text-sm text-muted-foreground">
          Tratamos tus datos de acuerdo con el consentimiento otorgado durante el registro y cumpliendo con la Ley de Protección de Datos Personales de Perú y el RGPD donde aplique. Puedes
          solicitar acceso, rectificación, portabilidad o eliminación de tu información escribiendo a{' '}
          <a className="text-primary underline" href="mailto:privacy@nutrifamily.app">
            privacy@nutrifamily.app
          </a>
          .
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Conservación y seguridad</h2>
        <p className="text-sm text-muted-foreground">
          Conservamos los datos mientras mantengas una cuenta activa. Utilizamos cifrado en tránsito (HTTPS), tokenización JWT y controles de acceso basados en roles. Cuando solicitas la eliminación
          de tu cuenta, anonimizamos los identificadores personales según se describe en nuestra página de eliminación de datos.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Cambios a esta política</h2>
        <p className="text-sm text-muted-foreground">
          Publicaremos cualquier actualización en esta página con la fecha de entrada en vigor. Si los cambios son significativos, te notificaremos por correo electrónico o dentro de la aplicación.
        </p>
        <p className="text-xs text-muted-foreground">Última actualización: {new Date().toLocaleDateString()}</p>
      </section>
    </LegalLayout>
  );
};

export default PrivacyPolicyPage;
