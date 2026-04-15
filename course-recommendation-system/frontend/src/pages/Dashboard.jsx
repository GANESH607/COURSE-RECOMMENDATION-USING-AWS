import Navbar from "../components/Navbar"
import { useNavigate } from "react-router-dom"

function Dashboard() {
  const navigate = useNavigate()

  return (
    <>
      <Navbar />
      <div className="container">
        <div className="page-title">Dashboard</div>

        <div className="card">
          <h3>Get AI Recommendations</h3>
          <p>See courses tailored specifically for you.</p>
          <button className="primary-btn" onClick={() => navigate("/recommendations")}>
            View Recommendations
          </button>
        </div>

        <div className="card">
          <h3>Improve Your Profile</h3>
          <p>Take the AI interview to refine your recommendations.</p>
          <button className="primary-btn" onClick={() => navigate("/interview")}>
            Take AI Interview
          </button>
        </div>
      </div>
    </>
  )
}

export default Dashboard