const BASE_URL = "http://127.0.0.1:8000"

export async function loginUser(username, password) {
  const formData = new URLSearchParams()
  formData.append("username", username)
  formData.append("password", password)

  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  })

  return response.json()
}

export async function signupUser(data) {
  const response = await fetch(`${BASE_URL}/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  })

  return response.json()
}

export async function getRecommendations(token) {
  const response = await fetch(`${BASE_URL}/recommendations`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })

  return response.json()
}

export async function getInterviewQuestions(token) {
  const response = await fetch("http://127.0.0.1:8000/cold-start-questions", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
  return response.json()
}

export async function submitInterview(token, answers) {
  const response = await fetch(
    `http://127.0.0.1:8000/submit-interview?answers=${encodeURIComponent(answers)}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  )
  return response.json()
}

export async function rateCourse(token, courseId, rating) {
  const response = await fetch(
    `http://127.0.0.1:8000/rate-course?course_id=${courseId}&rating=${rating}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  )
  return response.json()
}
