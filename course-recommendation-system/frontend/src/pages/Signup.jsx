import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { signupUser } from "../services/api"

function Signup() {
  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleSignup = async () => {
    const data = await signupUser({
      full_name: fullName,
      email,
      password
    })

    if (data.user_id) {
      alert("Account created successfully!")
      navigate("/")
    } else {
      alert("Signup failed")
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-left">
        <h1>Start Your Learning Journey</h1>
        <p>Join our AI-powered learning platform today.</p>
      </div>

      <div className="auth-right">
        <div className="auth-card">
          <h2>Create Account</h2>

          <input
            type="text"
            placeholder="Full Name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

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

          <button onClick={handleSignup}>Signup</button>

          <div className="auth-link" onClick={() => navigate("/")}>
            Already have an account?
          </div>
        </div>
      </div>
    </div>
  )
}

export default Signup