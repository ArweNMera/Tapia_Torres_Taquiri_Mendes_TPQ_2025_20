import React from 'react';
import { LegalLayout } from '../components/static/LegalLayout';

const DeleteDataPage: React.FC = () => {
  return (
    <LegalLayout
      title="Eliminación de Datos y Cierre de Cuenta"
      description="Opciones para solicitar la eliminación de tu cuenta de NutriFamily y los datos asociados."
    >
      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Solicitar la eliminación desde la app</h2>
        <p className="text-sm text-muted-foreground">
          Si has iniciado sesión, puedes eliminar tu cuenta desde el panel de configuración accediendo a <strong>Configuración &gt; Seguridad y privacidad &gt; Eliminar cuenta definitivamente</strong>. La acción cerrará tu sesión y anonimizaremos la información personal asociada con tu usuario.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Endpoint para eliminar cuenta</h2>
        <p className="text-sm text-muted-foreground">
          También puedes realizar la solicitud mediante nuestra API autenticada. Envía una petición DELETE a:
        </p>
        <div className="rounded-lg border border-border bg-muted/40 p-4 text-sm font-mono text-muted-foreground">
          DELETE https://nutricion-dd80c.web.app/api/v1/usuarios/me
        </div>
        <p className="text-sm text-muted-foreground">
          Debes incluir tu token de acceso válido en el encabezado <code>Authorization: Bearer {"<token>"}</code>. Recibirás una confirmación en formato JSON cuando los datos hayan sido anonimizados.
        </p>
        <div className="rounded-lg border border-border bg-muted/40 p-4 text-xs font-mono leading-5 text-muted-foreground">
{`curl -X DELETE \\
  https://nutricion-dd80c.web.app/api/v1/usuarios/me \\
  -H "Authorization: Bearer <tu_token>"`}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Solicitud manual por correo</h2>
        <p className="text-sm text-muted-foreground">
          Si no puedes acceder a tu cuenta, envía un correo a{' '}
          <a className="text-primary underline" href="mailto:privacy@nutrifamily.app">
            privacy@nutrifamily.app
          </a>{' '}
          indicando el correo con el que te registraste y el motivo de la eliminación. Responderemos dentro de 5 días hábiles para completar el proceso.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Qué ocurre con tus datos</h2>
        <ul className="list-disc space-y-2 pl-5 text-sm text-muted-foreground">
          <li>Tus identificadores personales se reemplazan por valores anónimos y se marca la cuenta como inactiva.</li>
          <li>Los registros agregados (estadísticas y métricas históricas) se conservan solo con fines analíticos y sin asociarlos a tu identidad.</li>
          <li>Los datos de niños asociados se disocian del tutor eliminado para prevenir accesos no autorizados.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Soporte</h2>
        <p className="text-sm text-muted-foreground">
          Si necesitas ayuda adicional puedes escribirnos a{' '}
          <a className="text-primary underline" href="mailto:soporte@nutrifamily.app">
            soporte@nutrifamily.app
          </a>{' '}
          o a través del formulario de contacto dentro de la aplicación.
        </p>
      </section>
    </LegalLayout>
  );
};

export default DeleteDataPage;
