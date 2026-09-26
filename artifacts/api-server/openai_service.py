import base64
import json
import logging
import os
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)

def get_ai_client():
    """Create a fresh client using configured OpenAI credentials."""
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    if not api_key:
        raise RuntimeError("OpenAI is not enabled for this app")
    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_face_with_ai(image_path, language='en', face_data=None):
    """
    Comprehensive face analysis using GPT-4o with advanced morphopsychology for all languages
    """
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Language-specific instructions
        language_instructions = {
            'ro': {
                'title': 'Ești un expert în morfopsihologie, inteligență artificială și dezvoltare personală.',
                'response_instruction': 'RĂSPUNDE OBLIGATORIU în format JSON valid cu următoarea structură:',
                'closing': 'Fii profund, transformațional și explică într-un limbaj accesibil, dar înspirat.'
            },
            'en': {
                'title': 'You are an expert in morphopsychology, artificial intelligence, and personal development.',
                'response_instruction': 'RESPOND MANDATORY in valid JSON format with the following structure:',
                'closing': 'Be profound, transformational and explain in accessible but inspired language.'
            },
            'de': {
                'title': 'Sie sind ein Experte für Morphopsychologie, künstliche Intelligenz und Persönlichkeitsentwicklung.',
                'response_instruction': 'ANTWORTEN Sie OBLIGATORISCH im gültigen JSON-Format mit folgender Struktur:',
                'closing': 'Seien Sie tiefgreifend, transformativ und erklären Sie in zugänglicher, aber inspirierender Sprache.'
            },
            'it': {
                'title': 'Sei un esperto in morfopsicologia, intelligenza artificiale e sviluppo personale.',
                'response_instruction': 'RISPONDI OBBLIGATORIAMENTE in formato JSON valido con la seguente struttura:',
                'closing': 'Sii profondo, trasformativo e spiega in un linguaggio accessibile ma ispirato.'
            },
            'fr': {
                'title': 'Vous êtes un expert en morphopsychologie, intelligence artificielle et développement personnel.',
                'response_instruction': 'RÉPONDEZ OBLIGATOIREMENT en format JSON valide avec la structure suivante:',
                'closing': 'Soyez profond, transformationnel et expliquez dans un langage accessible mais inspiré.'
            },
            'es': {
                'title': 'Eres un experto en morfopsicología, inteligencia artificial y desarrollo personal.',
                'response_instruction': 'RESPONDE OBLIGATORIAMENTE en formato JSON válido con la siguiente estructura:',
                'closing': 'Sé profundo, transformacional y explica en un lenguaje accesible pero inspirado.'
            },
            'zh': {
                'title': '您是形态心理学、人工智能和个人发展方面的专家。',
                'response_instruction': '必须以有效的JSON格式回答，结构如下：',
                'closing': '要深刻、具有转化性，用通俗易懂但富有启发性的语言进行解释。'
            },
            'ar': {
                'title': 'أنت خبير في علم نفس الأشكال والذكاء الاصطناعي والتطوير الشخصي.',
                'response_instruction': 'أجب إجبارياً بصيغة JSON صحيحة مع الهيكل التالي:',
                'closing': 'كن عميقاً وتحويلياً واشرح بلغة سهلة الوصول ولكن ملهمة.'
            },
            'ja': {
                'title': 'あなたは形態心理学、人工知能、個人的発達の専門家です。',
                'response_instruction': '以下の構造で有効なJSON形式で必ず回答してください：',
                'closing': '深く、変革的で、アクセスしやすいが刺激的な言語で説明してください。'
            }
        }
        
        lang_config = language_instructions.get(language, language_instructions['en'])
        
        prompt = f"""
{lang_config['title']}

Analyze only what is visibly observable in this face photograph. Do not infer personality,
intelligence, morality, mental health, sexuality, wealth, destiny, ethnicity, medical conditions,
or other sensitive traits from appearance. Separate observations from cultural interpretation.
Traditional systems are non-scientific cultural frameworks and must be phrased as possibilities
for reflection, never facts or predictions.

Use these facial analysis zones:
- **Forehead**: thinking, intellect, relationship with authority
- **Eyebrows**: will, emotionality, control
- **Eyes**: soul, vitality, intuition, energy
- **Nose**: ego, confidence, money, ambition
- **Lips/Mouth**: communication, affectivity, sexuality
- **Chin & Jaw**: will, inner power, resistance
- **Cheekbones**: leadership, expressiveness, openness
- **Ears**: self-relationship, listening, heritage
- **Skin/Complexion**: emotional health, vitality
- **Wrinkles/Lines**: experience, repetitive emotional patterns
- **General Face Shape**: basic personality
- **Facial Symmetry**: inner balance, unresolved conflicts

Integrate traditional techniques:
- Greek Physiognomy: character reflected in features
- Chinese Mian Xiang: life map on face
- Islamic Ilm al-Firāsa: face-temperament correlations
- Indian Ayurveda: dosha-face connections
- Modern Morphopsychology: contemporary psychological connections

Image preflight measurements: {json.dumps(face_data or {})}
Describe image quality and uncertainty. If a feature is obscured, say so rather than guessing.

{lang_config['response_instruction']}
{{
    "image_quality": {{
        "overall": "excellent/good/limited",
        "lighting": "observable lighting and impact",
        "pose": "pose and impact",
        "occlusions": "hair, glasses, crop, or none",
        "confidence": "high/medium/low",
        "limitations": ["specific limitation"]
    }},
    "analiza_trasaturi": {{
        "fruntea": "detailed forehead analysis",
        "sprancenele": "detailed eyebrow analysis", 
        "ochii": "detailed eye analysis",
        "nasul": "detailed nose analysis",
        "gura_buzele": "detailed mouth and lips analysis",
        "barbia_maxilarul": "detailed chin and jaw analysis",
        "pometii": "detailed cheekbone analysis",
        "urechile": "detailed ear analysis",
        "pielea_tenul": "detailed skin and complexion analysis",
        "riduri_linii": "detailed wrinkles and lines analysis",
        "forma_generala": "detailed general shape analysis",
        "simetria": "detailed symmetry analysis"
    }},
    "traditional_perspectives": {{
        "mian_xiang": "carefully qualified cultural interpretation",
        "greek_physiognomy": "carefully qualified historical interpretation",
        "ayurveda": "carefully qualified traditional interpretation",
        "ilm_al_firasa": "carefully qualified historical interpretation",
        "morphopsychology": "carefully qualified non-scientific interpretation"
    }},
    "profil_psihologic": "State that psychology cannot be reliably determined from a face, then offer neutral self-reflection questions inspired by visible expression only",
    "recomandari_dezvoltare": {{
        "incredere_identitate": "recommendations for confidence and identity",
        "relatii_comunicare": "recommendations for relationships and communication",
        "cariera_vocatie": "recommendations for career and vocation", 
        "decizii_intuitie": "recommendations for decisions and intuition",
        "sanatate_emotionala": "recommendations for emotional health"
    }},
    "tips_long_term": [
        "first long-term tip",
        "second tip with exercises",
        "third tip for introspection",
        "fourth tip for daily practices",
        "fifth tip for transformation"
    ],
    "executive_summary": "2-3 sentence summary of visible features, image confidence, and scope",
    "disclaimer": "Clear statement that this is not identity, medical, psychological, or predictive assessment"
}}

{lang_config['closing']}
"""
        
        # Make API call
        logging.info("Making OpenAI vision request")
        response = get_ai_client().chat.completions.create(
            model=os.environ.get("REPLIT_AI_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4o")),
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
            max_completion_tokens=6000
        )
        
        logging.info(f"OpenAI API response received. Choices: {len(response.choices)}")
        
        # Debug: Log the full response structure
        choice = response.choices[0]
        logging.info(f"Choice finish_reason: {choice.finish_reason}")
        logging.info(f"Message role: {choice.message.role}")
        
        response_content = choice.message.content
        logging.info(f"Response content type: {type(response_content)}, Length: {len(response_content) if response_content else 0}")
        
        # Check if content is None or empty
        if not response_content:
            error_msg = f"OpenAI returned empty content. Finish reason: {choice.finish_reason}"
            logging.error(error_msg)
            # Check if there's a refusal
            if hasattr(choice.message, 'refusal') and choice.message.refusal:
                error_msg = f"OpenAI refused: {choice.message.refusal}"
                logging.error(error_msg)
            raise ValueError(error_msg)
        
        if isinstance(response_content, str):
            try:
                analysis_result = json.loads(response_content)
            except json.JSONDecodeError as json_error:
                logging.error(f"JSON parsing error: {json_error}")
                logging.error(f"Raw response: {response_content[:500]}...")
                raise ValueError("The analysis response was not valid JSON")
        else:
            raise ValueError("Invalid or empty response from OpenAI")
        return analysis_result
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        error_text = str(e).lower()
        if "insufficient_quota" in error_text or "credit_balance_exhausted" in error_text or "no credits remaining" in error_text:
            message = "The AI analysis service has no OpenAI credits remaining. Please try again after billing is restored."
        elif "rate_limit" in error_text or "too many requests" in error_text:
            message = "The AI analysis service is busy. Please wait a moment and try again."
        else:
            message = "The analysis service is temporarily unavailable. Your photo has been deleted; please try again later."
        return {
            "error": "Analysis failed",
            "message": message
        }

def translate_text(text, target_language):
    """
    Translate text to target language using GPT-4o
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Translation text is required")
    if len(text) > 4000:
        raise ValueError("Translation text is too long")

    try:
        language_names = {
            'en': 'English',
            'ro': 'Romanian',
            'de': 'German', 
            'it': 'Italian',
            'fr': 'French',
            'es': 'Spanish',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'ja': 'Japanese'
        }
        
        target_name = language_names.get(target_language, 'English')
        
        response = get_ai_client().chat.completions.create(
            model=os.environ.get("REPLIT_AI_TRANSLATION_MODEL", "gpt-5.4-mini"),
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text to {target_name}. Maintain the tone and meaning while adapting to cultural context."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_completion_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text  # Return original text if translation fails