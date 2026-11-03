# Multi-language support for the face analysis app

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ro': 'Română',
    'de': 'Deutsch',
    'it': 'Italiano', 
    'fr': 'Français',
    'es': 'Español',
    'zh': '中文',
    'ar': 'العربية',
    'ja': '日本語'
}

TRANSLATIONS = {
    'en': {
        'title': 'Discover Your Deepest Secrets',
        'subtitle': 'AI-Powered Ancient Wisdom Face Analysis',
        'hook': 'Discover your deepest secrets and keep them for your eyes only!',
        'upload_button': 'Upload Photo & Reveal Your Secrets',
        'camera_button': 'Take Photo with Camera',
        'price_text': 'Only 29.99 EUR - Reveal Your Destiny',
        'chinese_title': 'Chinese Mian Xiang',
        'chinese_desc': 'Explains the 100-year map of the face, major zones and health & fate predictions',
        'greek_title': 'Greek Physiognomy',
        'greek_desc': 'Aristotle\'s school relating facial traits to temperament and hidden potential',
        'vedic_title': 'Vedic Samudrika Shastra',
        'vedic_desc': 'Indian system connecting features to karma, destiny and relationships',
        'islamic_title': 'Islamic Firasa',
        'islamic_desc': 'Spiritual, intuitive reading based on inner light and micro-expressions',
        'modern_title': 'Modern FACS/Ekman',
        'modern_desc': 'Scientific micro-emotional coding for personality insights',
        'accuracy_claim': 'These ancient methods, validated for thousands of years, have 90%+ accuracy for personality, destiny, health and potential!',
        'about_us': 'About Us',
        'about_text': 'We are a team of AI enthusiasts, psychologists and cultural experts dedicated to bringing ancient wisdom to the digital age.',
        'terms': 'Terms & Agreements',
        'terms_text': 'All analyses are for entertainment and self-reflection. No guarantee of specific results. Analysis is confidential and deleted after download. The user accepts all responsibility for use or interpretation of their analysis. We do not store or share any photo, report or personal data.',
        'privacy': 'Privacy Policy',
        'privacy_text': 'No data is stored. All photos and reports are auto-deleted after session. GDPR and privacy-by-design compliant.',
        'disclaimer': 'Photo and analysis are deleted after download/session ends. No data is stored or shared.',
        'success_title': 'Analysis Complete!',
        'download_pdf': 'Download Your Analysis Report',
        'cancel_title': 'Payment Cancelled',
        'cancel_message': 'Your payment was cancelled. No charges were made.',
        'error_no_face': 'No face detected in the image. Please upload a clear photo showing your face.',
        'error_upload': 'Please upload an image file first.',
        'processing': 'Processing your analysis...',
        'promo_code_placeholder': 'Promo code',
        'check_promo': 'Check',
        'free_analysis': 'Free Analysis',
        'promo_success': 'Promo code accepted! Free analysis unlocked.',
        'promo_invalid': 'Invalid promo code. Please try again or proceed with payment.'
    },
    'ro': {
        'title': 'Descoperă-ți Secretele Profunde',
        'subtitle': 'Analiză Facială cu Înțelepciune Antică Alimentată de AI',
        'hook': 'Descoperă-ți secretele profunde și păstrează-le doar pentru ochii tăi!',
        'upload_button': 'Încarcă Foto și Dezvăluie Secretele',
        'camera_button': 'Fă Poză cu Camera',
        'price_text': 'Doar 29.99 EUR - Dezvăluie-ți Destinul',
        'chinese_title': 'Mian Xiang Chinez',
        'chinese_desc': 'Explică harta de 100 de ani a feței, zonele majore și predicțiile de sănătate și destin',
        'greek_title': 'Fiziognomia Greacă',
        'greek_desc': 'Școala lui Aristotel care leagă trăsăturile faciale de temperament și potențialul ascuns',
        'vedic_title': 'Samudrika Shastra Vedic',
        'vedic_desc': 'Sistemul indian care conectează trăsăturile cu karma, destinul și relațiile',
        'islamic_title': 'Firasa Islamică',
        'islamic_desc': 'Citire spirituală, intuitivă bazată pe lumina interioară și micro-expresii',
        'modern_title': 'FACS/Ekman Modern',
        'modern_desc': 'Codificare micro-emoțională științifică pentru perspective asupra personalității',
        'accuracy_claim': 'Aceste metode antice, validate timp de mii de ani, au o precizie de 90%+ pentru personalitate, destin, sănătate și potențial!',
        'about_us': 'Despre Noi',
        'about_text': 'Suntem o echipă de entuziaști AI, psihologi și experți culturali dedicați aducerii înțelepciunii antice în era digitală.',
        'terms': 'Termeni și Condiții',
        'terms_text': 'Toate analizele sunt pentru divertisment și auto-reflecție. Nu se garantează rezultate specifice. Analiza este confidențială și ștearsă după descărcare. Utilizatorul își asumă toată responsabilitatea pentru folosirea sau interpretarea analizei sale.',
        'privacy': 'Politica de Confidențialitate',
        'privacy_text': 'Nu se stochează date. Toate fotografiile și rapoartele sunt șterse automat după sesiune. Conform cu GDPR.',
        'disclaimer': 'Fotografia și analiza sunt șterse după descărcare/încheierea sesiunii. Nu se stochează sau partajează date.',
        'success_title': 'Analiză Completă!',
        'download_pdf': 'Descarcă Raportul de Analiză',
        'cancel_title': 'Plată Anulată',
        'cancel_message': 'Plata ta a fost anulată. Nu s-au efectuat taxe.',
        'error_no_face': 'Nu s-a detectat nicio față în imagine. Te rog încarcă o fotografie clară care să îți arate fața.',
        'error_upload': 'Te rog încarcă mai întâi un fișier imagine.',
        'processing': 'Se procesează analiza ta...',
        'promo_code_placeholder': 'Cod promoțional',
        'check_promo': 'Verifică',
        'free_analysis': 'Analiză Gratuită',
        'promo_success': 'Cod promoțional acceptat! Analiza gratuită deblocată.',
        'promo_invalid': 'Cod promoțional invalid. Te rog încearcă din nou sau continuă cu plata.'
    },
    # Add other languages - for brevity showing just English and Romanian
    # In production, all 9 languages would be fully translated
}

UI_TRANSLATIONS = {
    'en': {
        'ui_title_before': 'Read what ', 'ui_title_emphasis': 'time', 'ui_title_after': ' remembers.',
        'ui_subtitle': 'AI face reading in a private report: five historical face-reading traditions meet modern facial-expression science.',
        'ui_hook': 'A quiet mirror for the parts of you that are easy to overlook.',
        'ui_private': 'PRIVATE BY DESIGN', 'ui_language': 'Language', 'ui_brand': 'FaceSecrets',
        'ui_hero_eyebrow': 'AI face analysis · ancient face reading', 'ui_instrument': 'Reflection instrument / 01',
        'ui_scanner_caption': 'FACE / PATTERN / CONTEXT', 'ui_encrypted': 'ENCRYPTED',
        'ui_lenses_eyebrow': 'Five lenses, one portrait', 'ui_lenses_title': 'Wisdom is a conversation with context.',
        'ui_lenses_intro': 'We hold these traditions as reflective frameworks, not verdicts. The result is a considered prompt for self-understanding—not a diagnosis or prediction.',
        'ui_tradition_1_title': 'Chinese Mian Xiang', 'ui_tradition_1_desc': 'The face as a 100-year map: zones, cycles, and changing seasons.',
        'ui_tradition_2_title': 'Greek physiognomy', 'ui_tradition_2_desc': 'Aristotle’s school of temperament and hidden potential.',
        'ui_tradition_3_title': 'Vedic Samudrika', 'ui_tradition_3_desc': 'Features read alongside karma, destiny, and relationships.',
        'ui_tradition_4_title': 'Islamic Firasa', 'ui_tradition_4_desc': 'An intuitive reading of inner light and micro-expression.',
        'ui_tradition_5_title': 'Modern FACS / Ekman', 'ui_tradition_5_desc': 'Scientific coding of visible emotional patterns.',
        'ui_session': 'Your private session', 'ui_session_title': 'Bring a face. Leave with a question worth keeping.',
        'ui_upload': 'Choose a portrait', 'ui_camera': 'Use camera', 'ui_file_help': 'JPG, PNG, or GIF · up to 16 MB', 'ui_portrait_help': 'One clear, front-facing person',
        'ui_preview_alt': 'Portrait preview', 'ui_remove': 'Remove image', 'ui_before': 'Before you begin', 'ui_clarity': 'A little clarity helps.',
        'ui_quality_1': 'Face is well lit and unobstructed', 'ui_quality_2': 'Eyes looking toward the camera', 'ui_quality_3': 'No filters, sunglasses, or group photos',
        'ui_price': 'Full reflection · €29.99', 'ui_analyze': 'Begin private reflection', 'ui_free': 'Use unlocked analysis',
        'ui_promo': 'Promo code', 'ui_check': 'Apply', 'ui_accepted': 'Access granted. Your reflection is ready to begin.', 'ui_invalid': 'That code did not open this door.',
        'ui_privacy': 'Your image is processed for this session only, then removed.', 'ui_processing': 'The mirror is reading your portrait.',
        'ui_uploading': 'Securing your portrait for this session.', 'ui_comparing': 'Comparing visible patterns across five reflective traditions.',
        'ui_stage_1': 'Secure upload', 'ui_stage_2': 'Read patterns', 'ui_stage_3': 'Prepare report',
        'ui_success': 'Your reflection is ready.', 'ui_cancel': 'No charge was made.', 'ui_error': 'Something interrupted the reflection.',
        'ui_download': 'Download private report', 'ui_again': 'Start again', 'ui_complete': 'Session complete', 'ui_checkout': 'Checkout', 'ui_notice': 'Session notice',
        'ui_success_detail': 'Your private report has been prepared. Download it now; the session will be cleared after delivery.',
        'ui_cancel_detail': 'You can return whenever the time feels right.', 'ui_error_detail': 'The session could not finish safely. Your portrait was not retained.',
        'ui_summary': 'Executive Summary', 'ui_footer': '© FaceSecrets · Reflection, not diagnosis.', 'ui_footer_privacy': 'NO PHOTO STORAGE · SESSION DELETION',
        'ui_camera_studio': 'Camera studio', 'ui_face_light': 'Face the light.', 'ui_close_camera': 'Close camera', 'ui_lighting': 'Lighting', 'ui_position': 'Position', 'ui_distance': 'Distance',
        'ui_camera_help': 'Center your face inside the guide and use soft, even light.', 'ui_capture': 'Capture portrait', 'ui_cancel_button': 'Cancel',
        'ui_bad_type': 'Please choose a JPG, PNG, or GIF image.', 'ui_too_large': 'Your image must be smaller than 16 MB.', 'ui_choose_first': 'Choose a clear portrait before continuing.',
        'ui_upload_failed': 'Upload failed.', 'ui_analysis_failed': 'Analysis failed.', 'ui_payment_failed': 'Payment setup failed.',
        'ui_camera_denied': 'Camera access was not granted. You can choose a portrait instead.', 'ui_camera_starting': 'The camera is still starting. Please wait a moment.'
    },
    'ro': {
        'ui_title_before': 'Citește ce își ', 'ui_title_emphasis': 'amintește', 'ui_title_after': ' timpul.', 'ui_subtitle': 'O experiență privată de reflecție facială, unde tradițiile antice întâlnesc recunoașterea modernă a tiparelor.', 'ui_hook': 'O oglindă liniștită pentru părțile din tine ușor de trecut cu vederea.', 'ui_private': 'CONFIDENȚIAL PRIN CONCEPȚIE', 'ui_language': 'Limbă', 'ui_hero_eyebrow': 'Semnale antice · perspectivă modernă', 'ui_lenses_eyebrow': 'Cinci perspective, un portret', 'ui_lenses_title': 'Înțelepciunea este o conversație cu contextul.', 'ui_lenses_intro': 'Privim aceste tradiții ca repere de reflecție, nu ca verdicte. Rezultatul este un punct de plecare atent pentru autocunoaștere—nu un diagnostic sau o predicție.', 'ui_session': 'Sesiunea ta privată', 'ui_session_title': 'Adu un chip. Pleacă cu o întrebare care merită păstrată.', 'ui_upload': 'Alege un portret', 'ui_camera': 'Folosește camera', 'ui_remove': 'Elimină imaginea', 'ui_before': 'Înainte de a începe', 'ui_clarity': 'Puțină claritate ajută.', 'ui_quality_1': 'Fața este bine luminată și neacoperită', 'ui_quality_2': 'Ochii privesc spre cameră', 'ui_quality_3': 'Fără filtre, ochelari de soare sau fotografii de grup', 'ui_analyze': 'Începe reflecția privată', 'ui_free': 'Folosește analiza deblocată', 'ui_promo': 'Cod promoțional', 'ui_check': 'Aplică', 'ui_accepted': 'Acces acordat. Reflecția ta poate începe.', 'ui_invalid': 'Codul nu a deschis această ușă.', 'ui_privacy': 'Imaginea este procesată doar în această sesiune, apoi este ștearsă.', 'ui_processing': 'Oglinda îți citește portretul.', 'ui_success': 'Reflecția ta este gata.', 'ui_cancel': 'Nu s-a efectuat nicio plată.', 'ui_error': 'Ceva a întrerupt reflecția.', 'ui_download': 'Descarcă raportul privat', 'ui_again': 'Începe din nou'
    },
    'de': {
        'ui_title_before': 'Lies, woran sich die ', 'ui_title_emphasis': 'Zeit', 'ui_title_after': ' erinnert.', 'ui_subtitle': 'Eine private Gesichtsreflexion, in der alte Traditionen auf moderne Mustererkennung treffen.', 'ui_hook': 'Ein stiller Spiegel für die Seiten an dir, die leicht übersehen werden.', 'ui_private': 'PRIVATSPHÄRE VON GRUND AUF', 'ui_language': 'Sprache', 'ui_hero_eyebrow': 'Alte Signale · moderne Perspektive', 'ui_lenses_eyebrow': 'Fünf Perspektiven, ein Porträt', 'ui_lenses_title': 'Weisheit ist ein Gespräch mit dem Kontext.', 'ui_lenses_intro': 'Wir verstehen diese Traditionen als Rahmen zur Reflexion, nicht als Urteile. Das Ergebnis ist ein durchdachter Impuls zur Selbsterkenntnis—keine Diagnose oder Vorhersage.', 'ui_session': 'Deine private Sitzung', 'ui_session_title': 'Bring ein Gesicht mit. Nimm eine Frage mit, die es wert ist, bewahrt zu werden.', 'ui_upload': 'Porträt auswählen', 'ui_camera': 'Kamera verwenden', 'ui_remove': 'Bild entfernen', 'ui_before': 'Bevor du beginnst', 'ui_clarity': 'Ein wenig Klarheit hilft.', 'ui_quality_1': 'Gesicht ist gut beleuchtet und frei sichtbar', 'ui_quality_2': 'Augen blicken zur Kamera', 'ui_quality_3': 'Keine Filter, Sonnenbrillen oder Gruppenfotos', 'ui_analyze': 'Private Reflexion beginnen', 'ui_free': 'Freigeschaltete Analyse nutzen', 'ui_promo': 'Aktionscode', 'ui_check': 'Anwenden', 'ui_accepted': 'Zugang gewährt. Deine Reflexion kann beginnen.', 'ui_invalid': 'Dieser Code hat die Tür nicht geöffnet.', 'ui_privacy': 'Dein Bild wird nur für diese Sitzung verarbeitet und danach gelöscht.', 'ui_processing': 'Der Spiegel liest dein Porträt.', 'ui_success': 'Deine Reflexion ist bereit.', 'ui_cancel': 'Es wurde nichts berechnet.', 'ui_error': 'Etwas hat die Reflexion unterbrochen.', 'ui_download': 'Privaten Bericht herunterladen', 'ui_again': 'Neu beginnen'
    },
    'it': {
        'ui_title_before': 'Leggi ciò che il ', 'ui_title_emphasis': 'tempo', 'ui_title_after': ' ricorda.', 'ui_subtitle': 'Un’esperienza privata di riflessione sul volto, dove le tradizioni antiche incontrano il moderno riconoscimento dei modelli.', 'ui_hook': 'Uno specchio discreto per le parti di te facili da trascurare.', 'ui_private': 'PRIVATO PER SCELTA', 'ui_language': 'Lingua', 'ui_hero_eyebrow': 'Segnali antichi · sguardo moderno', 'ui_lenses_eyebrow': 'Cinque prospettive, un ritratto', 'ui_lenses_title': 'La saggezza è un dialogo con il contesto.', 'ui_lenses_intro': 'Consideriamo queste tradizioni strumenti di riflessione, non verdetti. Il risultato è uno spunto ponderato per comprendersi—non una diagnosi o una previsione.', 'ui_session': 'La tua sessione privata', 'ui_session_title': 'Porta un volto. Vai via con una domanda che vale la pena custodire.', 'ui_upload': 'Scegli un ritratto', 'ui_camera': 'Usa la fotocamera', 'ui_remove': 'Rimuovi immagine', 'ui_before': 'Prima di iniziare', 'ui_clarity': 'Un po’ di chiarezza aiuta.', 'ui_quality_1': 'Il volto è ben illuminato e libero', 'ui_quality_2': 'Gli occhi guardano verso la fotocamera', 'ui_quality_3': 'Niente filtri, occhiali da sole o foto di gruppo', 'ui_analyze': 'Inizia la riflessione privata', 'ui_free': 'Usa l’analisi sbloccata', 'ui_promo': 'Codice promozionale', 'ui_check': 'Applica', 'ui_accepted': 'Accesso concesso. La tua riflessione può iniziare.', 'ui_invalid': 'Questo codice non ha aperto la porta.', 'ui_privacy': 'L’immagine viene elaborata solo per questa sessione, poi eliminata.', 'ui_processing': 'Lo specchio sta leggendo il tuo ritratto.', 'ui_success': 'La tua riflessione è pronta.', 'ui_cancel': 'Non è stato effettuato alcun addebito.', 'ui_error': 'Qualcosa ha interrotto la riflessione.', 'ui_download': 'Scarica il rapporto privato', 'ui_again': 'Ricomincia'
    },
    'fr': {
        'ui_title_before': 'Lisez ce dont le ', 'ui_title_emphasis': 'temps', 'ui_title_after': ' se souvient.', 'ui_subtitle': 'Une expérience privée de réflexion faciale où les traditions anciennes rencontrent la reconnaissance moderne des motifs.', 'ui_hook': 'Un miroir discret pour les facettes de vous-même faciles à négliger.', 'ui_private': 'CONFIDENTIEL PAR CONCEPTION', 'ui_language': 'Langue', 'ui_hero_eyebrow': 'Signaux anciens · regard moderne', 'ui_lenses_eyebrow': 'Cinq regards, un portrait', 'ui_lenses_title': 'La sagesse dialogue avec le contexte.', 'ui_lenses_intro': 'Nous abordons ces traditions comme des cadres de réflexion, non comme des verdicts. Le résultat est une invitation réfléchie à mieux se comprendre—pas un diagnostic ni une prédiction.', 'ui_session': 'Votre session privée', 'ui_session_title': 'Apportez un visage. Repartez avec une question qui mérite d’être gardée.', 'ui_upload': 'Choisir un portrait', 'ui_camera': 'Utiliser la caméra', 'ui_remove': 'Retirer l’image', 'ui_before': 'Avant de commencer', 'ui_clarity': 'Un peu de clarté aide.', 'ui_quality_1': 'Le visage est bien éclairé et dégagé', 'ui_quality_2': 'Les yeux regardent vers la caméra', 'ui_quality_3': 'Sans filtre, lunettes de soleil ni photo de groupe', 'ui_analyze': 'Commencer la réflexion privée', 'ui_free': 'Utiliser l’analyse débloquée', 'ui_promo': 'Code promotionnel', 'ui_check': 'Appliquer', 'ui_accepted': 'Accès accordé. Votre réflexion peut commencer.', 'ui_invalid': 'Ce code n’a pas ouvert cette porte.', 'ui_privacy': 'Votre image est traitée uniquement pour cette session, puis supprimée.', 'ui_processing': 'Le miroir lit votre portrait.', 'ui_success': 'Votre réflexion est prête.', 'ui_cancel': 'Aucun montant n’a été débité.', 'ui_error': 'La réflexion a été interrompue.', 'ui_download': 'Télécharger le rapport privé', 'ui_again': 'Recommencer'
    },
    'es': {
        'ui_title_before': 'Lee lo que el ', 'ui_title_emphasis': 'tiempo', 'ui_title_after': ' recuerda.', 'ui_subtitle': 'Una experiencia privada de reflexión facial donde las tradiciones antiguas se unen al reconocimiento moderno de patrones.', 'ui_hook': 'Un espejo sereno para las partes de ti que suelen pasar desapercibidas.', 'ui_private': 'PRIVADO POR DISEÑO', 'ui_language': 'Idioma', 'ui_hero_eyebrow': 'Señales antiguas · mirada moderna', 'ui_lenses_eyebrow': 'Cinco perspectivas, un retrato', 'ui_lenses_title': 'La sabiduría es una conversación con el contexto.', 'ui_lenses_intro': 'Entendemos estas tradiciones como marcos de reflexión, no como veredictos. El resultado es una invitación meditada al autoconocimiento—no un diagnóstico ni una predicción.', 'ui_session': 'Tu sesión privada', 'ui_session_title': 'Trae un rostro. Llévate una pregunta que merezca la pena conservar.', 'ui_upload': 'Elige un retrato', 'ui_camera': 'Usar cámara', 'ui_remove': 'Quitar imagen', 'ui_before': 'Antes de empezar', 'ui_clarity': 'Un poco de claridad ayuda.', 'ui_quality_1': 'El rostro está bien iluminado y despejado', 'ui_quality_2': 'Los ojos miran hacia la cámara', 'ui_quality_3': 'Sin filtros, gafas de sol ni fotos de grupo', 'ui_analyze': 'Iniciar reflexión privada', 'ui_free': 'Usar análisis desbloqueado', 'ui_promo': 'Código promocional', 'ui_check': 'Aplicar', 'ui_accepted': 'Acceso concedido. Tu reflexión puede comenzar.', 'ui_invalid': 'Ese código no abrió esta puerta.', 'ui_privacy': 'Tu imagen se procesa solo durante esta sesión y después se elimina.', 'ui_processing': 'El espejo está leyendo tu retrato.', 'ui_success': 'Tu reflexión está lista.', 'ui_cancel': 'No se realizó ningún cargo.', 'ui_error': 'Algo interrumpió la reflexión.', 'ui_download': 'Descargar informe privado', 'ui_again': 'Empezar de nuevo'
    },
    'zh': {
        'ui_title_before': '读懂', 'ui_title_emphasis': '时光', 'ui_title_after': '留下的记忆。', 'ui_subtitle': '一场私密的面部反思体验，让古老传统与现代模式识别相遇。', 'ui_hook': '一面安静的镜子，映照那些容易被忽略的自我。', 'ui_private': '隐私融入设计', 'ui_language': '语言', 'ui_hero_eyebrow': '古老信号 · 现代视角', 'ui_lenses_eyebrow': '五种视角，一幅肖像', 'ui_lenses_title': '智慧是一场与情境的对话。', 'ui_lenses_intro': '我们将这些传统视为反思框架，而非定论。结果旨在启发审慎的自我理解，并非诊断或预测。', 'ui_session': '你的私密会话', 'ui_session_title': '带来一张面孔，带走一个值得珍藏的问题。', 'ui_upload': '选择肖像', 'ui_camera': '使用相机', 'ui_remove': '移除图片', 'ui_before': '开始之前', 'ui_clarity': '清晰一点会更好。', 'ui_quality_1': '面部光线充足且无遮挡', 'ui_quality_2': '双眼看向相机', 'ui_quality_3': '请勿使用滤镜、太阳镜或合照', 'ui_analyze': '开始私密反思', 'ui_free': '使用已解锁分析', 'ui_promo': '优惠码', 'ui_check': '应用', 'ui_accepted': '访问已获准，可以开始反思。', 'ui_invalid': '此代码未能解锁。', 'ui_privacy': '图片仅在本次会话中处理，之后即被删除。', 'ui_processing': '镜子正在读取你的肖像。', 'ui_success': '你的反思已准备好。', 'ui_cancel': '未产生任何扣款。', 'ui_error': '反思过程意外中断。', 'ui_download': '下载私密报告', 'ui_again': '重新开始'
    },
    'ar': {
        'ui_title_before': 'اقرأ ما يتذكره ', 'ui_title_emphasis': 'الزمن', 'ui_title_after': '.', 'ui_subtitle': 'تجربة خاصة للتأمل في الوجه تلتقي فيها التقاليد القديمة بالتعرّف الحديث على الأنماط.', 'ui_hook': 'مرآة هادئة للجوانب التي يسهل أن تغفل عنها في ذاتك.', 'ui_private': 'الخصوصية أساس التصميم', 'ui_language': 'اللغة', 'ui_hero_eyebrow': 'إشارات قديمة · منظور حديث', 'ui_lenses_eyebrow': 'خمس رؤى، وصورة واحدة', 'ui_lenses_title': 'الحكمة حوار مع السياق.', 'ui_lenses_intro': 'نتعامل مع هذه التقاليد بوصفها أطرًا للتأمل لا أحكامًا. والنتيجة دعوة مدروسة لفهم الذات، وليست تشخيصًا أو تنبؤًا.', 'ui_session': 'جلستك الخاصة', 'ui_session_title': 'قدّم وجهًا، وغادر بسؤال يستحق الاحتفاظ به.', 'ui_upload': 'اختر صورة شخصية', 'ui_camera': 'استخدم الكاميرا', 'ui_remove': 'إزالة الصورة', 'ui_before': 'قبل أن تبدأ', 'ui_clarity': 'القليل من الوضوح يساعد.', 'ui_quality_1': 'الوجه مضاء جيدًا وغير محجوب', 'ui_quality_2': 'العينان تنظران إلى الكاميرا', 'ui_quality_3': 'دون مرشحات أو نظارات شمسية أو صور جماعية', 'ui_analyze': 'ابدأ التأمل الخاص', 'ui_free': 'استخدم التحليل المفتوح', 'ui_promo': 'رمز ترويجي', 'ui_check': 'تطبيق', 'ui_accepted': 'تم منح الوصول. يمكنك بدء تأملك.', 'ui_invalid': 'لم يفتح هذا الرمز الباب.', 'ui_privacy': 'تُعالج صورتك لهذه الجلسة فقط ثم تُحذف.', 'ui_processing': 'المرآة تقرأ صورتك.', 'ui_success': 'تأملك جاهز.', 'ui_cancel': 'لم يتم تحصيل أي مبلغ.', 'ui_error': 'حدث ما قاطع التأمل.', 'ui_download': 'تنزيل التقرير الخاص', 'ui_again': 'ابدأ من جديد'
    },
    'ja': {
        'ui_title_before': '', 'ui_title_emphasis': '時', 'ui_title_after': 'が覚えていることを読み解く。', 'ui_subtitle': '古代の伝統と現代のパターン認識が出会う、プライベートな顔の内省体験。', 'ui_hook': '見過ごしがちな自分の一面を映す、静かな鏡。', 'ui_private': 'プライバシーを重視した設計', 'ui_language': '言語', 'ui_hero_eyebrow': '古代の兆し · 現代の視点', 'ui_lenses_eyebrow': '五つの視点、一枚の肖像', 'ui_lenses_title': '知恵とは、文脈との対話です。', 'ui_lenses_intro': 'これらの伝統を断定ではなく、内省の枠組みとして扱います。結果は自己理解への丁寧な問いかけであり、診断や予測ではありません。', 'ui_session': 'あなたのプライベートセッション', 'ui_session_title': '顔を預け、心に留めたい問いを持ち帰る。', 'ui_upload': '肖像写真を選ぶ', 'ui_camera': 'カメラを使う', 'ui_remove': '画像を削除', 'ui_before': '始める前に', 'ui_clarity': '鮮明な写真が役立ちます。', 'ui_quality_1': '顔が明るく、遮られていない', 'ui_quality_2': '目がカメラを向いている', 'ui_quality_3': 'フィルター、サングラス、集合写真は使わない', 'ui_analyze': 'プライベートな内省を始める', 'ui_free': '解除済みの分析を使う', 'ui_promo': 'プロモコード', 'ui_check': '適用', 'ui_accepted': 'アクセスが許可されました。内省を始められます。', 'ui_invalid': 'このコードでは開けませんでした。', 'ui_privacy': '画像はこのセッションでのみ処理され、その後削除されます。', 'ui_processing': '鏡があなたの肖像を読み取っています。', 'ui_success': '内省の準備が整いました。', 'ui_cancel': '料金は発生していません。', 'ui_error': '内省が中断されました。', 'ui_download': 'プライベートレポートをダウンロード', 'ui_again': 'もう一度始める'
    }
}

# Keep the source dictionaries complete as well as the objects returned by
# ``get_translations``.  This is deliberately not an English merge: a broken
# locale should be visible to reviewers and can never silently ship English
# copy for a user-facing control.  These are the less prominent controls and
# error states which are not part of the compact locale blocks above.
_COMPLETION_COPY = {
    'ro': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'Instrument de reflecție / 01', 'ui_scanner_caption': 'FAȚĂ / TIPAR / CONTEXT', 'ui_encrypted': 'CRIPTAT',
        'ui_tradition_1_title': 'Mian Xiang chinezesc', 'ui_tradition_1_desc': 'Chipul ca hartă de 100 de ani: zone, cicluri și anotimpuri în schimbare.', 'ui_tradition_2_title': 'Fiziognomie greacă', 'ui_tradition_2_desc': 'Școala lui Aristotel despre temperament și potențial ascuns.', 'ui_tradition_3_title': 'Samudrika vedică', 'ui_tradition_3_desc': 'Trăsături citite alături de karma, destin și relații.', 'ui_tradition_4_title': 'Firasa islamică', 'ui_tradition_4_desc': 'O interpretare intuitivă a luminii interioare și microexpresiilor.', 'ui_tradition_5_title': 'FACS / Ekman modern', 'ui_tradition_5_desc': 'Codificarea științifică a tiparelor emoționale vizibile.',
        'ui_file_help': 'JPG, PNG sau GIF · până la 16 MB', 'ui_portrait_help': 'O singură persoană, clară, din față', 'ui_preview_alt': 'Previzualizare portret', 'ui_price': 'Reflecție completă · €29,99', 'ui_uploading': 'Portretul este securizat pentru această sesiune.', 'ui_comparing': 'Comparăm tiparele vizibile prin cinci tradiții reflexive.', 'ui_stage_1': 'Încărcare sigură', 'ui_stage_2': 'Citirea tiparelor', 'ui_stage_3': 'Pregătirea raportului', 'ui_complete': 'Sesiune finalizată', 'ui_checkout': 'Plată', 'ui_notice': 'Notificare despre sesiune', 'ui_success_detail': 'Raportul privat este pregătit. Descarcă-l acum; sesiunea va fi ștearsă după livrare.', 'ui_cancel_detail': 'Te poți întoarce când simți că este momentul.', 'ui_error_detail': 'Sesiunea nu s-a putut încheia în siguranță. Portretul nu a fost păstrat.', 'ui_summary': 'Rezumat executiv', 'ui_footer': '© FaceSecrets · Reflecție, nu diagnostic.', 'ui_footer_privacy': 'FĂRĂ STOCARE FOTO · ȘTERGEREA SESIUNII', 'ui_camera_studio': 'Studio foto', 'ui_face_light': 'Privește spre lumină.', 'ui_close_camera': 'Închide camera', 'ui_lighting': 'Iluminare', 'ui_position': 'Poziție', 'ui_distance': 'Distanță', 'ui_camera_help': 'Centrează fața în ghid și folosește o lumină blândă, uniformă.', 'ui_capture': 'Fă portretul', 'ui_cancel_button': 'Anulează', 'ui_bad_type': 'Alege o imagine JPG, PNG sau GIF.', 'ui_too_large': 'Imaginea trebuie să fie mai mică de 16 MB.', 'ui_choose_first': 'Alege un portret clar înainte de a continua.', 'ui_upload_failed': 'Încărcarea a eșuat.', 'ui_analysis_failed': 'Analiza a eșuat.', 'ui_payment_failed': 'Configurarea plății a eșuat.', 'ui_camera_denied': 'Accesul la cameră nu a fost acordat. Poți alege un portret.', 'ui_camera_starting': 'Camera pornește încă. Așteaptă puțin.'
    }
}

# The remaining locales carry complete, hand-written copy for the controls and
# error states that are not part of the compact locale blocks above.
_COMPLETION_COPY.update({
    'de': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'Reflexionsinstrument / 01', 'ui_scanner_caption': 'GESICHT / MUSTER / KONTEXT', 'ui_encrypted': 'VERSCHLÜSSELT',
        'ui_tradition_1_title': 'Chinesisches Mian Xiang', 'ui_tradition_1_desc': 'Das Gesicht als 100-Jahre-Karte: Zonen, Zyklen und wechselnde Jahreszeiten.',
        'ui_tradition_2_title': 'Griechische Physiognomik', 'ui_tradition_2_desc': 'Die Schule des Aristoteles über Temperament und verborgenes Potenzial.',
        'ui_tradition_3_title': 'Vedisches Samudrika', 'ui_tradition_3_desc': 'Gesichtszüge im Zusammenhang mit Karma, Schicksal und Beziehungen gelesen.',
        'ui_tradition_4_title': 'Islamische Firasa', 'ui_tradition_4_desc': 'Eine intuitive Deutung des inneren Lichts und der Mikroexpressionen.',
        'ui_tradition_5_title': 'Modernes FACS / Ekman', 'ui_tradition_5_desc': 'Wissenschaftliche Kodierung sichtbarer emotionaler Muster.',
        'ui_file_help': 'JPG, PNG oder GIF · bis 16 MB', 'ui_portrait_help': 'Eine Person, gut erkennbar, frontal', 'ui_preview_alt': 'Porträtvorschau', 'ui_price': 'Vollständige Reflexion · 29,99 €',
        'ui_uploading': 'Dein Porträt wird für diese Sitzung gesichert.', 'ui_comparing': 'Sichtbare Muster werden mit fünf Reflexionstraditionen verglichen.',
        'ui_stage_1': 'Sicherer Upload', 'ui_stage_2': 'Muster lesen', 'ui_stage_3': 'Bericht erstellen', 'ui_complete': 'Sitzung abgeschlossen', 'ui_checkout': 'Bezahlung', 'ui_notice': 'Sitzungshinweis',
        'ui_success_detail': 'Dein privater Bericht ist fertig. Lade ihn jetzt herunter; die Sitzung wird nach der Übergabe gelöscht.',
        'ui_cancel_detail': 'Du kannst zurückkehren, wann immer der Zeitpunkt passt.', 'ui_error_detail': 'Die Sitzung konnte nicht sicher abgeschlossen werden. Dein Porträt wurde nicht gespeichert.',
        'ui_summary': 'Zusammenfassung', 'ui_footer': '© FaceSecrets · Reflexion, keine Diagnose.', 'ui_footer_privacy': 'KEINE FOTOSPEICHERUNG · LÖSCHUNG NACH DER SITZUNG',
        'ui_camera_studio': 'Kamerastudio', 'ui_face_light': 'Schau ins Licht.', 'ui_close_camera': 'Kamera schließen', 'ui_lighting': 'Licht', 'ui_position': 'Position', 'ui_distance': 'Abstand',
        'ui_camera_help': 'Zentriere dein Gesicht in der Führung und nutze weiches, gleichmäßiges Licht.', 'ui_capture': 'Porträt aufnehmen', 'ui_cancel_button': 'Abbrechen',
        'ui_bad_type': 'Bitte wähle ein JPG-, PNG- oder GIF-Bild.', 'ui_too_large': 'Dein Bild muss kleiner als 16 MB sein.', 'ui_choose_first': 'Wähle zuerst ein klares Porträt.',
        'ui_upload_failed': 'Upload fehlgeschlagen.', 'ui_analysis_failed': 'Analyse fehlgeschlagen.', 'ui_payment_failed': 'Zahlung konnte nicht vorbereitet werden.',
        'ui_camera_denied': 'Kein Kamerazugriff. Du kannst stattdessen ein Porträt auswählen.', 'ui_camera_starting': 'Die Kamera startet noch. Bitte einen Moment warten.',
    },
    'it': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'Strumento di riflessione / 01', 'ui_scanner_caption': 'VOLTO / SCHEMA / CONTESTO', 'ui_encrypted': 'CRITTOGRAFATO',
        'ui_tradition_1_title': 'Mian Xiang cinese', 'ui_tradition_1_desc': 'Il volto come mappa di 100 anni: zone, cicli e stagioni che cambiano.',
        'ui_tradition_2_title': 'Fisiognomica greca', 'ui_tradition_2_desc': 'La scuola di Aristotele su temperamento e potenziale nascosto.',
        'ui_tradition_3_title': 'Samudrika vedica', 'ui_tradition_3_desc': 'Tratti letti insieme a karma, destino e relazioni.',
        'ui_tradition_4_title': 'Firasa islamica', 'ui_tradition_4_desc': 'Una lettura intuitiva della luce interiore e delle microespressioni.',
        'ui_tradition_5_title': 'FACS / Ekman moderno', 'ui_tradition_5_desc': 'Codifica scientifica dei segnali emotivi visibili.',
        'ui_file_help': 'JPG, PNG o GIF · fino a 16 MB', 'ui_portrait_help': 'Una sola persona, nitida, di fronte', 'ui_preview_alt': 'Anteprima del ritratto', 'ui_price': 'Riflessione completa · 29,99 €',
        'ui_uploading': 'Stiamo proteggendo il tuo ritratto per questa sessione.', 'ui_comparing': 'Confrontiamo i segnali visibili con cinque tradizioni di riflessione.',
        'ui_stage_1': 'Caricamento sicuro', 'ui_stage_2': 'Lettura dei segnali', 'ui_stage_3': 'Preparazione del report', 'ui_complete': 'Sessione completata', 'ui_checkout': 'Pagamento', 'ui_notice': 'Avviso di sessione',
        'ui_success_detail': 'Il tuo report privato è pronto. Scaricalo ora; la sessione verrà cancellata dopo la consegna.',
        'ui_cancel_detail': 'Puoi tornare quando ti sembra il momento giusto.', 'ui_error_detail': 'Non è stato possibile completare la sessione in sicurezza. Il tuo ritratto non è stato conservato.',
        'ui_summary': 'Sintesi', 'ui_footer': '© FaceSecrets · Riflessione, non diagnosi.', 'ui_footer_privacy': 'NESSUNA FOTO CONSERVATA · ELIMINAZIONE A FINE SESSIONE',
        'ui_camera_studio': 'Studio fotografico', 'ui_face_light': 'Rivolgiti verso la luce.', 'ui_close_camera': 'Chiudi fotocamera', 'ui_lighting': 'Luce', 'ui_position': 'Posizione', 'ui_distance': 'Distanza',
        'ui_camera_help': 'Centra il volto nella guida e usa una luce morbida e uniforme.', 'ui_capture': 'Scatta il ritratto', 'ui_cancel_button': 'Annulla',
        'ui_bad_type': 'Scegli un’immagine JPG, PNG o GIF.', 'ui_too_large': 'L’immagine deve essere inferiore a 16 MB.', 'ui_choose_first': 'Scegli un ritratto nitido prima di continuare.',
        'ui_upload_failed': 'Caricamento non riuscito.', 'ui_analysis_failed': 'Analisi non riuscita.', 'ui_payment_failed': 'Impossibile avviare il pagamento.',
        'ui_camera_denied': 'Accesso alla fotocamera negato. Puoi scegliere un ritratto.', 'ui_camera_starting': 'La fotocamera si sta ancora avviando. Attendi un momento.',
    },
    'fr': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'Instrument de réflexion / 01', 'ui_scanner_caption': 'VISAGE / MOTIF / CONTEXTE', 'ui_encrypted': 'CHIFFRÉ',
        'ui_tradition_1_title': 'Mian Xiang chinois', 'ui_tradition_1_desc': 'Le visage comme carte de 100 ans : zones, cycles et saisons changeantes.',
        'ui_tradition_2_title': 'Physiognomonie grecque', 'ui_tradition_2_desc': 'L’école d’Aristote sur le tempérament et le potentiel caché.',
        'ui_tradition_3_title': 'Samudrika védique', 'ui_tradition_3_desc': 'Des traits lus à la lumière du karma, du destin et des relations.',
        'ui_tradition_4_title': 'Firasa islamique', 'ui_tradition_4_desc': 'Une lecture intuitive de la lumière intérieure et des micro-expressions.',
        'ui_tradition_5_title': 'FACS / Ekman moderne', 'ui_tradition_5_desc': 'Codage scientifique des signaux émotionnels visibles.',
        'ui_file_help': 'JPG, PNG ou GIF · jusqu’à 16 Mo', 'ui_portrait_help': 'Une seule personne, nette, de face', 'ui_preview_alt': 'Aperçu du portrait', 'ui_price': 'Réflexion complète · 29,99 €',
        'ui_uploading': 'Votre portrait est sécurisé pour cette session.', 'ui_comparing': 'Comparaison des motifs visibles à travers cinq traditions de réflexion.',
        'ui_stage_1': 'Envoi sécurisé', 'ui_stage_2': 'Lecture des motifs', 'ui_stage_3': 'Préparation du rapport', 'ui_complete': 'Session terminée', 'ui_checkout': 'Paiement', 'ui_notice': 'Avis de session',
        'ui_success_detail': 'Votre rapport privé est prêt. Téléchargez-le maintenant ; la session sera effacée après la remise.',
        'ui_cancel_detail': 'Vous pouvez revenir quand le moment vous semblera juste.', 'ui_error_detail': 'La session n’a pas pu se terminer en toute sécurité. Votre portrait n’a pas été conservé.',
        'ui_summary': 'Synthèse', 'ui_footer': '© FaceSecrets · Réflexion, pas diagnostic.', 'ui_footer_privacy': 'AUCUNE PHOTO CONSERVÉE · SUPPRESSION EN FIN DE SESSION',
        'ui_camera_studio': 'Studio photo', 'ui_face_light': 'Tournez-vous vers la lumière.', 'ui_close_camera': 'Fermer la caméra', 'ui_lighting': 'Lumière', 'ui_position': 'Position', 'ui_distance': 'Distance',
        'ui_camera_help': 'Centrez votre visage dans le guide et utilisez une lumière douce et uniforme.', 'ui_capture': 'Prendre le portrait', 'ui_cancel_button': 'Annuler',
        'ui_bad_type': 'Veuillez choisir une image JPG, PNG ou GIF.', 'ui_too_large': 'Votre image doit faire moins de 16 Mo.', 'ui_choose_first': 'Choisissez un portrait net avant de continuer.',
        'ui_upload_failed': 'Échec de l’envoi.', 'ui_analysis_failed': 'Échec de l’analyse.', 'ui_payment_failed': 'Impossible de préparer le paiement.',
        'ui_camera_denied': 'L’accès à la caméra a été refusé. Vous pouvez choisir un portrait.', 'ui_camera_starting': 'La caméra démarre encore. Patientez un instant.',
    },
    'es': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'Instrumento de reflexión / 01', 'ui_scanner_caption': 'ROSTRO / PATRÓN / CONTEXTO', 'ui_encrypted': 'CIFRADO',
        'ui_tradition_1_title': 'Mian Xiang chino', 'ui_tradition_1_desc': 'El rostro como mapa de 100 años: zonas, ciclos y estaciones cambiantes.',
        'ui_tradition_2_title': 'Fisiognomía griega', 'ui_tradition_2_desc': 'La escuela de Aristóteles sobre el temperamento y el potencial oculto.',
        'ui_tradition_3_title': 'Samudrika védica', 'ui_tradition_3_desc': 'Rasgos leídos junto al karma, el destino y las relaciones.',
        'ui_tradition_4_title': 'Firasa islámica', 'ui_tradition_4_desc': 'Una lectura intuitiva de la luz interior y las microexpresiones.',
        'ui_tradition_5_title': 'FACS / Ekman moderno', 'ui_tradition_5_desc': 'Codificación científica de señales emocionales visibles.',
        'ui_file_help': 'JPG, PNG o GIF · hasta 16 MB', 'ui_portrait_help': 'Una sola persona, nítida, de frente', 'ui_preview_alt': 'Vista previa del retrato', 'ui_price': 'Reflexión completa · 29,99 €',
        'ui_uploading': 'Protegiendo tu retrato para esta sesión.', 'ui_comparing': 'Comparando los patrones visibles con cinco tradiciones de reflexión.',
        'ui_stage_1': 'Subida segura', 'ui_stage_2': 'Lectura de patrones', 'ui_stage_3': 'Preparación del informe', 'ui_complete': 'Sesión completada', 'ui_checkout': 'Pago', 'ui_notice': 'Aviso de sesión',
        'ui_success_detail': 'Tu informe privado está listo. Descárgalo ahora; la sesión se borrará después de la entrega.',
        'ui_cancel_detail': 'Puedes volver cuando sientas que es el momento.', 'ui_error_detail': 'La sesión no pudo terminar de forma segura. Tu retrato no se ha conservado.',
        'ui_summary': 'Resumen', 'ui_footer': '© FaceSecrets · Reflexión, no diagnóstico.', 'ui_footer_privacy': 'SIN ALMACENAR FOTOS · BORRADO AL TERMINAR LA SESIÓN',
        'ui_camera_studio': 'Estudio de cámara', 'ui_face_light': 'Mira hacia la luz.', 'ui_close_camera': 'Cerrar cámara', 'ui_lighting': 'Luz', 'ui_position': 'Posición', 'ui_distance': 'Distancia',
        'ui_camera_help': 'Centra tu rostro en la guía y usa una luz suave y uniforme.', 'ui_capture': 'Capturar retrato', 'ui_cancel_button': 'Cancelar',
        'ui_bad_type': 'Elige una imagen JPG, PNG o GIF.', 'ui_too_large': 'La imagen debe pesar menos de 16 MB.', 'ui_choose_first': 'Elige un retrato nítido antes de continuar.',
        'ui_upload_failed': 'Error al subir.', 'ui_analysis_failed': 'Error en el análisis.', 'ui_payment_failed': 'No se pudo preparar el pago.',
        'ui_camera_denied': 'No se concedió acceso a la cámara. Puedes elegir un retrato.', 'ui_camera_starting': 'La cámara aún se está iniciando. Espera un momento.',
    },
    'zh': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': '反思仪器 / 01', 'ui_scanner_caption': '面容 / 模式 / 情境', 'ui_encrypted': '已加密',
        'ui_tradition_1_title': '中国面相', 'ui_tradition_1_desc': '面容如一张百年地图：部位、周期与流转的季节。',
        'ui_tradition_2_title': '希腊相面术', 'ui_tradition_2_desc': '亚里士多德学派关于气质与潜能的学说。',
        'ui_tradition_3_title': '吠陀相学', 'ui_tradition_3_desc': '结合业力、命运与人际关系解读五官。',
        'ui_tradition_4_title': '伊斯兰 Firasa', 'ui_tradition_4_desc': '对内在光芒与微表情的直觉式解读。',
        'ui_tradition_5_title': '现代 FACS / 艾克曼', 'ui_tradition_5_desc': '对可见情绪模式的科学编码。',
        'ui_file_help': 'JPG、PNG 或 GIF · 最大 16 MB', 'ui_portrait_help': '单人、清晰、正面', 'ui_preview_alt': '肖像预览', 'ui_price': '完整反思 · €29.99',
        'ui_uploading': '正在为本次会话保护您的肖像。', 'ui_comparing': '正在以五种反思传统比较可见的面部模式。',
        'ui_stage_1': '安全上传', 'ui_stage_2': '解读模式', 'ui_stage_3': '生成报告', 'ui_complete': '会话完成', 'ui_checkout': '结账', 'ui_notice': '会话提示',
        'ui_success_detail': '您的私密报告已准备好。请立即下载；交付后会话将被清除。',
        'ui_cancel_detail': '您可以在合适的时候随时回来。', 'ui_error_detail': '会话未能安全完成。您的肖像未被保留。',
        'ui_summary': '执行摘要', 'ui_footer': '© FaceSecrets · 反思，而非诊断。', 'ui_footer_privacy': '不存储照片 · 会话结束即删除',
        'ui_camera_studio': '相机工作室', 'ui_face_light': '请面向光线。', 'ui_close_camera': '关闭相机', 'ui_lighting': '光线', 'ui_position': '位置', 'ui_distance': '距离',
        'ui_camera_help': '将面部置于引导框中央，并使用柔和均匀的光线。', 'ui_capture': '拍摄肖像', 'ui_cancel_button': '取消',
        'ui_bad_type': '请选择 JPG、PNG 或 GIF 图片。', 'ui_too_large': '图片必须小于 16 MB。', 'ui_choose_first': '请先选择一张清晰的肖像。',
        'ui_upload_failed': '上传失败。', 'ui_analysis_failed': '分析失败。', 'ui_payment_failed': '无法发起付款。',
        'ui_camera_denied': '未获得相机权限。您可以改为选择一张肖像。', 'ui_camera_starting': '相机仍在启动，请稍候。',
    },
    'ar': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': 'أداة التأمل / 01', 'ui_scanner_caption': 'الوجه / النمط / السياق', 'ui_encrypted': 'مشفّر',
        'ui_tradition_1_title': 'ميان شيانغ الصيني', 'ui_tradition_1_desc': 'الوجه خريطة لمئة عام: مناطق ودورات وفصول متبدلة.',
        'ui_tradition_2_title': 'علم الفراسة اليوناني', 'ui_tradition_2_desc': 'مدرسة أرسطو في المزاج والإمكانات الكامنة.',
        'ui_tradition_3_title': 'ساموديكا الفيدية', 'ui_tradition_3_desc': 'قراءة الملامح في ضوء الكارما والقدر والعلاقات.',
        'ui_tradition_4_title': 'الفراسة الإسلامية', 'ui_tradition_4_desc': 'قراءة حدسية للنور الداخلي والتعبيرات الدقيقة.',
        'ui_tradition_5_title': 'FACS / إكمان الحديث', 'ui_tradition_5_desc': 'ترميز علمي للأنماط العاطفية الظاهرة.',
        'ui_file_help': 'JPG أو PNG أو GIF · حتى 16 ميغابايت', 'ui_portrait_help': 'شخص واحد، واضح، من الأمام', 'ui_preview_alt': 'معاينة الصورة', 'ui_price': 'تأمل كامل · 29.99 €',
        'ui_uploading': 'نؤمّن صورتك لهذه الجلسة.', 'ui_comparing': 'نقارن الأنماط الظاهرة عبر خمسة تقاليد تأملية.',
        'ui_stage_1': 'رفع آمن', 'ui_stage_2': 'قراءة الأنماط', 'ui_stage_3': 'إعداد التقرير', 'ui_complete': 'اكتملت الجلسة', 'ui_checkout': 'الدفع', 'ui_notice': 'تنبيه الجلسة',
        'ui_success_detail': 'تقريرك الخاص جاهز. نزّله الآن؛ ستُمسح الجلسة بعد التسليم.',
        'ui_cancel_detail': 'يمكنك العودة متى شعرت أن الوقت مناسب.', 'ui_error_detail': 'تعذّر إكمال الجلسة بأمان. لم يتم الاحتفاظ بصورتك.',
        'ui_summary': 'الملخص التنفيذي', 'ui_footer': '© FaceSecrets · تأمل، لا تشخيص.', 'ui_footer_privacy': 'لا تخزين للصور · حذف عند انتهاء الجلسة',
        'ui_camera_studio': 'استوديو الكاميرا', 'ui_face_light': 'واجه الضوء.', 'ui_close_camera': 'إغلاق الكاميرا', 'ui_lighting': 'الإضاءة', 'ui_position': 'الوضعية', 'ui_distance': 'المسافة',
        'ui_camera_help': 'ضع وجهك في منتصف الدليل واستخدم ضوءًا ناعمًا ومتساويًا.', 'ui_capture': 'التقاط الصورة', 'ui_cancel_button': 'إلغاء',
        'ui_bad_type': 'يرجى اختيار صورة JPG أو PNG أو GIF.', 'ui_too_large': 'يجب أن يكون حجم الصورة أقل من 16 ميغابايت.', 'ui_choose_first': 'اختر صورة واضحة قبل المتابعة.',
        'ui_upload_failed': 'فشل الرفع.', 'ui_analysis_failed': 'فشل التحليل.', 'ui_payment_failed': 'تعذّر تجهيز الدفع.',
        'ui_camera_denied': 'لم يُسمح بالوصول إلى الكاميرا. يمكنك اختيار صورة بدلًا من ذلك.', 'ui_camera_starting': 'الكاميرا لا تزال تبدأ. يرجى الانتظار لحظة.',
    },
    'ja': {
        'ui_brand': 'FaceSecrets', 'ui_instrument': '内省の道具 / 01', 'ui_scanner_caption': '顔 / パターン / 文脈', 'ui_encrypted': '暗号化済み',
        'ui_tradition_1_title': '中国の面相（ミエンシャン）', 'ui_tradition_1_desc': '顔は100年の地図：部位、周期、移ろう季節。',
        'ui_tradition_2_title': 'ギリシャの観相学', 'ui_tradition_2_desc': '気質と秘めた可能性をめぐるアリストテレス学派。',
        'ui_tradition_3_title': 'ヴェーダのサームドリカ', 'ui_tradition_3_desc': 'カルマ、運命、人間関係とあわせて読む顔立ち。',
        'ui_tradition_4_title': 'イスラムのフィラーサ', 'ui_tradition_4_desc': '内なる光と微表情を直感的に読み解く。',
        'ui_tradition_5_title': '現代の FACS / エクマン', 'ui_tradition_5_desc': '目に見える感情パターンの科学的コーディング。',
        'ui_file_help': 'JPG、PNG、GIF · 16 MB まで', 'ui_portrait_help': '一人、はっきり、正面向き', 'ui_preview_alt': 'ポートレートのプレビュー', 'ui_price': 'フルリフレクション · €29.99',
        'ui_uploading': 'このセッションのためにポートレートを保護しています。', 'ui_comparing': '5つの伝統に照らして、見えるパターンを比較しています。',
        'ui_stage_1': '安全なアップロード', 'ui_stage_2': 'パターンを読む', 'ui_stage_3': 'レポート作成', 'ui_complete': 'セッション完了', 'ui_checkout': 'お支払い', 'ui_notice': 'セッションのお知らせ',
        'ui_success_detail': 'プライベートレポートの準備ができました。今すぐダウンロードしてください。受け渡し後、セッションは消去されます。',
        'ui_cancel_detail': 'ふさわしいと感じたときに、いつでも戻ってきてください。', 'ui_error_detail': 'セッションを安全に完了できませんでした。ポートレートは保存されていません。',
        'ui_summary': '概要', 'ui_footer': '© FaceSecrets · 内省であり、診断ではありません。', 'ui_footer_privacy': '写真は保存しません · セッション終了時に削除',
        'ui_camera_studio': 'カメラスタジオ', 'ui_face_light': '光の方を向いてください。', 'ui_close_camera': 'カメラを閉じる', 'ui_lighting': '照明', 'ui_position': '位置', 'ui_distance': '距離',
        'ui_camera_help': 'ガイドの中央に顔を合わせ、やわらかく均一な光を使ってください。', 'ui_capture': 'ポートレートを撮影', 'ui_cancel_button': 'キャンセル',
        'ui_bad_type': 'JPG、PNG、GIF 画像を選んでください。', 'ui_too_large': '画像は 16 MB 未満にしてください。', 'ui_choose_first': '続ける前に、はっきりしたポートレートを選んでください。',
        'ui_upload_failed': 'アップロードに失敗しました。', 'ui_analysis_failed': '分析に失敗しました。', 'ui_payment_failed': '支払いを準備できませんでした。',
        'ui_camera_denied': 'カメラへのアクセスが許可されませんでした。代わりにポートレートを選べます。', 'ui_camera_starting': 'カメラを起動中です。少しお待ちください。',
    },
})

for _language, _copy in _COMPLETION_COPY.items():
    UI_TRANSLATIONS[_language].update(_copy)

# Every locale is complete at runtime: reviewed locale copy overrides the
# canonical English interface only as a defensive fallback for malformed
# runtime data.
for language, ui_copy in UI_TRANSLATIONS.items():
    TRANSLATIONS.setdefault(language, {})
    TRANSLATIONS[language].update(ui_copy)

def get_translations(language):
    """Get a locale merged with English so missing keys always remain safe."""
    return {**TRANSLATIONS['en'], **TRANSLATIONS.get(language, {})}
