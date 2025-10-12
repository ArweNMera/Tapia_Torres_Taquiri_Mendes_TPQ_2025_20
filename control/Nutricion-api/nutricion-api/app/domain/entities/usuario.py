"""
Entidad Usuario - Representa un usuario del sistema.
Entidad pura de dominio sin dependencias de frameworks.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Usuario:
    """
    Entidad de dominio para Usuario.
    Representa un usuario del sistema con sus atributos básicos.
    """

    usr_id: int
    usr_usuario: str
    usr_correo: str
    usr_nombre: str | None
    usr_apellido: str | None
    usr_dni: str | None
    rol_id: int
    usr_activo: bool
    creado_en: datetime
    actualizado_en: datetime | None = None

    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.usr_usuario or len(self.usr_usuario.strip()) == 0:
            raise ValueError("El usuario no puede estar vacío")

        if not self.usr_correo or "@" not in self.usr_correo:
            raise ValueError("El correo debe ser válido")

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        nombre = self.usr_nombre or ""
        apellido = self.usr_apellido or ""
        return f"{nombre} {apellido}".strip() or self.usr_usuario

    def is_active(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.usr_activo


@dataclass
class UsuarioPerfil:
    """
    Entidad de dominio para el perfil del usuario.
    Información adicional del usuario.
    """

    usrper_id: int
    usr_id: int
    usrper_avatar_url: str | None = None
    usrper_telefono: str | None = None
    usrper_direccion: str | None = None
    usrper_genero: str | None = None
    usrper_fecha_nac: str | None = None
    usrper_idioma: str = "es-PE"
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None


@dataclass
class Rol:
    """
    Entidad de dominio para Rol.
    Representa un rol del sistema.
    """

    rol_id: int
    rol_codigo: str
    rol_nombre: str
    creado_en: datetime
    actualizado_en: datetime | None = None

    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.rol_codigo or len(self.rol_codigo.strip()) == 0:
            raise ValueError("El código de rol no puede estar vacío")

        if not self.rol_nombre or len(self.rol_nombre.strip()) == 0:
            raise ValueError("El nombre de rol no puede estar vacío")

    def is_admin(self) -> bool:
        """Verifica si es un rol de administrador"""
        return self.rol_codigo in ("ADMIN", "SUPERADMIN")

    def can_manage_children(self) -> bool:
        """Verifica si el rol puede gestionar niños"""
        return self.rol_codigo in ("PADRE", "PADRES", "TUTOR", "ADMIN", "SUPERADMIN")
