import google.genai as genai
from google.genai import types
import os
import time
from typing import Optional

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY environment variable not set')
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise Exception(f'Failed to initialize Gemini service: {str(e)}')
            
    def _generate_with_retry(self, prompt: str, model_name: str = "gemini-2.5-flash", max_retries: int = 4) -> str:
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota" in error_str:
                    if attempt < max_retries - 1:

                        continue
                raise e
        
    def generate_question(self, job_title: str, difficulty: str, question_number: int) -> str:

        prompt = f"""Generate a {difficulty} level interview question for a {job_title} position.
        This is question number {question_number} out of 10.
        Only provide the question, no numbering or extra text."""
        
        try:
            return self._generate_with_retry(prompt)
        except Exception as e:
            raise Exception(f'Error generating question: {str(e)}')
    
    def evaluate_answer(self, question: str, user_answer: str, job_title: str) -> dict:

        prompt = f"""You are an expert interviewer evaluating a candidate for a {job_title} position.

Question: {question}

Candidate's Answer: {user_answer}

Please provide:
1. A score from 0-100
2. Brief evaluation (2-3 sentences)
3. Key strengths
4. Areas for improvement

Format your response as JSON with keys: score, evaluation, strengths, improvements"""
        
        try:
            return self._generate_with_retry(prompt)
        except Exception as e:
            raise Exception(f'Error evaluating answer: {str(e)}')
    
    def generate_audio_response(self, text: str) -> Optional[bytes]:

        try:

            prompt = f"Convert this to speech: {text}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None
    
    def generate_overall_feedback(self, job_title: str, all_answers: list, all_scores: list) -> dict:

        answers_text = "\n".join([f"Q{i+1}: {answer}" for i, answer in enumerate(all_answers)])
        scores_text = ", ".join([str(s) for s in all_scores])
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        prompt = f"""You are an expert recruiter. A candidate interviewed for a {job_title} position.

Scores: {scores_text} (Average: {avg_score:.1f}/100)

Answers Summary:
{answers_text}

Provide comprehensive feedback in JSON format with keys:
- overall_feedback (2-3 sentences)
- strengths (3-4 key strengths)
- areas_for_improvement (3-4 areas to work on)
- recommendation (hire/maybe/no)"""
        
        try:
            return self._generate_with_retry(prompt)
        except Exception as e:
            raise Exception(f'Error generating feedback: {str(e)}')

    def analyze_resume_and_start(self, resume_text: str) -> str:

        prompt = f"""You are an expert HR and technical interviewer. You have just been provided with the candidate's resume:
{resume_text}

Your task is to start the interview.
1. Greet the candidate normally and warmly to make them comfortable (e.g., "Hello! Welcome to the interview. How are you doing today?").
2. Do NOT ask any interview questions yet. Just start with the friendly greeting.
3. Do NOT mention the structure, the number of questions, or what type of questions you will ask. Keep your response concise.

Only output what you say to the candidate. Keep the tone conversational and professional. Do NOT give yourself a personal name (just refer to yourself as HR or the hiring team)."""
        try:
            return self._generate_with_retry(prompt)
        except Exception as e:
            raise Exception(f'Error starting resume interview: {str(e)}')

    def continue_interview_chat(self, resume_text: str, conversation_history: list) -> str:

        history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['text']}" for msg in conversation_history])
        num_user_answers = sum(1 for msg in conversation_history if msg.get('role') == 'user')
        
        if num_user_answers >= 8:
            prompt = f"""You are an expert HR and technical interviewer.
Candidate's Resume context:
{resume_text}

Conversation History:
{history_text}

The candidate has just answered the 7th and final question. 
Your task: Briefly acknowledge their answer, thank them for their time, and politely conclude the interview by stating that the hiring team will review their profile and get back to them (revert) soon. Do NOT ask any more questions."""
        else:
            current_question_num = num_user_answers
            prompt = f"""You are an expert HR and technical interviewer conducting an interview.
Candidate's Resume context:
{resume_text}

Conversation History:
{history_text}

You are currently asking Question {current_question_num} out of 7, but do NOT mention the question number or structure to the candidate.
Based on the candidate's last answer, acknowledge it briefly and naturally. Do NOT use the candidate's name.
Then, ask the NEXT question.
- Keep your entire response (acknowledgment + question) very short, maximum 3 to 4 lines.
- Keep the difficulty of the questions VERY EASY and simple. Do NOT go in-depth.
- If this is Question 1, simply ask them to "Tell me about yourself" to start things off.
- For questions 2-4, ask basic, surface-level questions about their projects or the specific technologies they used (e.g., "What technologies did you use for project X?").
- For questions 5-7, switch to simple, easy HR-related questions.
- Only ask ONE very simple question at a time. Do not overwhelm them.
- Maintain a professional, warm, and encouraging HR persona. Do NOT use a personal name for yourself, and do NOT repeat the candidate's name.
- Do not include your internal evaluation in the output, only output what you say to the candidate."""

        try:
            return self._generate_with_retry(prompt)
        except Exception as e:
            raise Exception(f'Error continuing interview: {str(e)}')

    def transcribe_audio(self, audio_file_path: str) -> str:

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with open(audio_file_path, 'rb') as f:
                    audio_bytes = f.read()
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=audio_bytes,
                            mime_type="audio/webm"
                        ),
                        "Please transcribe this audio exactly as spoken. Only output the transcription, nothing else."
                    ]
                )
                return response.text.strip()
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "Quota" in error_str) and attempt < max_retries - 1:
                    time.sleep(2.0)
                    continue
                import traceback
                traceback.print_exc()
                raise Exception(f"Gemini transcription failed: {str(e)}")
