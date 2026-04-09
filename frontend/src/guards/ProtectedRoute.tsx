import { type FC } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../shared/auth/AuthContext';

/**
 * ProtectedRoute — оборачивает маршруты, доступные только авторизованным.
 *
 * Если пользователь не авторизован → редирект на /login
 * с сохранением исходного URL в state (для redirect-back после логина).
 *
 * Пока идёт restoreSession — показываем лоадер.
 */
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div style={styles.loader}>
        <div style={styles.spinner} />
        <span style={styles.text}>Загрузка...</span>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
};

const styles = {
  loader: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    background: '#0e0f13',
    gap: 16,
  },
  spinner: {
    width: 32,
    height: 32,
    border: '3px solid #2a2b35',
    borderTopColor: '#5b5eff',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  text: {
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    fontSize: 13,
    color: '#7a7d95',
  },
};

// Inject keyframe via side-effect (simple approach)
if (typeof document !== 'undefined') {
  const styleEl = document.createElement('style');
  styleEl.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
  document.head.appendChild(styleEl);
}

export default ProtectedRoute;
