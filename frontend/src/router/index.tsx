import { createBrowserRouter } from 'react-router-dom';
import { RoomGuard } from '@/guards/RoomGuard';
import ProtectedRoute from '@/guards/ProtectedRoute';
import { Dashboard } from '@/pages/Dashboard/Dashboard'
import { NotFound } from '@/pages/NotFound/NotFound';
import { LoginPage } from '@/pages/LoginPage/LoginPage';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: '/interview/:roomId',
    element: <RoomGuard />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
