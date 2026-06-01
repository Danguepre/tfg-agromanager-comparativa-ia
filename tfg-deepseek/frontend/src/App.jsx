import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import AdminRoute from './components/AdminRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import MyCrops from './pages/MyCrops';
import Catalog from './pages/Catalog';
import CropDetail from './pages/CropDetail';
import CalendarPage from './pages/Calendar';
import Tasks from './pages/Tasks';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminCrops from './pages/admin/AdminCrops';
import AdminTasks from './pages/admin/AdminTasks';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div style={{ minHeight: '100vh', background: '#f5f7fa' }}>
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
              <Route path="/crops" element={<PrivateRoute><MyCrops /></PrivateRoute>} />
              <Route path="/crops/:id" element={<PrivateRoute><CropDetail /></PrivateRoute>} />
              <Route path="/catalog" element={<PrivateRoute><Catalog /></PrivateRoute>} />
              <Route path="/calendar" element={<PrivateRoute><CalendarPage /></PrivateRoute>} />
              <Route path="/tasks" element={<PrivateRoute><Tasks /></PrivateRoute>} />
              <Route path="/admin/dashboard" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
              <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
              <Route path="/admin/crops" element={<AdminRoute><AdminCrops /></AdminRoute>} />
              <Route path="/admin/tasks" element={<AdminRoute><AdminTasks /></AdminRoute>} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
