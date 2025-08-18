  // Función para mostrar notificaciones
  const handleShowNotification = (message: string, type: 'success' | 'error') => {
    showNotification({
      message,
      type,
    });
  };
