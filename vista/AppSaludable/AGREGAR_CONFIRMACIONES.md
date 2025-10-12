# 📋 Guía para Agregar Modales de Confirmación

## Componentes que ya tienen modales:
- ✅ `UserProfileForm.tsx` - Editar perfil (tiene ConfirmationModal)
- ✅ `CreateChildForm.tsx` - Registrar niño (tiene ConfirmationModal para éxito/error)

## Componentes que necesitan modales de confirmación:

### 1. **CreateChildForm.tsx** - Agregar confirmación ANTES de guardar

```typescript
// Agregar al inicio del componente (después de los otros estados):
const [actionConfirmModal, setActionConfirmModal] = useState<{
  isOpen: boolean;
  action: 'save' | null;
}>({ isOpen: false, action: null });

// Modificar handleSubmit para mostrar confirmación primero:
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // Validaciones...
  if (!formData.nin_nombres || !formData.nin_apellidos...) {
    // ... validaciones existentes
    return;
  }

  // Mostrar modal de confirmación
  setActionConfirmModal({ isOpen: true, action: 'save' });
};

// Crear función para confirmar guardado:
const confirmSave = async () => {
  setActionConfirmModal({ isOpen: false, action: null });

  // Código existente de guardado...
  const fullName = `${formData.nin_nombres.trim()} ${formData.nin_apellidos.trim()}`;
  // ... resto del código de guardado
};

// Agregar al final del JSX (antes del cierre del div principal):
<ActionConfirmModal
  isOpen={actionConfirmModal.isOpen}
  onClose={() => setActionConfirmModal({ isOpen: false, action: null })}
  onConfirm={confirmSave}
  title="¿Registrar nuevo niño?"
  description={`Se creará el perfil de ${formData.nin_nombres} ${formData.nin_apellidos} con sus datos antropométricos.`}
  confirmText="Sí, registrar"
  cancelText="Cancelar"
  isLoading={createChildProfile.loading}
/>
```

---

### 2. **ChildProfileView.tsx** - Múltiples confirmaciones

```typescript
// Importar ActionConfirmModal:
import ActionConfirmModal from '../ui/ActionConfirmModal';

// Agregar estados para confirmaciones:
const [actionConfirmModal, setActionConfirmModal] = useState<{
  isOpen: boolean;
  action: 'edit' | 'addMeasurement' | 'addAllergy' | 'removeAllergy' | 'assignEntity' | null;
  data?: any;
}>({ isOpen: false, action: null, data: null });

// Para EDITAR INFORMACIÓN DEL NIÑO:
const handleEditChild = () => {
  setActionConfirmModal({
    isOpen: true,
    action: 'edit',
    data: editedChildData
  });
};

const confirmEditChild = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  // Código existente de actualización...
  const result = await updateNino.execute(childId, data);
  if (result) {
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Información actualizada',
      message: 'Los datos del niño se actualizaron correctamente.'
    });
  }
};

// Para AGREGAR MEDICIÓN ANTROPOMÉTRICA:
const handleAddMeasurement = (e: React.FormEvent) => {
  e.preventDefault();

  if (!newMeasurement.ant_peso_kg || !newMeasurement.ant_talla_cm) {
    setConfirmModal({
      isOpen: true,
      type: 'error',
      title: 'Campos incompletos',
      message: 'Por favor, completa peso y talla.'
    });
    return;
  }

  setActionConfirmModal({
    isOpen: true,
    action: 'addMeasurement',
    data: newMeasurement
  });
};

const confirmAddMeasurement = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  const measurementData: AnthropometryCreate = {
    ant_peso_kg: parseFloat(data.ant_peso_kg),
    ant_talla_cm: parseFloat(data.ant_talla_cm),
    ant_fecha: data.ant_fecha,
  };

  const result = await addAnthropometry.execute(childId, measurementData);

  if (result) {
    await evaluateNutritionalStatus.execute(childId);
    await getChildWithData.execute(childId);

    setNewMeasurement({
      ant_peso_kg: '',
      ant_talla_cm: '',
      ant_fecha: new Date().toISOString().split('T')[0],
    });
    setShowAddMeasurement(false);

    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Medición agregada',
      message: 'La medición se agregó y el estado nutricional se actualizó.'
    });
  }
};

// Para AGREGAR ALERGIA:
const handleAddAllergy = (allergyCode: string, allergyName: string) => {
  setActionConfirmModal({
    isOpen: true,
    action: 'addAllergy',
    data: { code: allergyCode, name: allergyName }
  });
};

const confirmAddAllergy = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  const result = await addAllergy.execute(childId, {
    ta_codigo: data.code,
    severidad: 'LEVE'
  });

  if (result) {
    await getChildWithData.execute(childId);
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Alergia agregada',
      message: `Se agregó la alergia: ${data.name}`
    });
  }
};

// Para ELIMINAR ALERGIA:
const handleRemoveAllergy = (allergyId: number, allergyName: string) => {
  setActionConfirmModal({
    isOpen: true,
    action: 'removeAllergy',
    data: { id: allergyId, name: allergyName }
  });
};

const confirmRemoveAllergy = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  const result = await removeAllergy.execute(childId, data.id);

  if (result) {
    await getChildWithData.execute(childId);
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Alergia eliminada',
      message: `Se eliminó la alergia: ${data.name}`
    });
  }
};

// Para ASOCIAR ENTIDAD:
const handleAssignEntity = (entityId: number, entityName: string) => {
  setActionConfirmModal({
    isOpen: true,
    action: 'assignEntity',
    data: { id: entityId, name: entityName }
  });
};

const confirmAssignEntity = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  const result = await updateNino.execute(childId, { ent_id: data.id });

  if (result) {
    await getChildWithData.execute(childId);
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Entidad asociada',
      message: `Se asoció la entidad: ${data.name}`
    });
  }
};

// Agregar al final del JSX:
<ActionConfirmModal
  isOpen={actionConfirmModal.isOpen}
  onClose={() => setActionConfirmModal({ isOpen: false, action: null })}
  onConfirm={() => {
    switch (actionConfirmModal.action) {
      case 'edit':
        confirmEditChild();
        break;
      case 'addMeasurement':
        confirmAddMeasurement();
        break;
      case 'addAllergy':
        confirmAddAllergy();
        break;
      case 'removeAllergy':
        confirmRemoveAllergy();
        break;
      case 'assignEntity':
        confirmAssignEntity();
        break;
    }
  }}
  title={
    actionConfirmModal.action === 'edit' ? '¿Guardar cambios?' :
    actionConfirmModal.action === 'addMeasurement' ? '¿Agregar medición?' :
    actionConfirmModal.action === 'addAllergy' ? '¿Agregar alergia?' :
    actionConfirmModal.action === 'removeAllergy' ? '¿Eliminar alergia?' :
    actionConfirmModal.action === 'assignEntity' ? '¿Asociar entidad?' :
    'Confirmar acción'
  }
  description={
    actionConfirmModal.action === 'edit' ? 'Se actualizará la información del niño.' :
    actionConfirmModal.action === 'addMeasurement' ? `Se agregará la medición: Peso ${actionConfirmModal.data?.ant_peso_kg}kg, Talla ${actionConfirmModal.data?.ant_talla_cm}cm` :
    actionConfirmModal.action === 'addAllergy' ? `Se agregará la alergia: ${actionConfirmModal.data?.name}` :
    actionConfirmModal.action === 'removeAllergy' ? `Se eliminará la alergia: ${actionConfirmModal.data?.name}` :
    actionConfirmModal.action === 'assignEntity' ? `Se asociará la entidad: ${actionConfirmModal.data?.name}` :
    ''
  }
  confirmText="Sí, continuar"
  cancelText="Cancelar"
/>
```

---

### 3. **ChildrenList.tsx** - Eliminar niño

```typescript
// Importar ActionConfirmModal:
import ActionConfirmModal from '../ui/ActionConfirmModal';

// Agregar estado:
const [deleteConfirmModal, setDeleteConfirmModal] = useState<{
  isOpen: boolean;
  childId: number | null;
  childName: string;
}>({ isOpen: false, childId: null, childName: '' });

// Modificar handleDeleteChild:
const handleDeleteChild = (childId: number, childName: string) => {
  setDeleteConfirmModal({
    isOpen: true,
    childId,
    childName
  });
};

const confirmDeleteChild = async () => {
  const { childId, childName } = deleteConfirmModal;
  setDeleteConfirmModal({ isOpen: false, childId: null, childName: '' });

  if (!childId) return;

  const result = await deleteNino.execute(childId);

  if (result) {
    await getNinos.execute();
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Niño eliminado',
      message: `Se eliminó a ${childName} y todos sus registros asociados.`
    });
  }
};

// Agregar al final del JSX:
<ActionConfirmModal
  isOpen={deleteConfirmModal.isOpen}
  onClose={() => setDeleteConfirmModal({ isOpen: false, childId: null, childName: '' })}
  onConfirm={confirmDeleteChild}
  title="¿Eliminar niño?"
  description={`Se eliminará a "${deleteConfirmModal.childName}" y todos sus registros asociados. Esta acción no se puede deshacer.`}
  confirmText="Sí, eliminar"
  cancelText="Cancelar"
  isLoading={deleteNino.loading}
/>
```

---

### 4. **AnthropometryManagement.tsx** - Agregar/editar antropometría

```typescript
// Importar ActionConfirmModal:
import ActionConfirmModal from '../ui/ActionConfirmModal';

// Agregar estado:
const [actionConfirmModal, setActionConfirmModal] = useState<{
  isOpen: boolean;
  action: 'add' | 'edit' | null;
  data?: any;
}>({ isOpen: false, action: null });

// Para AGREGAR:
const handleAddAnthropometry = (e: React.FormEvent) => {
  e.preventDefault();

  // Validaciones...

  setActionConfirmModal({
    isOpen: true,
    action: 'add',
    data: formData
  });
};

const confirmAddAnthropometry = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  // Código existente de guardado...
  const result = await addAnthropometry.execute(childId, data);

  if (result) {
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Medición agregada',
      message: 'La medición antropométrica se agregó correctamente.'
    });
  }
};

// Para EDITAR:
const handleEditAnthropometry = (measurementId: number, data: any) => {
  setActionConfirmModal({
    isOpen: true,
    action: 'edit',
    data: { id: measurementId, ...data }
  });
};

const confirmEditAnthropometry = async () => {
  const { data } = actionConfirmModal;
  setActionConfirmModal({ isOpen: false, action: null });

  // Código de actualización...
  const result = await updateAnthropometry.execute(data.id, data);

  if (result) {
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Medición actualizada',
      message: 'La medición antropométrica se actualizó correctamente.'
    });
  }
};

// Agregar al final del JSX:
<ActionConfirmModal
  isOpen={actionConfirmModal.isOpen}
  onClose={() => setActionConfirmModal({ isOpen: false, action: null })}
  onConfirm={() => {
    if (actionConfirmModal.action === 'add') {
      confirmAddAnthropometry();
    } else if (actionConfirmModal.action === 'edit') {
      confirmEditAnthropometry();
    }
  }}
  title={actionConfirmModal.action === 'add' ? '¿Agregar medición?' : '¿Actualizar medición?'}
  description={
    actionConfirmModal.action === 'add'
      ? `Se agregará la medición: Peso ${actionConfirmModal.data?.ant_peso_kg}kg, Talla ${actionConfirmModal.data?.ant_talla_cm}cm`
      : 'Se actualizará la medición antropométrica.'
  }
  confirmText="Sí, guardar"
  cancelText="Cancelar"
/>
```

---

## 🎯 Resumen de Cambios

Para cada componente:

1. **Importar** `ActionConfirmModal`
2. **Agregar estado** para el modal de confirmación
3. **Modificar handlers** para mostrar modal en vez de ejecutar directamente
4. **Crear funciones** `confirm*` que ejecutan la acción
5. **Agregar JSX** del `ActionConfirmModal` al final del componente

---

## 💡 Tips

- `ActionConfirmModal` es para **confirmar ANTES** de hacer la acción (rojo, con advertencia)
- `ConfirmationModal` es para **mostrar resultado DESPUÉS** de la acción (verde/rojo, éxito/error)
- Usa ambos: primero `ActionConfirmModal`, luego `ConfirmationModal`

---

## 🔧 Ejemplo Completo de Flujo

```typescript
// 1. Usuario hace clic en "Guardar"
const handleSave = () => {
  setActionConfirmModal({ isOpen: true, action: 'save', data: formData });
};

// 2. Usuario confirma en el modal
const confirmSave = async () => {
  setActionConfirmModal({ isOpen: false, action: null });

  const result = await saveData.execute(formData);

  // 3. Mostrar resultado
  if (result) {
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Guardado exitoso',
      message: 'Los datos se guardaron correctamente.'
    });
  } else {
    setConfirmModal({
      isOpen: true,
      type: 'error',
      title: 'Error al guardar',
      message: 'No se pudieron guardar los datos.'
    });
  }
};
```

---

¿Quieres que implemente alguno de estos cambios específicamente? 🚀
