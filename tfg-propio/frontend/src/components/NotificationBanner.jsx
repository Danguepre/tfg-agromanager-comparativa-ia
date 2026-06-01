import { useMemo } from 'react';

const NotificationBanner = ({ events }) => {
  const currentTasks = useMemo(() => {
    const now = new Date();
    const currentMonth = now.getMonth() + 1; // getMonth() es 0-based
    const currentDay = now.getDate();
    const currentHalf = currentDay <= 15 ? 1 : 2;

    return events.filter(
      (event) => event.month === currentMonth && event.half === currentHalf
    );
  }, [events]);

  if (currentTasks.length === 0) {
    return null;
  }

  const taskTitles = currentTasks.map((task) => task.title).join(', ');

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        backgroundColor: '#d4edda', // Verde claro para alerta
        border: '1px solid #c3e6cb',
        borderRadius: '8px',
        padding: '12px 16px',
        margin: '10px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      <span style={{ fontSize: '20px', marginRight: '8px' }}>⚠️</span>
      <div>
        <strong>Tienes {currentTasks.length} tarea{currentTasks.length > 1 ? 's' : ''} en esta quincena:</strong> {taskTitles}
      </div>
    </div>
  );
};

export default NotificationBanner;
