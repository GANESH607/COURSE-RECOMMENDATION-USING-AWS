import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

export default function CourseDetails() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);

  useEffect(() => {
    const fetchCourse = async () => {
      const token = localStorage.getItem("token");

      const res = await fetch(
        `http://127.0.0.1:8000/course-details/${id}`,
        {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        }
      );

      const data = await res.json();
      setCourse(data);
    };

    fetchCourse();
  }, [id]);

  if (!course) return <p>Loading...</p>;

  return (
    <div>
      <h2>{course.course_title}</h2>
      <p>Subject: {course.subject}</p>
      <p>Level: {course.level}</p>
      <p>Duration: {course.content_duration} hours</p>
      <p>Lectures: {course.num_lectures}</p>
      <p>Price: {course.is_paid ? `$${course.price}` : "Free"}</p>

      <a
        href={course.url}
        target="_blank"
        rel="noopener noreferrer"
      >
        <button>Enroll Now</button>
      </a>
    </div>
  );
}