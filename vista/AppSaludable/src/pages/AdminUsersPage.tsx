/**
 * Página de administración de usuarios - Solo para admins
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { UsuarioAdmin } from '../types/api';
import { toast } from 'sonner';
import { Loader2, Shield, Key, UserX, UserCheck } from 'lucide-react';

export const AdminUsersPage: React.FC = () => {
  const [usuarios, setUsuarios] = useState<UsuarioAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UsuarioAdmin | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cargarUsuarios = async () => {
    setLoading(true);
    try {
      const response = await apiService.getAllUsers();
      if (response.success && response.data) {
        setUsuarios(response.data);
      } else {
        toast.error('Error al cargar usuarios', {
          description: response.error || 'No se pudieron cargar los usuarios',
        });
      }
    } catch (error) {
      toast.error('Error de conexión', {
        description: 'No se pudo conectar con el servidor',
      });
    } finally {
      setLoading(false);
    }
  };

  const abrirModalReset = (usuario: UsuarioAdmin) => {
    setSelectedUser(usuario);
    setNewPassword('');
    setResetModalOpen(true);
  };

  const cerrarModalReset = () => {
    setResetModalOpen(false);
    setSelectedUser(null);
    setNewPassword('');
  };

  const handleResetPassword = async () => {
    if (!selectedUser || !newPassword) {
      toast.error('Error', {
        description: 'Debes ingresar una contraseña',
      });
      return;
    }

    if (newPassword.length < 6) {
      toast.error('Contraseña muy corta', {
        description: 'La contraseña debe tener al menos 6 caracteres',
      });
      return;
    }

    setResetting(true);
    try {
      const response = await apiService.resetUserPassword(
        selectedUser.usr_id,
        newPassword
      );

      if (response.success) {
        toast.success('Contraseña actualizada', {
          description: `La contraseña de ${selectedUser.usr_usuario} fue actualizada exitosamente`,
        });
        cerrarModalReset();
      } else {
        toast.error('Error al resetear contraseña', {
          description: response.error || 'No se pudo actualizar la contraseña',
        });
      }
    } catch (error) {
      toast.error('Error de conexión', {
        description: 'No se pudo conectar con el servidor',
      });
    } finally {
      setResetting(false);
    }
  };

  const handleToggleActive = async (usuario: UsuarioAdmin) => {
    const accion = usuario.usr_activo ? 'desactivar' : 'activar';
    const confirmado = window.confirm(
      `¿Estás seguro de que deseas ${accion} al usuario ${usuario.usr_usuario}?`
    );

    if (!confirmado) return;

    try {
      const response = await apiService.toggleUserActive(usuario.usr_id);

      if (response.success) {
        toast.success(`Usuario ${accion}do`, {
          description: `El usuario ${usuario.usr_usuario} fue ${accion}do exitosamente`,
        });
        cargarUsuarios();
      } else {
        toast.error(`Error al ${accion} usuario`, {
          description: response.error || `No se pudo ${accion} el usuario`,
        });
      }
    } catch (error) {
      toast.error('Error de conexión', {
        description: 'No se pudo conectar con el servidor',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            Panel de Administración
          </h1>
        </div>
        <p className="text-gray-600">
          Gestiona usuarios y resetea contraseñas (Solo administradores)
        </p>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nombre Completo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Correo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usuarios.map((usuario) => (
                <tr key={usuario.usr_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {usuario.usr_usuario}
                    </div>
                    <div className="text-xs text-gray-500">
                      ID: {usuario.usr_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {usuario.usr_nombres} {usuario.usr_apellidos}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {usuario.usr_correo}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${usuario.rol_nombre === 'Administrador'
                        ? 'bg-red-100 text-red-800'
                        : usuario.rol_nombre === 'Nutricionista'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                        }`}
                    >
                      {usuario.rol_nombre}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${usuario.usr_activo
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                        }`}
                    >
                      {usuario.usr_activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => abrirModalReset(usuario)}
                      className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-900"
                      title="Resetear contraseña"
                    >
                      <Key className="w-4 h-4" />
                      Resetear
                    </button>
                    <button
                      onClick={() => handleToggleActive(usuario)}
                      className={`inline-flex items-center gap-1 ${usuario.usr_activo
                        ? 'text-red-600 hover:text-red-900'
                        : 'text-green-600 hover:text-green-900'
                        }`}
                      title={usuario.usr_activo ? 'Desactivar' : 'Activar'}
                    >
                      {usuario.usr_activo ? (
                        <>
                          <UserX className="w-4 h-4" />
                          Desactivar
                        </>
                      ) : (
                        <>
                          <UserCheck className="w-4 h-4" />
                          Activar
                        </>
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {resetModalOpen && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <Key className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-bold text-gray-900">
                  Resetear Contraseña
                </h2>
              </div>

              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Usuario: <span className="font-semibold">{selectedUser.usr_usuario}</span>
                </p>
                <p className="text-sm text-gray-600">
                  Nombre: <span className="font-semibold">
                    {selectedUser.usr_nombres} {selectedUser.usr_apellidos}
                  </span>
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nueva Contraseña
                </label>
                <input
                  type="text"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Ingresa la nueva contraseña"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  autoFocus
                />
                <p className="mt-1 text-xs text-gray-500">
                  Mínimo 6 caracteres. El usuario podrá cambiarla después.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={cerrarModalReset}
                  disabled={resetting}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleResetPassword}
                  disabled={resetting || !newPassword}
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {resetting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Reseteando...
                    </>
                  ) : (
                    'Resetear Contraseña'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
