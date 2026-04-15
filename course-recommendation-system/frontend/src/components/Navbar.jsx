import { useNavigate } from "react-router-dom"

function Navbar() {
  const navigate = useNavigate()

  return (
    <div className="navbar">
      <h2>AI Course Recommender</h2>
      <button onClick={() => {
        localStorage.removeItem("token")
        navigate("/")
      }}>
        Logout
      </button>
    </div>
  )
}

export default Navbar  