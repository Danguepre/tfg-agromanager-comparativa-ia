import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useContext, useState, useEffect } from "react";
import { AuthContext } from "./context/auth-context";
import Navbar from "./components/Navbar";
import NotificationBanner from "./components/NotificationBanner";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import OAuthCallback from "./pages/OAuthCallback";
import Crops from "./pages/Crops";
import PublishedCrops from "./pages/PublishedCrops";
import Tasks from "./pages/Tasks";
import Home from "./pages/Home";
import Calendar from "./pages/Calendar";
import Admin from "./pages/Admin";
import Dashboard from "./pages/Dashboard";
import { getMyCalendarEvents } from "./api/api";
import { parseJwt } from "./utils/auth";

function ProtectedRoute({ children }) {
  const { token } = useContext(AuthContext);
  return token ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }) {
  const { token } = useContext(AuthContext);
  const currentUser = parseJwt(token || "");

  if (!token) return <Navigate to="/login" replace />;
  return currentUser?.role === "admin" ? children : <Navigate to="/dashboard" replace />;
}


function RouteWrapper() {
  const { token, login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (token) {
      const loadEvents = async () => {
        try {
          const data = await getMyCalendarEvents(token);
          setEvents(Array.isArray(data) ? data : []);
        } catch {
          setEvents([]);
        }
      };
      loadEvents();
    }
  }, [token]);

  return (
    <>
      {token && <Navbar />}
      {token && <NotificationBanner events={events} />}
      <Routes>
        <Route path="/oauth/callback" element={<OAuthCallback onLogin={login} />} />
        <Route
          path="/login"
          element={
            token ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <Login onLogin={(token) => {
                login(token);
                navigate("/dashboard", { replace: true });
              }} onSwitch={() => navigate("/signup")} />
            )
          }
        />
        <Route
          path="/signup"
          element={
            token ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <SignUp onLogin={(token) => {
                login(token);
                navigate("/dashboard", { replace: true });
              }} onSwitch={() => navigate("/login")} />
            )
          }
        />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard token={token} /></ProtectedRoute>} />
        <Route path="/crops" element={<ProtectedRoute><Crops token={token} /></ProtectedRoute>} />
        <Route path="/published-crops" element={<ProtectedRoute><PublishedCrops token={token} /></ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute><Tasks token={token} /></ProtectedRoute>} />
        <Route path="/calendar" element={<ProtectedRoute><Calendar /></ProtectedRoute>} />
        <Route path="/admin" element={<AdminRoute><Admin token={token} /></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><Admin token={token} /></AdminRoute>} />
        <Route path="/admin/crops" element={<AdminRoute><Admin token={token} /></AdminRoute>} />
        <Route path="/" element={token ? <Navigate to="/dashboard" replace /> : <Home />} />
        <Route path="*" element={<Navigate to={token ? "/dashboard" : "/"} replace />} />
      </Routes>
    </>
  );
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <RouteWrapper />
    </BrowserRouter>
  );
}
