import { useState } from "react";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);

  const askRecommendation = async () => {
    const token = localStorage.getItem("token");

    const res = await fetch(
      `http://127.0.0.1:8000/chat-recommendation?message=${message}`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    const data = await res.json();
    setResponse(data);
  };

  return (
    <div>
      <h2>AI Course Advisor</h2>

      <input
        type="text"
        placeholder="Ask something..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />

      <button onClick={askRecommendation}>
        Ask
      </button>

      {response && (
        <div>
          <h3>{response.recommended_course.course_title}</h3>
          <p>{response.explanation}</p>

          <button onClick={() =>
            window.location.href = `/course/${response.recommended_course.course_id}`
          }>
            View Details
          </button>
        </div>
      )}
    </div>
  );
}