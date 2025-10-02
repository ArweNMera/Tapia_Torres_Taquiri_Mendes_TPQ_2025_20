import React, { useState, useEffect } from 'react';
import ConfirmationModal from './ui/ConfirmationModal';
import { useUserApi } from '../hooks/useApi';
import { useAuth } from '../contexts/AuthContext';
import type { UserProfile, UserResponse } from '../types/api';

interface Props {
  onSaved?: (profile: UserResponse) => void;
}

const UserProfileForm: React.FC<Props> = ({ onSaved }) => {
  const [formData, setFormData] = useState<UserProfile>({
    dni: '',
    nombres: '',
    apellidos: '',
    avatar_url: '',
    telefono: '',
    direccion: '',
    genero: undefined,
    fecha_nac: '',
    idioma: 'es',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const { getProfile, updateProfile } = useUserApi();
  const { user } = useAuth();

  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'success' | 'error';
    title: string;
    message?: string;
  }>({ isOpen: false, type: 'success', title: '', message: '' });

  useEffect(() => {
    getProfile.execute();
  }, []);

  useEffect(() => {
    if (getProfile.data) {
      setFormData({
        dni: getProfile.data.dni || '',
        nombres: getProfile.data.usr_nombre || '',
        apellidos: getProfile.data.usr_apellido || '',
        avatar_url: getProfile.data.avatar_url || user?.avatar_url || '',
        telefono: getProfile.data.telefono || '',
        direccion: getProfile.data.direccion || '',
        genero: getProfile.data.genero,
        fecha_nac: getProfile.data.fecha_nac || '',
        idioma: getProfile.data.idioma || 'es',
      });
    }
  }, [getProfile.data, user?.avatar_url]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validate = () => {
    if (!formData.nombres?.trim() || !formData.apellidos?.trim()) {
      setLocalError('Nombres y apellidos son obligatorios.');
      return false;
    }
    setLocalError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    // Normalizar fecha DD/MM/YYYY -> YYYY-MM-DD si aplica
    const payload: UserProfile = { ...formData };
    if (payload.fecha_nac && /^\d{2}\/\d{2}\/\d{4}$/.test(payload.fecha_nac)) {
      const [dd, mm, yyyy] = payload.fecha_nac.split('/');
      payload.fecha_nac = `${yyyy}-${mm}-${dd}`;
    }

    const result = await updateProfile.execute(payload);
    if (!result) {
      setConfirmModal({
        isOpen: true,
        type: 'error',
        title: 'Error al actualizar',
        message: String(updateProfile.error || 'No se pudo actualizar el perfil.'),
      });
      return;
    }
    setIsEditing(false);
    onSaved?.(result);
    window.dispatchEvent(new CustomEvent('profile:updated'));
    getProfile.execute();
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Perfil actualizado',
      message: 'Tu información se guardó correctamente.',
    });
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'No especificado';
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const calculateAge = (birthDate: string) => {
    if (!birthDate) return 'No especificado';
    const birth = new Date(birthDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - birth.getTime());
    const diffYears = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 365.25));
    return `${diffYears} años`;
  };

  if (getProfile.loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-pulse text-gray-500">Cargando perfil…</div>
      </div>
    );
  }

  const initials = `${(formData.nombres || 'U').charAt(0)}${(formData.apellidos || '').charAt(0)}`.toUpperCase();
  const ageYears = formData.fecha_nac ? Math.floor((Date.now() - new Date(formData.fecha_nac).getTime()) / (1000 * 60 * 60 * 24 * 365.25)) : null;
  const isSelfManaged = typeof ageYears === 'number' ? ageYears >= 13 : null;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Encabezado compacto */}
      <div className="rounded-xl p-5 mb-6 shadow-sm border border-emerald-100 bg-gradient-to-r from-emerald-50 to-green-50">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center text-lg font-semibold text-gray-700">
            {formData.avatar_url ? (
              <img src={formData.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
            ) : (
              <span>{initials}</span>
            )}
          </div>
          <div className="flex-1">
            <div className="text-xl font-semibold text-gray-900">
              {formData.nombres && formData.apellidos
                ? `${formData.nombres} ${formData.apellidos}`
                : getProfile.data?.usr_usuario || 'Usuario'}
            </div>
            <div className="text-sm text-gray-500">{getProfile.data?.usr_correo || '—'}</div>
            {formData.fecha_nac && (
              <div className="text-sm text-gray-500">{calculateAge(formData.fecha_nac)} • Nacido el {formatDate(formData.fecha_nac)}</div>
            )}
            {typeof isSelfManaged === 'boolean' && (
              <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${isSelfManaged ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                {isSelfManaged ? 'Autogestionado (≥13 años)' : 'Gestionado por tutor (<13 años)'}
              </span>
            )}
          </div>
          {/* Botones del encabezado removidos para evitar doble edición */}
        </div>
      </div>

      {/* Tarjeta de información personal */}
      <div className="bg-white border border-emerald-100 rounded-xl p-6 shadow-sm mb-6">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Información Personal</h2>
            <p className="text-sm text-gray-500">Gestiona tu información personal y preferencias</p>
          </div>
          {!isEditing && (
            <button onClick={() => setIsEditing(true)} className="px-3 py-2 rounded-md bg-green-600 text-white text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-400">Editar</button>
          )}
        </div>

        {isEditing ? (
          <form id="user-profile-form" onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">DNI</label>
                <input name="dni" value={formData.dni} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Nombres</label>
                <input name="nombres" value={formData.nombres} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Apellidos</label>
                <input name="apellidos" value={formData.apellidos} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Teléfono</label>
                <input name="telefono" value={formData.telefono} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Fecha de Nacimiento</label>
                <input type="date" name="fecha_nac" value={formData.fecha_nac} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Género</label>
                <select name="genero" value={formData.genero || ''} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                  <option value="">Seleccionar…</option>
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                  <option value="X">Otro</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm text-gray-600 mb-1">Dirección</label>
                <input name="direccion" value={formData.direccion} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">URL del Avatar</label>
                <input name="avatar_url" value={formData.avatar_url} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Idioma</label>
                <select name="idioma" value={formData.idioma} onChange={handleInputChange} className="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
                  <option value="es">Español</option>
                  <option value="en">English</option>
                  <option value="pt">Português</option>
                </select>
              </div>
            </div>

            {localError && (
              <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">{localError}</div>
            )}
            {updateProfile.error && (
              <div className="rounded-md border border-red-200 bg-red-50 text-red-700 px-3 py-2 text-sm">{String(updateProfile.error)}</div>
            )}

            <div className="flex gap-3">
              <button type="submit" disabled={updateProfile.loading} className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50">
                {updateProfile.loading ? 'Guardando…' : 'Guardar cambios'}
              </button>
              <button type="button" onClick={() => setIsEditing(false)} className="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200">Cancelar</button>
            </div>
          </form>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h3 className="text-sm text-gray-500">DNI/Cédula</h3>
                <p className="text-gray-900">{formData.dni || 'No especificado'}</p>
              </div>
              <div>
                <h3 className="text-sm text-gray-500">Teléfono</h3>
                <p className="text-gray-900">{formData.telefono || 'No especificado'}</p>
              </div>
              <div>
                <h3 className="text-sm text-gray-500">Género</h3>
                <p className="text-gray-900">
                  {formData.genero === 'M' ? 'Masculino' : formData.genero === 'F' ? 'Femenino' : formData.genero === 'X' ? 'Otro' : 'No especificado'}
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm text-gray-500">Dirección</h3>
                <p className="text-gray-900">{formData.direccion || 'No especificado'}</p>
              </div>
              <div>
                <h3 className="text-sm text-gray-500">Idioma</h3>
                <p className="text-gray-900">{formData.idioma === 'es' ? 'Español' : formData.idioma === 'en' ? 'English' : formData.idioma === 'pt' ? 'Português' : 'Español'}</p>
              </div>
              {/* Eliminado: Usuario desde */}
            </div>
          </div>
        )}
      </div>

      {/* Tarjeta de cuenta */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información de la Cuenta</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm text-gray-500">Usuario</h3>
            <p className="text-gray-900">{getProfile.data?.usr_usuario}</p>
          </div>
          <div>
            <h3 className="text-sm text-gray-500">Correo electrónico</h3>
            <p className="text-gray-900">{getProfile.data?.usr_correo}</p>
          </div>
          <div>
            <h3 className="text-sm text-gray-500">Rol</h3>
            <p className="text-gray-900">{getProfile.data?.rol_id === 1 ? 'Administrador' : 'Usuario'}</p>
          </div>
          <div>
            <h3 className="text-sm text-gray-500">Estado</h3>
            <span className={`inline-block px-2 py-1 rounded-full text-xs ${getProfile.data?.usr_activo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {getProfile.data?.usr_activo ? 'Activo' : 'Inactivo'}
            </span>
          </div>
        </div>
      </div>

      {/* Nota para <13 años: este aviso depende de isSelfManaged calculado */}
      {typeof isSelfManaged === 'boolean' && !isSelfManaged && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-900">
          Este perfil está administrado por un tutor. Algunas opciones de edición pueden estar limitadas.
        </div>
      )}

      {/* Modal de confirmación (éxito/error) */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, type: 'success', title: '', message: '' })}
        type={confirmModal.type}
        title={confirmModal.title}
        message={confirmModal.message}
      />
    </div>
  );
};

export default UserProfileForm;
