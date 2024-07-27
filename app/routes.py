from flask import Blueprint, request, jsonify, current_app, send_file
from app.services import generate_questions, create_quiz_reel
import os

bp = Blueprint('main', __name__)

@bp.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    topic = data.get('topic')
    num_questions = data.get('num_questions', 5)
    
    if not topic:
        return jsonify({'error': 'Missing required parameter: topic'}), 400
    
    try:
        
        
        questions = generate_questions(topic, num_questions)
        output_filename = create_quiz_reel(topic, questions)
        
      
        
        output_folder = os.path.abspath(os.path.join(current_app.config['OUTPUT_FOLDER'], '.'))
        output_path = os.path.join(output_folder, output_filename)
        
        current_app.logger.info(f"Generated quiz file: {output_path}")
        
       
        if not os.path.exists(output_path):
            return jsonify({'error': f'Generated file not found: {output_filename}'}), 500
    
        return send_file(output_path, 
                         mimetype='video/mp4',
                         as_attachment=True,
                         download_name=output_filename)
    except Exception as e:
        current_app.logger.error(f"Error generating quiz: {str(e)}")
        return jsonify({'error': f'Failed to generate quiz: {str(e)}'}), 500

@bp.after_request
def cleanup(response):
   
    if response.status_code == 200 and request.endpoint == 'main.generate_quiz':
        output_filename = os.path.basename(request.path)
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
        if os.path.exists(output_path):
            os.remove(output_path)
    return response