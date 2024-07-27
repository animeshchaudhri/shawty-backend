import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from flask import current_app
from .audio_generator import create_audio
import random
import logging

def create_quiz_reel(topic, questions, think_time=5):
    try:
        # Ensure OUTPUT_FOLDER exists
        os.makedirs(current_app.config['OUTPUT_FOLDER'], exist_ok=True)
        current_app.logger.info(f"Ensured OUTPUT_FOLDER exists: {current_app.config['OUTPUT_FOLDER']}")

        static_folder = current_app.static_folder
        videos_folder = os.path.join(static_folder, 'videos')
        
        # List all video files in the videos folder
        video_files = [f for f in os.listdir(videos_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
        
        if not video_files:
            raise FileNotFoundError("No video files found in the static/videos folder")
        
        # Choose a random video file
        video_filename = random.choice(video_files)
        video_path = os.path.join(videos_folder, video_filename)
        current_app.logger.info(f"Selected background video: {video_path}")
        
        background = VideoFileClip(video_path)
        video_clips = [background]
        audio_clips = []
        
        current_time = 0
        # Load timer sound
        current_app.logger.info(f"Timer sound path: {current_app.config['TIMER_SOUND_PATH']}")
        current_app.logger.info(f"Output folder: {current_app.config['OUTPUT_FOLDER']}")
        timer_sound = AudioFileClip(current_app.config['TIMER_SOUND_PATH']).subclip(0, think_time)

        for i, q in enumerate(questions):
            question_start_time = current_time
            
            # Question
            question_text = f"Question {i+1}: {q['question']}"
            temp_audio_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f"temp_question_{i}.mp3")
            q_audio = create_audio(question_text, temp_audio_path)
            q_duration = q_audio.duration
            
            audio_clips.append(q_audio.set_start(current_time))
            current_time += q_duration
            
            # Options
            option_clips = []
            for j, option in enumerate(q['options']):
                option_text = f"{chr(65+j)}. {option}"
                temp_option_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f"temp_option_{i}_{j}.mp3")
                option_audio = create_audio(option_text, temp_option_path)
                option_duration = option_audio.duration
                
                audio_clips.append(option_audio.set_start(current_time))
                
                option_clip = (TextClip(option_text, fontsize=40, color='yellow', bg_color='rgba(0,0,0,0.8)', 
                                        font='Impact', size=(background.w-20, None), stroke_color='black', stroke_width=2, method='caption')
                               .set_position(('center', 500 + j*80))
                               .set_start(current_time))
                
                option_clips.append(option_clip)
                current_time += option_duration
            
            # Think time
            audio_clips.append(timer_sound.set_start(current_time))
            think_time_end = current_time + think_time
            current_time = think_time_end
            
            # Answer
            answer_text = f"The correct answer is: {q['correct_answer']}"
            temp_answer_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f"temp_answer_{i}.mp3")
            a_audio = create_audio(answer_text, temp_answer_path)
            a_duration = a_audio.duration
            
            audio_clips.append(a_audio.set_start(current_time))
            answer_end_time = current_time + a_duration + 1
            
            # Set durations for question and option clips
            question_total_duration = answer_end_time - question_start_time
            q_txt_clip = (TextClip(question_text, fontsize=50, color='white', bg_color='rgba(0,0,0,0.8)', 
                                   font='Arial-Bold', size=(background.w-20, None), method='caption')
                          .set_position(('center', 50))
                          .set_start(question_start_time)
                          .set_duration(question_total_duration))
            
            video_clips.append(q_txt_clip)

            for option_clip in option_clips:
                option_clip = option_clip.set_duration(think_time_end - option_clip.start)
                video_clips.append(option_clip)
            
            # Answer clip
            a_txt_clip = (TextClip(answer_text, fontsize=50, color='green', bg_color='rgba(0,0,0,0.8)', 
                                   font='Arial-Bold', size=(background.w-20, None), method='caption')
                          .set_position('center')
                          .set_start(current_time)
                          .set_duration(a_duration + 1))
            
            video_clips.append(a_txt_clip)
            
            current_time = answer_end_time
        
        # Ensure the background video is long enough
        if current_time > background.duration:
            video_clips[0] = background.loop(duration=current_time)
        else:
            video_clips[0] = background.subclip(0, current_time)
        
        # Combine video and audio clips
        final_video = CompositeVideoClip(video_clips)
        final_audio = CompositeAudioClip(audio_clips)
        final_clip = final_video.set_audio(final_audio)
        
        # Write output video file
        output_filename = f"{topic.replace(' ', '_')}_quiz_reel.mp4"
        output_path = os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
        
        current_app.logger.info(f"Writing final video to: {output_path}")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=16)
        
        # Clean up temporary audio files
        cleanup_count = 0
        for filename in os.listdir(current_app.config['OUTPUT_FOLDER']):
            if filename.startswith("temp_") and filename.endswith(".mp3"):
                os.remove(os.path.join(current_app.config['OUTPUT_FOLDER'], filename))
                cleanup_count += 1
        current_app.logger.info(f"Cleaned up {cleanup_count} temporary audio files")
        
        current_app.logger.info(f"Successfully created quiz reel: {output_filename}")
        return output_filename

    except FileNotFoundError as e:
        current_app.logger.error(f"File not found error in create_quiz_reel: {str(e)}")
        raise
    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_quiz_reel: {str(e)}")
        raise