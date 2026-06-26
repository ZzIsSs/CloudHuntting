import { Routes, Route } from 'react-router-dom'
import AuthPage from './pages/AuthPage/AuthPage'
import CloudGamePage from './pages/CloudGamePage/CloudGamePage'
import CarouselPage from './pages/CarouselPage/CarouselPage'
import DetailPage from './pages/DetailPage/DetailPage'
import MapPage from './pages/MapPage/MapPage'
import RankingPage from './pages/RankingPage/RankingPage'
import BookingLayout from './components/Booking/BookingLayout'
import ScheduleLayout from './components/Schedule/ScheduleLayout'

import SupportTickets from './components/Support/SupportTickets'
import ProfilePage from './pages/ProfilePage/ProfilePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthPage />} />
      <Route path="/game" element={<CloudGamePage />} />
      <Route path="/results" element={<CarouselPage />} />
      <Route path="/detail" element={<DetailPage />} />
      <Route path="/map" element={<MapPage />} />
      <Route path="/ranking" element={<RankingPage />} />
      <Route path="/booking" element={<BookingLayout />} />
      <Route path="/schedule" element={<ScheduleLayout />} />

      <Route path="/support" element={<SupportTickets />} />
      <Route path="/profile" element={<ProfilePage />} />
    </Routes>
  )
}

export default App
