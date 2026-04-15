import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import { getInterviewQuestions, submitInterview } from "../services/api"
import { useNavigate } from "react-router-dom"

function Interview() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchQuestions = async () => {
      const token = localStorage.getItem("token")
      const data = await getInterviewQuestions(token)

      if (data.questions) {
        setMessages([{ type: "ai", text: data.questions }])
      }

      setLoading(false)
    }

    fetchQuestions()
  }, [])

  const handleSend = async () => {
    if (!input.trim()) return

    const updatedMessages = [
      ...messages,
      { type: "user", text: input }
    ]

    setMessages(updatedMessages)
    setInput("")

    const token = localStorage.getItem("token")

    await submitInterview(token, input)

    setMessages([
      ...updatedMessages,
      { type: "ai", text: "Preferences saved! Redirecting to recommendations..." }
    ])

    setTimeout(() => {
      navigate("/recommendations")
    }, 2000)
  }

  return (
    <>
      <Navbar />
      <div className="chat-container">
        <div className="chat-messages">
          {loading && <p>Loading interview...</p>}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.type}`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="chat-input-area">
          <input
            type="text"
            placeholder="Type your answer..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend()
            }}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </>
  )
}

export default Interview