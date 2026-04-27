# Mock Interview API - Testing with cURL

**Base URL:** `http://localhost:5000`

## 1. Create a New Interview

```bash
curl -X POST http://localhost:5000/api/interview/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "John Doe",
    "email": "john@example.com",
    "job_title": "Software Engineer",
    "difficulty": "medium"
  }'
```

**Response Example:**
```json
{
  "status": "success",
  "interview_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_title": "Software Engineer",
  "difficulty": "medium"
}
```

---

## 2. Get Next Question

```bash
curl -X GET http://localhost:5000/api/interview/550e8400-e29b-41d4-a716-446655440000/next-question
```

**Response Example:**
```json
{
  "status": "success",
  "question_id": "q1-uuid",
  "question_number": 1,
  "question_text": "Tell me about your experience with Python..."
}
```

---

## 3. Submit Answer for a Question

```bash
curl -X POST http://localhost:5000/api/interview/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "q1-uuid",
    "answer": "I have 5 years of experience with Python, primarily using Flask and Django for web development..."
  }'
```

**Response Example:**
```json
{
  "status": "success",
  "evaluation": "Score: 78, Evaluation: Good understanding of Python fundamentals..."
}
```

---

## 4. Get All Questions for an Interview

```bash
curl -X GET http://localhost:5000/api/questions/550e8400-e29b-41d4-a716-446655440000
```

**Response Example:**
```json
{
  "status": "success",
  "total_questions": 3,
  "questions": [
    {
      "id": "q1-uuid",
      "question_number": 1,
      "question_text": "Tell me about your experience...",
      "user_answer": "I have 5 years...",
      "score": 78
    }
  ]
}
```

---

## 5. Get Specific Question Details

```bash
curl -X GET http://localhost:5000/api/questions/q1-uuid
```

**Response Example:**
```json
{
  "status": "success",
  "id": "q1-uuid",
  "question_text": "Tell me about your experience...",
  "question_number": 1,
  "user_answer": "I have 5 years...",
  "ai_evaluation": "Score: 78...",
  "score": 78
}
```

---

## 6. End Interview

```bash
curl -X POST http://localhost:5000/api/interview/550e8400-e29b-41d4-a716-446655440000/end
```

**Response Example:**
```json
{
  "status": "success",
  "final_score": 75,
  "interview_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 7. Get Feedback for Completed Interview

```bash
curl -X GET http://localhost:5000/api/feedback/550e8400-e29b-41d4-a716-446655440000
```

**Response Example:**
```json
{
  "status": "success",
  "interview_id": "550e8400-e29b-41d4-a716-446655440000",
  "final_score": 75,
  "overall_feedback": "Strong technical foundation...",
  "strengths": "Problem-solving, communication",
  "areas_for_improvement": "Advanced algorithms, system design"
}
```

---

## Quick Test Workflow

### Step 1: Create Interview
```bash
INTERVIEW_ID=$(curl -s -X POST http://localhost:5000/api/interview/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "name": "Test User",
    "email": "test@example.com",
    "job_title": "Software Engineer",
    "difficulty": "easy"
  }' | jq -r '.interview_id')

echo "Interview ID: $INTERVIEW_ID"
```

### Step 2: Get First Question
```bash
QUESTION=$(curl -s -X GET http://localhost:5000/api/interview/$INTERVIEW_ID/next-question)
QUESTION_ID=$(echo $QUESTION | jq -r '.question_id')

echo "Question ID: $QUESTION_ID"
echo "Question: $(echo $QUESTION | jq -r '.question_text')"
```

### Step 3: Submit Answer
```bash
curl -s -X POST http://localhost:5000/api/interview/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "'$QUESTION_ID'",
    "answer": "I have experience with Python, Django, and REST APIs. I have built several production applications..."
  }' | jq '.'
```

### Step 4: Get More Questions (repeat steps 2-3 for 10 questions total)

### Step 5: End Interview
```bash
curl -s -X POST http://localhost:5000/api/interview/$INTERVIEW_ID/end | jq '.'
```

### Step 6: Get Feedback
```bash
curl -s -X GET http://localhost:5000/api/feedback/$INTERVIEW_ID | jq '.'
```

---

## Notes

- Replace `550e8400-e29b-41d4-a716-446655440000` with actual interview IDs from your responses
- Make sure your `.env` file has `GEMINI_API_KEY` set
- Use `jq` for pretty JSON output (install with: `brew install jq` or `choco install jq`)
- For Windows, use PowerShell with `-UseBasicParsing` flag if needed
