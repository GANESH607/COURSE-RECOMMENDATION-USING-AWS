import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { loginUser } from "../services/api"

function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleLogin = async () => {
    const data = await loginUser(email, password)

    if (data.access_token) {
      localStorage.setItem("token", data.access_token)
      navigate("/dashboard")
    } else {
      alert("Invalid credentials")
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-left">
        <h1>AI Course Recommender</h1>
        <p>Discover courses tailored to your skills, goals, and interests using AI.</p>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <h2>Login</h2>

          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={handleLogin}>Login</button>

          <div className="auth-link" onClick={() => navigate("/signup")}>
            Create an account
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login