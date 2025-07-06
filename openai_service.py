import json
import os
import base64
import logging
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_face_with_ai(image_path, face_data, language='en'):
    """
    Analyze face using GPT-4o with ancient wisdom systems
    """
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Create comprehensive prompt for face analysis
        prompt = f"""
        As an expert in ancient face reading systems and modern physiognomy, analyze this face using ALL of the following systems and provide a comprehensive report in {language}:

        1. **Chinese Mian Xiang (Face Reading)**:
           - Analyze the 100-year face map zones
           - Examine forehead (early life 15-30), nose (middle age 31-50), chin/jaw (later life 51+)
           - Assess the five features: eyebrows, eyes, nose, mouth, ears
           - Identify wealth, health, and relationship indicators
           - Predict career success and life path

        2. **Greek Physiognomy (Aristotelian)**:
           - Analyze facial geometry and proportions
           - Examine nose shape and what it reveals about temperament
           - Assess eye shape, spacing, and character implications
           - Evaluate jaw strength and determination indicators
           - Identify leadership qualities and intellectual capacity

        3. **Vedic Samudrika Shastra**:
           - Examine facial symmetry and karmic implications
           - Analyze any visible marks, moles, or distinctive features
           - Assess the three doshas reflected in facial features
           - Examine spiritual development indicators
           - Predict relationship compatibility and family life

        4. **Islamic Firasa (Intuitive Reading)**:
           - Read the inner light and spiritual essence
           - Analyze micro-expressions and subtle energy
           - Examine truthfulness and character indicators
           - Assess spiritual development and moral character
           - Identify hidden talents and divine gifts

        5. **Modern FACS/Ekman (Optional Enhancement)**:
           - Analyze habitual facial expressions
           - Identify personality traits from muscle patterns
           - Assess emotional tendencies and stress patterns

        Based on the facial analysis, provide a detailed JSON response with the following structure:
        {{
            "overall_personality": "detailed personality assessment",
            "chinese_analysis": {{
                "forehead_reading": "early life analysis",
                "nose_reading": "middle age predictions",
                "chin_reading": "later life prospects",
                "wealth_indicators": "financial potential",
                "health_predictions": "health insights",
                "life_path": "overall destiny"
            }},
            "greek_analysis": {{
                "temperament": "character assessment",
                "intellectual_capacity": "mental abilities",
                "leadership_qualities": "leadership potential",
                "social_tendencies": "interpersonal traits"
            }},
            "vedic_analysis": {{
                "karmic_indicators": "past life influences",
                "spiritual_development": "soul evolution level",
                "relationship_patterns": "love and family insights",
                "life_purpose": "dharmic path"
            }},
            "islamic_analysis": {{
                "spiritual_essence": "inner light reading",
                "moral_character": "ethical nature",
                "hidden_talents": "divine gifts",
                "truthfulness": "honesty indicators"
            }},
            "modern_analysis": {{
                "emotional_patterns": "habitual emotions",
                "stress_indicators": "stress management",
                "communication_style": "interpersonal communication"
            }},
            "life_predictions": {{
                "career_success": "professional prospects",
                "relationships": "love and partnership",
                "health_longevity": "physical wellbeing",
                "wealth_abundance": "financial future",
                "spiritual_growth": "consciousness evolution"
            }},
            "recommendations": {{
                "strengths_to_develop": "natural talents to enhance",
                "challenges_to_overcome": "areas for improvement",
                "life_advice": "guidance for optimal living",
                "spiritual_practices": "recommended practices"
            }},
            "accuracy_note": "These ancient methods have been validated for thousands of years with 90%+ accuracy for personality and destiny insights."
        }}

        Face detection data provided: {face_data}
        
        Make the analysis detailed, professional, and personally meaningful. Focus on positive insights while being honest about challenges.
        """

        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=4000
        )
        
        analysis_result = json.loads(response.choices[0].message.content)
        return analysis_result
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        return {
            "error": "Analysis failed",
            "message": "Unable to complete face analysis. Please try again."
        }

def translate_text(text, target_language):
    """
    Translate text to target language using GPT-4o
    """
    try:
        language_names = {
            'en': 'English',
            'ro': 'Romanian',
            'de': 'German', 
            'it': 'Italian',
            'fr': 'French',
            'es': 'Spanish',
            'zh': 'Chinese (Mandarin)',
            'ar': 'Arabic',
            'ja': 'Japanese'
        }
        
        target_lang_name = language_names.get(target_language, 'English')
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"Translate the following text to {target_lang_name}. Maintain the meaning and tone accurately."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text  # Return original text if translation fails
