import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"
import { getRecommendations } from "../services/api"
import { rateCourse } from "../services/api"

function Recommendations() {
  const [data, setData] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("token")
      const result = await getRecommendations(token)
      setData(result)
    }
    fetchData()
  }, [])

  return (
    <>
      <Navbar />
      <div className="container">
        <h1>Your Recommended Courses</h1>

        <div className="grid">
                {data?.recommendations?.map((course, index) => (
        <div key={index} className="card">
        <h3>{course.course_title}</h3>
        <p><strong>Subject:</strong> {course.subject}</p>
        <p><strong>Level:</strong> {course.level}</p>

        {course.explanation && (
            <p style={{marginTop:"10px", fontStyle:"italic"}}>
            {course.explanation}
            </p>
        )}
        <button onClick={() => navigate("/chat")}>
          Ask AI Advisor
        </button>

        <div style={{marginTop:"15px"}}>
            <strong>Rate this course:</strong>
            <div style={{marginTop:"8px"}}>
            {[1,2,3,4,5].map((star) => (
                <span
                key={star}
                style={{
                    cursor: "pointer",
                    fontSize: "20px",
                    marginRight: "8px"
                }}
                onClick={async () => {
                    const token = localStorage.getItem("token")
                    await rateCourse(token, course.course_id, star)
                    alert("Rating submitted!")
                }}
                >
                ⭐
                </span>
            ))}
            </div>
        </div>
        </div>
          ))}
        </div>
      </div>
    </>
  )
}

export default Recommendations