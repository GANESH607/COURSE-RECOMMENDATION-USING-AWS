import { BrowserRouter, Routes, Route } from "react-router-dom"
import Login from "./pages/Login.jsx"
import Signup from "./pages/Signup.jsx"
import Dashboard from "./pages/Dashboard.jsx"
import Interview from "./pages/Interview.jsx"
import ChatPage from "./pages/ChatPage";
import CourseDetails from "./pages/CourseDetails";
import Recommendations from "./pages/Recommendations.jsx"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/interview" element={<Interview />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/course/:id" element={<CourseDetails />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App