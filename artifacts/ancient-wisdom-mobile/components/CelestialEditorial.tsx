import React, { useEffect, useRef, useState } from 'react';
import { AccessibilityInfo, Animated, Image, Platform, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Feather } from '@expo/vector-icons';
import colors from '@/constants/colors';

const c = colors.light;
const hooks: Record<string, { line: string; sub: string }> = {
  en: { line: 'Your face holds a story. Explore it through five traditions.', sub: 'A portrait, a new perspective. Made for curiosity, not certainty.' },
  ro: { line: 'Chipul tău spune o poveste. Descoper-o prin cinci tradiții.', sub: 'Un portret, o nouă perspectivă. Pentru curiozitate, nu certitudini.' },
  de: { line: 'Dein Gesicht erzählt eine Geschichte. Entdecke fünf Traditionen.', sub: 'Ein Porträt, ein neuer Blick. Für Neugier, nicht Gewissheit.' },
  it: { line: 'Il tuo viso racconta una storia. Esplora cinque tradizioni.', sub: 'Un ritratto, una nuova prospettiva. Curiosità, non certezza.' },
  fr: { line: 'Votre visage raconte une histoire. Explorez cinq traditions.', sub: 'Un portrait, un autre regard. Pour la curiosité, pas la certitude.' },
  es: { line: 'Tu rostro cuenta una historia. Explora cinco tradiciones.', sub: 'Un retrato, otra perspectiva. Curiosidad, no certezas.' },
  zh: { line: '你的面容有故事。透过五种传统，换个角度看自己。', sub: '一张肖像，一种新视角。为好奇，而非定论。' },
  ar: { line: 'لوجهك حكاية. تأملها عبر خمس تقاليد.', sub: 'صورة ومنظور جديد. للفضول، لا لليقين.' },
  ja: { line: '顔には物語がある。五つの伝統から見つめ直そう。', sub: '一枚の肖像から、新しい視点へ。断定ではなく好奇心のために。' },
};

type EditorialCopy = {
  caption: string; portraitAlt: string; heroKicker: string;
  framework: string; traditionsTitle: string; traditionsIntro: string; disclaimer: string;
  origins: string[]; descriptions: string[];
  examplesKicker: string; examplesTitle: string; disclosure: string;
  carouselLabel: string; previous: string; next: string; showPage: string;
};
const editorial: Record<string, EditorialCopy> = {
  en: {
    caption: 'THE ART OF SEEING DIFFERENTLY', portraitAlt: 'Editorial portrait of an adult blonde woman against a celestial background', heroKicker: 'A PORTRAIT IN FIVE PERSPECTIVES',
    framework: 'THE FRAMEWORK / 05 LENSES', traditionsTitle: 'Five ways of seeing.', traditionsIntro: 'Your report draws on these actual historical and cultural traditions as prompts for reflection.',
    disclaimer: 'Historical and cultural interpretations, not scientific methods. A face cannot establish personality, health, or destiny. This report is for entertainment and self-reflection only.',
    origins: ['CHINA', 'ANCIENT GREECE', 'SOUTH ASIA', 'ARABIC TRADITIONS', '20TH-CENTURY EUROPE'],
    descriptions: ['A historical practice of reading facial features in Chinese cultural traditions.', 'Classical writings that linked outward appearance with character.', 'A traditional system with ideas about constitution and outward features.', 'A historical tradition of interpreting appearance and perception.', 'A later interpretive framework connecting facial form and temperament.'],
    examplesKicker: 'IMAGINE THE EXPERIENCE', examplesTitle: 'A moment to look closer.', disclosure: 'FICTIONAL ILLUSTRATIVE EXAMPLES — NOT REAL CUSTOMER TESTIMONIALS',
    carouselLabel: 'Illustrative examples, swipe horizontally for more', previous: 'Previous examples', next: 'Next examples', showPage: 'Show examples page',
  },
  ro: {
    caption: 'ARTA DE A PRIVI ALTFEL', portraitAlt: 'Portret editorial al unei femei adulte blonde, pe un fundal celest', heroKicker: 'UN PORTRET ÎN CINCI PERSPECTIVE',
    framework: 'CADRUL / 05 PERSPECTIVE', traditionsTitle: 'Cinci feluri de a privi.', traditionsIntro: 'Raportul folosește aceste tradiții istorice și culturale reale ca puncte de plecare pentru reflecție.',
    disclaimer: 'Interpretări istorice și culturale, nu metode științifice. Chipul nu poate stabili personalitatea, sănătatea sau destinul. Raportul este doar pentru divertisment și reflecție personală.',
    origins: ['CHINA', 'GRECIA ANTICĂ', 'ASIA DE SUD', 'TRADIȚII ARABE', 'EUROPA SECOLULUI XX'],
    descriptions: ['O practică istorică de interpretare a trăsăturilor feței în cultura chineză.', 'Scrieri clasice care asociau aspectul exterior cu caracterul.', 'Un sistem tradițional cu idei despre constituție și trăsături exterioare.', 'O tradiție istorică de interpretare a înfățișării și percepției.', 'Un cadru interpretativ ulterior care lega forma feței de temperament.'],
    examplesKicker: 'IMAGINEAZĂ-ȚI EXPERIENȚA', examplesTitle: 'Un moment să privești mai atent.', disclosure: 'EXEMPLE FICTIVE ILUSTRATIVE — NU SUNT MĂRTURII ALE UNOR CLIENȚI REALI',
    carouselLabel: 'Exemple ilustrative; glisează orizontal pentru mai multe', previous: 'Exemplele anterioare', next: 'Exemplele următoare', showPage: 'Arată pagina de exemple',
  },
  de: {
    caption: 'DIE KUNST, ANDERS ZU SEHEN', portraitAlt: 'Redaktionelles Porträt einer erwachsenen blonden Frau vor einem Sternenhintergrund', heroKicker: 'EIN PORTRÄT AUS FÜNF PERSPEKTIVEN',
    framework: 'DER RAHMEN / 05 SICHTWEISEN', traditionsTitle: 'Fünf Arten zu sehen.', traditionsIntro: 'Dein Bericht nutzt diese tatsächlichen historischen und kulturellen Traditionen als Anregung zur Reflexion.',
    disclaimer: 'Historische und kulturelle Deutungen, keine wissenschaftlichen Methoden. Ein Gesicht verrät weder Persönlichkeit noch Gesundheit oder Schicksal. Der Bericht dient nur der Unterhaltung und Selbstreflexion.',
    origins: ['CHINA', 'ANTIKES GRIECHENLAND', 'SÜDASIEN', 'ARABISCHE TRADITIONEN', 'EUROPA IM 20. JAHRHUNDERT'],
    descriptions: ['Eine historische Praxis, Gesichtszüge in chinesischen Kulturtraditionen zu deuten.', 'Klassische Schriften, die äußere Erscheinung mit Charakter verbanden.', 'Ein traditionelles System mit Vorstellungen zu Konstitution und äußeren Merkmalen.', 'Eine historische Tradition zur Deutung von Erscheinung und Wahrnehmung.', 'Ein späterer Deutungsansatz, der Gesichtsform und Temperament verband.'],
    examplesKicker: 'STELL DIR DIE ERFAHRUNG VOR', examplesTitle: 'Ein Moment zum genaueren Hinsehen.', disclosure: 'FIKTIVE BEISPIELE ZUR VERANSCHAULICHUNG — KEINE ECHTEN KUNDENSTIMMEN',
    carouselLabel: 'Beispiele zur Veranschaulichung; für mehr horizontal wischen', previous: 'Vorherige Beispiele', next: 'Nächste Beispiele', showPage: 'Beispielseite anzeigen',
  },
  it: {
    caption: 'L’ARTE DI VEDERE DIVERSAMENTE', portraitAlt: 'Ritratto editoriale di una donna adulta bionda su uno sfondo celeste', heroKicker: 'UN RITRATTO, CINQUE PROSPETTIVE',
    framework: 'IL PERCORSO / 05 PROSPETTIVE', traditionsTitle: 'Cinque modi di vedere.', traditionsIntro: 'Il rapporto si ispira a queste autentiche tradizioni storiche e culturali come spunti di riflessione.',
    disclaimer: 'Interpretazioni storiche e culturali, non metodi scientifici. Un volto non rivela personalità, salute o destino. Il rapporto è solo per intrattenimento e riflessione personale.',
    origins: ['CINA', 'GRECIA ANTICA', 'ASIA MERIDIONALE', 'TRADIZIONI ARABE', 'EUROPA DEL XX SECOLO'],
    descriptions: ['Una pratica storica di lettura dei tratti del viso nelle tradizioni culturali cinesi.', 'Scritti classici che collegavano l’aspetto esteriore al carattere.', 'Un sistema tradizionale con idee sulla costituzione e i tratti esteriori.', 'Una tradizione storica di interpretazione dell’aspetto e della percezione.', 'Un quadro interpretativo successivo che collegava forma del viso e temperamento.'],
    examplesKicker: 'IMMAGINA L’ESPERIENZA', examplesTitle: 'Un momento per guardare meglio.', disclosure: 'ESEMPI ILLUSTRATIVI DI FANTASIA — NON SONO TESTIMONIANZE DI CLIENTI REALI',
    carouselLabel: 'Esempi illustrativi; scorri in orizzontale per vederne altri', previous: 'Esempi precedenti', next: 'Esempi successivi', showPage: 'Mostra la pagina degli esempi',
  },
  fr: {
    caption: 'L’ART DE VOIR AUTREMENT', portraitAlt: 'Portrait éditorial d’une femme adulte blonde sur fond céleste', heroKicker: 'UN PORTRAIT, CINQ PERSPECTIVES',
    framework: 'LE CADRE / 05 REGARDS', traditionsTitle: 'Cinq façons de voir.', traditionsIntro: 'Votre rapport s’appuie sur ces véritables traditions historiques et culturelles comme pistes de réflexion.',
    disclaimer: 'Des interprétations historiques et culturelles, pas des méthodes scientifiques. Un visage ne révèle ni personnalité, ni santé, ni destin. Ce rapport est réservé au divertissement et à la réflexion personnelle.',
    origins: ['CHINE', 'GRÈCE ANTIQUE', 'ASIE DU SUD', 'TRADITIONS ARABES', 'EUROPE DU XXE SIÈCLE'],
    descriptions: ['Une pratique historique d’interprétation des traits du visage dans les traditions chinoises.', 'Des écrits classiques reliant l’apparence extérieure au caractère.', 'Un système traditionnel proposant des idées sur la constitution et les traits extérieurs.', 'Une tradition historique d’interprétation de l’apparence et de la perception.', 'Un cadre interprétatif plus récent reliant la forme du visage au tempérament.'],
    examplesKicker: 'IMAGINEZ L’EXPÉRIENCE', examplesTitle: 'Un instant pour regarder de plus près.', disclosure: 'EXEMPLES FICTIFS À TITRE ILLUSTRATIF — PAS DE VRAIS TÉMOIGNAGES CLIENTS',
    carouselLabel: 'Exemples illustratifs, balayez horizontalement pour en voir plus', previous: 'Exemples précédents', next: 'Exemples suivants', showPage: 'Afficher la page d’exemples',
  },
  es: {
    caption: 'EL ARTE DE MIRAR DE OTRA FORMA', portraitAlt: 'Retrato editorial de una mujer adulta rubia sobre un fondo celestial', heroKicker: 'UN RETRATO, CINCO PERSPECTIVAS',
    framework: 'EL MARCO / 05 MIRADAS', traditionsTitle: 'Cinco formas de mirar.', traditionsIntro: 'Tu informe toma estas tradiciones históricas y culturales reales como punto de partida para reflexionar.',
    disclaimer: 'Interpretaciones históricas y culturales, no métodos científicos. Un rostro no revela personalidad, salud ni destino. Este informe es solo para entretenimiento y reflexión personal.',
    origins: ['CHINA', 'GRECIA ANTIGUA', 'ASIA MERIDIONAL', 'TRADICIONES ÁRABES', 'EUROPA DEL SIGLO XX'],
    descriptions: ['Una práctica histórica de lectura de rasgos faciales en las tradiciones culturales chinas.', 'Textos clásicos que relacionaban la apariencia exterior con el carácter.', 'Un sistema tradicional con ideas sobre la constitución y los rasgos externos.', 'Una tradición histórica de interpretación de la apariencia y la percepción.', 'Un marco interpretativo posterior que vinculaba la forma del rostro y el temperamento.'],
    examplesKicker: 'IMAGINA LA EXPERIENCIA', examplesTitle: 'Un momento para mirar más de cerca.', disclosure: 'EJEMPLOS FICTICIOS ILUSTRATIVOS — NO SON TESTIMONIOS DE CLIENTES REALES',
    carouselLabel: 'Ejemplos ilustrativos; desliza horizontalmente para ver más', previous: 'Ejemplos anteriores', next: 'Ejemplos siguientes', showPage: 'Mostrar página de ejemplos',
  },
  zh: {
    caption: '换个角度看世界', portraitAlt: '星空背景下的成年金发女性艺术肖像', heroKicker: '一张肖像，五种视角',
    framework: '解读框架 / 五种视角', traditionsTitle: '五种观察方式。', traditionsIntro: '报告借鉴以下真实存在的历史和文化传统，作为自我反思的起点。',
    disclaimer: '这些是历史与文化解读，并非科学方法。面容无法判定性格、健康或命运。本报告仅供娱乐及自我反思。',
    origins: ['中国', '古希腊', '南亚', '阿拉伯文化传统', '二十世纪欧洲'],
    descriptions: ['中国文化传统中观察和解读面部特征的历史实践。', '将外貌与性格联系起来的古典著作。', '包含体质及外在特征观念的传统体系。', '解释外貌与感知的历史传统。', '将面部形态与气质联系起来的近代解释框架。'],
    examplesKicker: '想象这样的体验', examplesTitle: '留一刻，细细观察。', disclosure: '虚构示例，仅供说明——并非真实客户评价',
    carouselLabel: '说明性示例；左右滑动查看更多', previous: '上一组示例', next: '下一组示例', showPage: '显示示例第',
  },
  ar: {
    caption: 'فن الرؤية من منظور مختلف', portraitAlt: 'صورة فنية لامرأة شقراء بالغة على خلفية سماوية', heroKicker: 'صورة واحدة، خمس وجهات نظر',
    framework: 'الإطار / خمس رؤى', traditionsTitle: 'خمس طرق للنظر.', traditionsIntro: 'يستند تقريرك إلى هذه التقاليد التاريخية والثقافية الفعلية بوصفها منطلقات للتأمل.',
    disclaimer: 'هذه تفسيرات تاريخية وثقافية وليست أساليب علمية. لا يمكن للوجه تحديد الشخصية أو الصحة أو المصير. هذا التقرير للترفيه والتأمل الذاتي فقط.',
    origins: ['الصين', 'اليونان القديمة', 'جنوب آسيا', 'التقاليد العربية', 'أوروبا في القرن العشرين'],
    descriptions: ['ممارسة تاريخية لقراءة ملامح الوجه في التقاليد الثقافية الصينية.', 'كتابات كلاسيكية ربطت المظهر الخارجي بالطباع.', 'نظام تقليدي يضم أفكاراً عن البنية والسمات الظاهرة.', 'تقليد تاريخي في تفسير المظهر والإدراك.', 'إطار تفسيري أحدث ربط شكل الوجه بالمزاج.'],
    examplesKicker: 'تخيّل التجربة', examplesTitle: 'لحظة للنظر عن قرب.', disclosure: 'أمثلة توضيحية خيالية — ليست شهادات عملاء حقيقيين',
    carouselLabel: 'أمثلة توضيحية؛ اسحب أفقياً للمزيد', previous: 'الأمثلة السابقة', next: 'الأمثلة التالية', showPage: 'عرض صفحة الأمثلة',
  },
  ja: {
    caption: '異なる視点で見るということ', portraitAlt: '星空を背景にした成人の金髪女性のエディトリアルポートレート', heroKicker: '一枚の肖像、五つの視点',
    framework: '枠組み / 五つの視点', traditionsTitle: '五つの見方。', traditionsIntro: 'このレポートは、実在する歴史的・文化的伝統を自己省察のきっかけとして取り上げます。',
    disclaimer: 'これらは歴史的・文化的な解釈であり、科学的方法ではありません。顔から性格、健康、運命を判断することはできません。本レポートは娯楽と自己省察のみを目的とします。',
    origins: ['中国', '古代ギリシャ', '南アジア', 'アラブの伝統', '20世紀のヨーロッパ'],
    descriptions: ['中国の文化的伝統における、顔の特徴を読み解く歴史的な実践。', '外見と性格を結びつけた古典の記述。', '体質や外見上の特徴についての考えを含む伝統的な体系。', '外見や知覚を解釈する歴史的な伝統。', '顔の形と気質を結びつけた、後世の解釈の枠組み。'],
    examplesKicker: '体験を想像してみる', examplesTitle: '少しだけ、近くで見る時間。', disclosure: '説明用の架空の例です — 実際のお客様の声ではありません',
    carouselLabel: '説明用の例。横にスワイプして続きを表示', previous: '前の例', next: '次の例', showPage: '例のページを表示',
  },
};

const traditionData = [
  { name: 'Mian Xiang' },
  { name: 'Greek physiognomy' },
  { name: 'Ayurveda' },
  { name: 'Ilm al-Firasa' },
  { name: 'Morphopsychology' },
];

const examples = [
  { language: 'ENGLISH', text: 'I came for the portrait, and stayed for the questions it made me ask about myself.' },
  { language: 'FRANÇAIS', text: 'Une façon inattendue de regarder mon portrait, sans prétendre me définir.' },
  { language: 'ESPAÑOL', text: 'Me gustó descubrir distintas tradiciones en un solo lugar y reflexionar a mi ritmo.' },
  { language: 'DEUTSCH', text: 'Keine Antwort auf alles, sondern ein schöner Anlass, genauer hinzusehen.' },
  { language: 'ITALIANO', text: 'Cinque prospettive diverse mi hanno dato nuovi spunti su cui riflettere.' },
  { language: 'ROMÂNĂ', text: 'Un moment de curiozitate care m-a făcut să privesc portretul altfel.' },
  { language: '日本語', text: '自分の写真を、少し違う角度から眺めるきっかけになりました。' },
  { language: '中文', text: '不同文化的视角，让我重新思考自己熟悉的面容。' },
  { language: 'العربية', text: 'تجربة تأملية فتحت لي باباً لرؤية صورتي من منظور مختلف.' },
];

export function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduced).catch(() => {});
    const subscription = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduced);
    return () => subscription.remove();
  }, []);
  return reduced;
}

export function StarField({ reduced }: { reduced: boolean }) {
  const drift = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) { drift.setValue(0); return; }
    const loop = Animated.loop(Animated.sequence([
      Animated.timing(drift, { toValue: 1, duration: 8500, useNativeDriver: Platform.OS !== 'web' }),
      Animated.timing(drift, { toValue: 0, duration: 8500, useNativeDriver: Platform.OS !== 'web' }),
    ]));
    loop.start();
    return () => loop.stop();
  }, [drift, reduced]);
  const positions = [
    [5, 2, 2], [78, 3, 2], [34, 7, 1], [92, 13, 2], [12, 20, 1],
    [64, 25, 2], [22, 36, 2], [85, 43, 1], [6, 54, 2], [71, 61, 1],
    [35, 72, 2], [95, 79, 2], [14, 88, 1], [61, 96, 2],
  ];
  return <View style={[StyleSheet.absoluteFill, { pointerEvents: 'none' }]}>
    {positions.map(([left, top, size], index) => <Animated.View key={index} style={{
      position: 'absolute', left: `${left}%`, top: `${top}%`, width: size, height: size,
      borderRadius: size, backgroundColor: c.primary,
      opacity: reduced ? .27 : drift.interpolate({ inputRange: [0, 1], outputRange: [index % 3 === 0 ? .16 : .35, index % 3 === 0 ? .48 : .13] }),
      transform: [{ translateY: reduced ? 0 : drift.interpolate({ inputRange: [0, 1], outputRange: [0, index % 2 ? -12 : 12] }) }],
    }} />)}
  </View>;
}

export function PortraitHero({ language, reduced }: { language: string; reduced: boolean }) {
  const glow = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) { glow.setValue(0); return; }
    const loop = Animated.loop(Animated.sequence([
      Animated.timing(glow, { toValue: 1, duration: 3500, useNativeDriver: Platform.OS !== 'web' }),
      Animated.timing(glow, { toValue: 0, duration: 3500, useNativeDriver: Platform.OS !== 'web' }),
    ]));
    loop.start();
    return () => loop.stop();
  }, [glow, reduced]);
  const copy = hooks[language] || hooks.en;
  const words = editorial[language] || editorial.en;
  return <View style={heroStyles.wrap}>
    <View style={heroStyles.imageFrame}>
      <Image source={require('../assets/images/facesecrets-portrait.png')} style={heroStyles.image} resizeMode="cover" accessibilityLabel={words.portraitAlt} />
      <View style={heroStyles.imageCaption}><View style={heroStyles.captionLine} /><Text style={heroStyles.imageCaptionText}>{words.caption}</Text><View style={heroStyles.captionLine} /></View>
    </View>
    <View style={heroStyles.copy}>
      <Text style={heroStyles.kicker}>{words.heroKicker}</Text>
      <Animated.Text style={[heroStyles.title, { opacity: reduced ? 1 : glow.interpolate({ inputRange: [0, 1], outputRange: [.85, 1] }) }]}>{copy.line}</Animated.Text>
      <Text style={heroStyles.subtitle}>{copy.sub}</Text>
      <View style={heroStyles.rule}><View style={heroStyles.diamond} /></View>
    </View>
  </View>;
}

export function Traditions({ language }: { language: string }) {
  const words = editorial[language] || editorial.en;
  return <View style={sectionStyles.section}>
    <Text style={sectionStyles.kicker}>{words.framework}</Text>
    <Text style={sectionStyles.title}>{words.traditionsTitle}</Text>
    <Text style={sectionStyles.lede}>{words.traditionsIntro}</Text>
    <View style={sectionStyles.list}>
      {traditionData.map((item, index) => <View key={item.name} style={sectionStyles.row}>
        <Text style={sectionStyles.number}>0{index + 1}</Text>
        <View style={sectionStyles.rowBody}><Text style={sectionStyles.origin}>{words.origins[index]}</Text><Text style={sectionStyles.name}>{item.name}</Text><Text style={sectionStyles.detail}>{words.descriptions[index]}</Text></View>
        <Feather name="arrow-up-right" size={16} color={c.primary} />
      </View>)}
    </View>
    <View style={sectionStyles.context}><Feather name="info" size={16} color={c.primary} /><Text style={sectionStyles.contextText}>{words.disclaimer}</Text></View>
  </View>;
}

export function IllustrativeCarousel({ reduced, language }: { reduced: boolean; language: string }) {
  const words = editorial[language] || editorial.en;
  const [page, setPage] = useState(0);
  const [width, setWidth] = useState(0);
  const scroll = useRef<ScrollView>(null);
  const pageRef = useRef(0);
  const widthRef = useRef(0);
  widthRef.current = width;
  const go = (next: number) => {
    const target = (next + 3) % 3;
    pageRef.current = target;
    setPage(target);
    scroll.current?.scrollTo({ x: target * widthRef.current, animated: !reduced });
  };
  useEffect(() => {
    if (reduced) return;
    const timer = setInterval(() => go((pageRef.current + 1) % 3), 8000);
    return () => clearInterval(timer);
  }, [reduced]);
  return <View style={sectionStyles.carouselSection}>
    <Text style={sectionStyles.kicker}>{words.examplesKicker}</Text>
    <Text style={sectionStyles.title}>{words.examplesTitle}</Text>
    <View style={sectionStyles.exampleNotice}><Feather name="edit-3" size={15} color={c.primary} /><Text style={sectionStyles.exampleNoticeText}>{words.disclosure}</Text></View>
    <View onLayout={event => setWidth(event.nativeEvent.layout.width)}>
      {width > 0 && <ScrollView ref={scroll} horizontal pagingEnabled showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={event => { const next = Math.max(0, Math.min(2, Math.round(event.nativeEvent.contentOffset.x / width))); pageRef.current = next; setPage(next); }}
        accessibilityLabel={words.carouselLabel}
      >{[0, 1, 2].map(group => <View key={group} style={{ width, gap: 10 }}>
        {examples.slice(group * 3, group * 3 + 3).map((example, index) => <View key={example.language} style={sectionStyles.exampleCard}>
          <View style={sectionStyles.exampleTop}><Text style={sectionStyles.exampleNumber}>0{group * 3 + index + 1} / 09</Text><Text style={sectionStyles.origin}>{example.language}</Text></View>
          <Text style={sectionStyles.exampleText}>{example.text}</Text>
        </View>)}
      </View>)}</ScrollView>}
    </View>
    <View style={sectionStyles.carouselControls}>
      <Pressable testID="examples-previous" accessibilityLabel={words.previous} onPress={() => go(page - 1)} style={sectionStyles.arrow}><Feather name="arrow-left" size={18} color={c.primary} /></Pressable>
      <View style={sectionStyles.dots}>{[0, 1, 2].map(index => <Pressable key={index} testID={`examples-page-${index + 1}`} accessibilityLabel={`${words.showPage} ${index + 1}`} onPress={() => go(index)} style={[sectionStyles.dot, page === index && sectionStyles.activeDot]} />)}</View>
      <Pressable testID="examples-next" accessibilityLabel={words.next} onPress={() => go(page + 1)} style={sectionStyles.arrow}><Feather name="arrow-right" size={18} color={c.primary} /></Pressable>
    </View>
  </View>;
}

const heroStyles = StyleSheet.create({
  wrap: { marginTop: 22 },
  imageFrame: { width: '100%', aspectRatio: 1.08, borderWidth: 1, borderColor: c.border, overflow: 'hidden', backgroundColor: c.card },
  image: { width: '100%', height: '100%' },
  imageCaption: { position: 'absolute', bottom: 0, left: 0, right: 0, minHeight: 42, backgroundColor: 'rgba(9,13,20,0.84)', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 },
  captionLine: { width: 20, height: 1, backgroundColor: c.primary, opacity: .7 },
  imageCaptionText: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 9, letterSpacing: 1.8 },
  copy: { paddingTop: 29, alignItems: 'center' },
  kicker: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 10, letterSpacing: 2.1, textAlign: 'center' },
  title: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 42, lineHeight: 46, textAlign: 'center', marginTop: 16 },
  subtitle: { color: c.mutedForeground, fontFamily: 'DMSans_400Regular', fontSize: 14, lineHeight: 22, textAlign: 'center', marginTop: 14, paddingHorizontal: 10 },
  rule: { width: '100%', marginTop: 28, height: 1, backgroundColor: c.border, alignItems: 'center', justifyContent: 'center' },
  diamond: { width: 8, height: 8, backgroundColor: c.primary, transform: [{ rotate: '45deg' }] },
});

const sectionStyles = StyleSheet.create({
  section: { marginTop: 76 },
  carouselSection: { marginTop: 75, marginBottom: 24 },
  kicker: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 10, letterSpacing: 2 },
  title: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 39, lineHeight: 43, marginTop: 11 },
  lede: { color: c.mutedForeground, fontFamily: 'DMSans_400Regular', fontSize: 14, lineHeight: 23, marginTop: 13 },
  list: { marginTop: 24, borderTopWidth: 1, borderTopColor: c.border },
  row: { flexDirection: 'row', gap: 14, paddingVertical: 22, borderBottomWidth: 1, borderBottomColor: c.border },
  number: { color: c.primary, fontFamily: 'InstrumentSerif_400Regular', fontSize: 25, minWidth: 34 },
  rowBody: { flex: 1 },
  origin: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 9, letterSpacing: 1.4 },
  name: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 27, lineHeight: 32, marginTop: 4 },
  detail: { color: c.mutedForeground, fontFamily: 'DMSans_400Regular', fontSize: 13, lineHeight: 20, marginTop: 5 },
  context: { flexDirection: 'row', gap: 10, padding: 16, marginTop: 22, backgroundColor: c.card, borderLeftWidth: 2, borderLeftColor: c.primary },
  contextText: { flex: 1, color: c.mutedForeground, fontFamily: 'DMSans_400Regular', fontSize: 12, lineHeight: 19 },
  exampleNotice: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, paddingVertical: 15, marginTop: 20, marginBottom: 14, borderTopWidth: 1, borderBottomWidth: 1, borderColor: c.border },
  exampleNoticeText: { color: c.foreground, flex: 1, fontFamily: 'DMSans_700Bold', fontSize: 10, lineHeight: 16, letterSpacing: 1 },
  exampleCard: { padding: 18, minHeight: 125, backgroundColor: c.card, borderWidth: 1, borderColor: c.border, justifyContent: 'space-between' },
  exampleTop: { flexDirection: 'row', justifyContent: 'space-between', gap: 8 },
  exampleNumber: { color: c.mutedForeground, fontFamily: 'DMSans_400Regular', fontSize: 10, letterSpacing: 1 },
  exampleText: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 21, lineHeight: 26, marginTop: 10 },
  carouselControls: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 17 },
  arrow: { width: 48, height: 48, alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: c.border },
  dots: { flexDirection: 'row', alignItems: 'center', gap: 9 },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: c.border },
  activeDot: { backgroundColor: c.primary, width: 22 },
});