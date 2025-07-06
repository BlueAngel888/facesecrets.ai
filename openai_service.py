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
    Comprehensive face analysis using GPT-4o with advanced life path assessment
    """
    try:
        # Encode image
        base64_image = encode_image(image_path)
        
        # Create comprehensive morphopsychology-based analysis prompt
        if language == 'ro':
            prompt = f"""
Ești un expert în morfopsihologie, inteligență artificială și dezvoltare personală. 
Vei analiza chipul unei persoane pornind de la trăsăturile descrise sau extrase dintr-o imagine și vei oferi un raport complet, profund și transformațional.

Obiectivul tău este ca platforma FaceSecrets.ai să ofere:

1. O analiză a personalității bazată pe următoarele zone ale feței:
   - **Fruntea**: gândire, intelect, relația cu autoritatea
   - **Sprâncenele**: voință, emoționalitate, control
   - **Ochii**: suflet, vitalitate, intuiție, energie
   - **Nasul**: ego, încredere, bani, ambiție
   - **Buzele/Gura**: comunicare, afectivitate, sexualitate
   - **Bărbia și maxilarul**: voință, putere interioară, rezistență
   - **Pomeții**: leadership, expresivitate, deschidere
   - **Urechile**: relația cu sinele, ascultare, moștenirea
   - **Pielea/tenul**: sănătate emoțională, vitalitate
   - **Ridurile/liniile**: experiență, tipare emoționale repetitive
   - **Forma generală a feței**: personalitate de bază (rotundă, pătrată, triunghiulară etc.)
   - **Simetria facială**: echilibru interior, conflicte nerezolvate

2. Integrează aceste zone în interpretare folosind următoarele tehnici tradiționale:
   - 🏛️ **Fiziognomia greacă**: caracter reflectat în trăsături
   - 🐉 **Mian Xiang (China)**: harta vieții pe față (frunte = trecut, mijloc = prezent, bărbie = viitor)
   - 🕌 **Ilm al-Firāsa (Islamic)**: corelații între chip și temperament
   - 🕉️ **Ayurveda indiană**: legătura dintre dosha și forma facială
   - 🧬 **Morfopsihologie modernă**: legături psihologice contemporane

3. Interpretarea fiecărei trăsături prin prisma tradițiilor combinate cu corelări moderne din psihologie și dezvoltare personală.

4. Sfaturi și strategii personalizate pentru evoluția clientului în:
   - relații
   - carieră
   - încredere de sine
   - gestionarea emoțiilor
   - decizii personale

5. Tips & tricks pe termen scurt și lung (stil coaching), exerciții, afirmații sau practici.

Date de analiză facială: {face_data}

RĂSPUNDE OBLIGATORIU în format JSON valid cu următoarea structură:
{{
    "analiza_trasaturi": {{
        "fruntea": "analiza detaliata a frunții",
        "sprancenele": "analiza detaliata a sprancenelor", 
        "ochii": "analiza detaliata a ochilor",
        "nasul": "analiza detaliata a nasului",
        "gura_buzele": "analiza detaliata a gurii si buzelor",
        "barbia_maxilarul": "analiza detaliata a barbiei si maxilarului",
        "pometii": "analiza detaliata a pometilor",
        "urechile": "analiza detaliata a urechilor",
        "pielea_tenul": "analiza detaliata a pielii si tenului",
        "riduri_linii": "analiza detaliata a ridurilor si liniilor",
        "forma_generala": "analiza detaliata a formei generale",
        "simetria": "analiza detaliata a simetriei"
    }},
    "profil_psihologic": "Profil psihologic detaliat in 2-3 paragrafe",
    "recomandari_dezvoltare": {{
        "incredere_identitate": "recomandari pentru incredere si identitate",
        "relatii_comunicare": "recomandari pentru relatii si comunicare",
        "cariera_vocatie": "recomandari pentru cariera si vocatie", 
        "decizii_intuitie": "recomandari pentru decizii si intuitie",
        "sanatate_emotionala": "recomandari pentru sanatate emotionala"
    }},
    "tips_long_term": [
        "primul tip pentru termen lung",
        "al doilea tip cu exercitii",
        "al treilea tip pentru introspecție",
        "al patrulea tip pentru practici zilnice",
        "al cincilea tip pentru transformare"
    ],
    "executive_summary": "Rezumat executiv in 2-3 fraze despre personalitate si dezvoltare"
}}

Fii profund, transformațional și explică într-un limbaj accesibil, dar înspirat. Fii ghidul interior al utilizatorului.
"""
        else:
            prompt = f"""
        As an expert in advanced morphopsychology, physiognomy, and personal development, provide a comprehensive face reading in {language}. 
        
        Perform detailed analysis using scientific and traditional systems:

        **ANALYTICAL FRAMEWORK:**
        
        1. **Advanced Morphopsychology & Physiognomy**:
           - Facial structure analysis (bone density, muscle tone, skin texture)
           - Cranial proportions and brain development indicators
           - Micro-expression patterns and habitual muscle tension
           - Asymmetry analysis for brain hemisphere dominance
           - Aging patterns that reveal life experiences
           
        2. **Traditional Systems (Secular Application)**:
           - Greek Physiognomy: character reflected in features
           - Chinese Mian Xiang: life map on face (forehead = past, middle = present, chin = future)
           - Five Element theory in facial features
           - Islamic Ilm al-Firāsa: temperament correlations
           - Indian Ayurvedic: dosha-face connections
           
        3. **Psychological Profiling**:
           - Big Five personality traits assessment
           - Cognitive processing style indicators
           - Emotional intelligence markers
           - Stress response patterns
           - Social interaction preferences
           
        4. **Life Path & Potential Assessment**:
           - Natural talents and abilities
           - Career aptitudes and professional calling
           - Leadership vs. collaboration tendencies
           - Creative vs. analytical thinking patterns
           - Risk tolerance and decision-making style

        **REQUIRED OUTPUT - Comprehensive JSON Report:**
        {{
            "executive_summary": "3-4 sentence overview of personality and life path",
            
            "personality_core": {{
                "dominant_traits": "Top 5 personality characteristics",
                "cognitive_style": "How this person processes information and makes decisions",
                "emotional_profile": "Emotional patterns, sensitivity, and expression style",
                "social_dynamics": "Interpersonal style and relationship patterns",
                "energy_type": "Natural energy levels and motivation sources"
            }},
            
            "life_path_analysis": {{
                "early_life_patterns": "Childhood and youth development (ages 0-25)",
                "career_prime": "Professional peak and achievements (ages 26-50)", 
                "wisdom_years": "Later life focus and legacy (ages 51+)",
                "major_life_themes": "Recurring patterns and lessons",
                "destiny_indicators": "Natural life direction and purpose"
            }},
            
            "professional_guidance": {{
                "ideal_career_fields": "Top 3-5 career areas with high success potential",
                "work_environment": "Optimal working conditions and team dynamics",
                "leadership_style": "Natural management and influence approach",
                "entrepreneurial_potential": "Business ownership and innovation capability",
                "skill_development_priorities": "Key areas for professional growth"
            }},
            
            "relationship_insights": {{
                "romantic_compatibility": "Partnership style and ideal relationship dynamics",
                "family_dynamics": "Role in family and parenting approach",
                "friendship_patterns": "Social circle preferences and loyalty style",
                "communication_style": "How this person expresses and receives information",
                "conflict_resolution": "Approach to disagreements and problem-solving"
            }},
            
            "health_vitality": {{
                "physical_constitution": "Natural health strengths and vulnerabilities",
                "stress_indicators": "How stress manifests and management strategies",
                "longevity_factors": "Lifestyle choices that support long-term wellbeing",
                "energy_optimization": "Daily rhythms and peak performance times",
                "wellness_recommendations": "Specific health and fitness guidance"
            }},
            
            "wealth_abundance": {{
                "financial_patterns": "Natural relationship with money and resources",
                "wealth_building_approach": "Optimal strategies for financial growth",
                "investment_temperament": "Risk tolerance and investment style",
                "abundance_blocks": "Potential obstacles to financial success",
                "prosperity_timeline": "Expected financial development phases"
            }},
            
            "personal_development": {{
                "natural_strengths": "Inherent talents to leverage and develop",
                "growth_opportunities": "Key areas for personal expansion",
                "life_challenges": "Obstacles that will drive growth and wisdom",
                "learning_style": "Optimal approaches for skill acquisition",
                "transformation_phases": "Expected personal evolution cycles"
            }},
            
            "action_plan": {{
                "immediate_focus": "Next 1-2 years development priorities",
                "medium_term_goals": "3-7 year strategic objectives",
                "long_term_vision": "10+ year life direction and legacy goals",
                "daily_practices": "Specific habits and routines for optimal development",
                "milestone_markers": "How to track progress and success"
            }},
            
            "advanced_insights": {{
                "hidden_potentials": "Underdeveloped talents and capabilities",
                "soul_purpose": "Deeper life mission and contribution to others",
                "evolutionary_path": "Personal growth trajectory and consciousness development",
                "intuitive_gifts": "Natural psychic or empathic abilities",
                "creative_expression": "Artistic and innovative potential"
            }}
        }}

        Face analysis data: {face_data}
        
        Provide deep, actionable insights while maintaining scientific credibility. Focus on empowerment and practical guidance for life optimization.
        Avoid any religious references or spiritual practices tied to specific faiths.
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
        
        response_content = response.choices[0].message.content
        if response_content and isinstance(response_content, str):
            try:
                analysis_result = json.loads(response_content)
            except json.JSONDecodeError as json_error:
                logging.error(f"JSON parsing error: {json_error}")
                logging.error(f"Raw response: {response_content[:500]}...")
                # Create a basic fallback analysis structure
                return {
                    "executive_summary": "Analiza a fost completă dar nu a putut fi formatată corect. Vă rugăm să încercați din nou.",
                    "analiza_trasaturi": {
                        "fruntea": "Analiză indisponibilă din cauza unei erori de formatare",
                        "ochii": "Analiză indisponibilă din cauza unei erori de formatare"
                    },
                    "profil_psihologic": "Profilul psihologic nu a putut fi generat din cauza unei erori tehnice.",
                    "recomandari_dezvoltare": {
                        "incredere_identitate": "Vă rugăm să încercați din nou pentru recomandări personalizate"
                    },
                    "tips_long_term": ["Încercați din nou pentru tips personalizați"],
                    "parsing_error": True
                }
        else:
            raise ValueError("Invalid or empty response from OpenAI")
        return analysis_result
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        return {
            "error": "Analysis failed", 
            "message": f"Unable to complete face analysis: {str(e)}. Please try again."
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
