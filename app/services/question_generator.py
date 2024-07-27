import google.generativeai as genai
import json
from flask import current_app

def generate_questions(topic, num_questions=5):
    genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    
    prompt = f"Generate {num_questions} quiz questions about {topic} in JSON format. Each question should have 'question', 'options' (an array of 4 choices), and 'correct_answer' fields."
    current_app.logger.info(f"Prompt sent to model: {prompt}")
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        current_app.logger.info(f"Response received: {response_text}")

        # Try parsing JSON directly
        try:
            questions = json.loads(response_text)
            current_app.logger.info(f"Parsed questions: {questions}")
        except json.JSONDecodeError:
            # Handle different response format
            if '```json\n' in response_text and '\n```' in response_text:
                try:
                    json_content = response_text.strip().split('```json\n')[1].split('\n```')[0]
                    questions = json.loads(json_content)
                    current_app.logger.info(f"Parsed questions from formatted response: {questions}")
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"Error decoding JSON response from formatted content: {e}")
                    raise
            else:
                current_app.logger.error("Response does not contain valid JSON or the expected format.")
                raise ValueError("Response format is incorrect.")

        return questions
    
    except Exception as e:
        current_app.logger.error(f"Error generating quiz: {e}")
        raise
