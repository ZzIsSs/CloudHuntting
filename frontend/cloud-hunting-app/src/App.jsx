import { Routes, Route, Navigate } from 'react-router-dom'
import { isAdmin } from './utils/authUtils'
import AuthPage from './pages/AuthPage/AuthPage'
import CloudGamePage from './pages/CloudGamePage/CloudGamePage'
import CarouselPage from './pages/CarouselPage/CarouselPage'
import DetailPage from './pages/DetailPage/DetailPage'
import MapPage from './pages/MapPage/MapPage'
import RankingPage from './pages/RankingPage/RankingPage'
import BookingLayout from './components/Booking/BookingLayout'
import ScheduleLayout from './components/Schedule/ScheduleLayout'
import AdminDashboard from './pages/AdminDashboard/AdminDashboard'
import SupportTickets from './components/Support/SupportTickets'
import ProfilePage from './pages/ProfilePage/ProfilePage'

function ProtectedUserRoute({ children }) {
  if (isAdmin()) {
    return <Navigate to="/admin" replace />;
  }
  return children;
}

function ProtectedAdminRoute({ children }) {
  if (!isAdmin()) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={isAdmin() ? <Navigate to="/admin" replace /> : <AuthPage />} />
      <Route path="/admin" element={<ProtectedAdminRoute><AdminDashboard /></ProtectedAdminRoute>} />
      
      {/* User routes */}
      <Route path="/game" element={<ProtectedUserRoute><CloudGamePage /></ProtectedUserRoute>} />
      <Route path="/results" element={<ProtectedUserRoute><CarouselPage /></ProtectedUserRoute>} />
      <Route path="/detail" element={<ProtectedUserRoute><DetailPage /></ProtectedUserRoute>} />
      <Route path="/map" element={<ProtectedUserRoute><MapPage /></ProtectedUserRoute>} />
      <Route path="/ranking" element={<ProtectedUserRoute><RankingPage /></ProtectedUserRoute>} />
      <Route path="/booking" element={<ProtectedUserRoute><BookingLayout /></ProtectedUserRoute>} />
      <Route path="/schedule" element={<ProtectedUserRoute><ScheduleLayout /></ProtectedUserRoute>} />
      <Route path="/support" element={<ProtectedUserRoute><SupportTickets /></ProtectedUserRoute>} />
      <Route path="/profile" element={<ProtectedUserRoute><ProfilePage /></ProtectedUserRoute>} />
    </Routes>
  )
}

export default App
