import React, { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Animated, Image, Linking, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import colors from '@/constants/colors';
import { ApiError, mobileApi, type Analysis, type Page } from '@/lib/mobile-api';
import { availableReport, buyReport, loginForReport, restoreReportPurchases } from '@/lib/revenuecat';
import { loadDeviceCredential, loadSession, saveDeviceCredential, saveSession } from '@/lib/session-store';
import { IllustrativeCarousel, PortraitHero, StarField, Traditions, useReducedMotion } from '@/components/CelestialEditorial';
import type { PurchasesPackage } from 'react-native-purchases';

const c = colors.light;
const fallbackLanguages = { en: 'English', ro: 'Română', de: 'Deutsch', it: 'Italiano', fr: 'Français', es: 'Español', zh: '中文', ar: 'العربية', ja: '日本語' };
type Step = 'choose' | 'upload' | 'unlock' | 'analysis' | 'result';
type Photo = { uri: string; mimeType?: string; fileSize?: number; width: number; height: number };
const purchaseCopy: Record<string, { buy: string; restore: string; confirm: string; question: string; later: string; verified: string; unavailable: string }> = {
  en: { buy: 'Unlock report', restore: 'Restore a purchase', confirm: 'Confirm purchase', question: 'Buy one portrait report for', later: 'Not now', verified: 'Purchase verified. One report is unlocked.', unavailable: 'Purchases are unavailable right now. You can still use a valid promo code.' },
  ro: { buy: 'Deblochează raportul', restore: 'Restaurează achiziția', confirm: 'Confirmă achiziția', question: 'Cumperi un raport pentru', later: 'Nu acum', verified: 'Achiziția a fost verificată. Un raport este deblocat.', unavailable: 'Achizițiile nu sunt disponibile acum. Poți folosi un cod promoțional valid.' },
  de: { buy: 'Bericht freischalten', restore: 'Kauf wiederherstellen', confirm: 'Kauf bestätigen', question: 'Einen Porträtbericht kaufen für', later: 'Nicht jetzt', verified: 'Kauf bestätigt. Ein Bericht ist freigeschaltet.', unavailable: 'Käufe sind derzeit nicht verfügbar. Du kannst einen gültigen Aktionscode verwenden.' },
  it: { buy: 'Sblocca il rapporto', restore: 'Ripristina acquisto', confirm: 'Conferma acquisto', question: 'Acquistare un rapporto per', later: 'Non ora', verified: 'Acquisto verificato. Un rapporto è sbloccato.', unavailable: 'Gli acquisti non sono disponibili. Puoi usare un codice promozionale valido.' },
  fr: { buy: 'Débloquer le rapport', restore: 'Restaurer un achat', confirm: "Confirmer l'achat", question: 'Acheter un rapport pour', later: 'Pas maintenant', verified: 'Achat vérifié. Un rapport est débloqué.', unavailable: 'Les achats sont indisponibles pour le moment. Vous pouvez utiliser un code promo valide.' },
  es: { buy: 'Desbloquear informe', restore: 'Restaurar compra', confirm: 'Confirmar compra', question: 'Comprar un informe por', later: 'Ahora no', verified: 'Compra verificada. Un informe desbloqueado.', unavailable: 'Las compras no están disponibles ahora. Puedes usar un código promocional válido.' },
  zh: { buy: '解锁报告', restore: '恢复购买', confirm: '确认购买', question: '购买一份肖像报告，价格', later: '暂不', verified: '购买已验证，报告已解锁。', unavailable: '暂时无法购买。你仍可使用有效的优惠码。' },
  ar: { buy: 'افتح التقرير', restore: 'استعادة الشراء', confirm: 'تأكيد الشراء', question: 'شراء تقرير صورة شخصية مقابل', later: 'ليس الآن', verified: 'تم التحقق من الشراء. تم فتح تقرير واحد.', unavailable: 'عمليات الشراء غير متاحة الآن. يمكنك استخدام رمز ترويجي صالح.' },
  ja: { buy: 'レポートを購入', restore: '購入を復元', confirm: '購入を確認', question: 'ポートレートレポートを購入：', later: '後で', verified: '購入を確認しました。レポートを1件利用できます。', unavailable: '現在購入できません。有効なプロモーションコードは使用できます。' },
};

function ReportSection({ title, value }: { title: string; value: unknown }) {
  if (typeof value === 'string') return <View style={styles.panel}><Text style={styles.eyebrow}>{title}</Text><Text style={styles.body}>{value}</Text></View>;
  if (Array.isArray(value)) return <View style={styles.panel}><Text style={styles.eyebrow}>{title}</Text>{value.map((item, i) => <Text key={i} style={styles.body}>• {String(item)}</Text>)}</View>;
  if (value && typeof value === 'object') return <View style={styles.panel}><Text style={styles.eyebrow}>{title}</Text>{Object.entries(value).map(([key, item]) => <Text key={key} style={styles.body}><Text style={{ color: c.primary }}>{key.replaceAll('_', ' ')} · </Text>{Array.isArray(item) ? item.join(' · ') : String(item)}</Text>)}</View>;
  return null;
}

function GoldShimmer() {
  const reduced = useReducedMotion();
  const progress = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    if (reduced) return;
    const loop = Animated.loop(Animated.sequence([
      Animated.timing(progress, { toValue: 1, duration: 1600, useNativeDriver: Platform.OS !== 'web' }),
      Animated.delay(5500),
      Animated.timing(progress, { toValue: 0, duration: 0, useNativeDriver: Platform.OS !== 'web' }),
    ]));
    loop.start();
    return () => loop.stop();
  }, [progress, reduced]);
  return <Animated.View style={[styles.shimmer, { pointerEvents: 'none', opacity: reduced ? 0 : .24, transform: [{ translateX: progress.interpolate({ inputRange: [0, 1], outputRange: [-80, 560] }) }, { skewX: '-25deg' }] }]} />;
}

function Action({ title, icon, onPress, secondary, luminous, disabled, testID }: { title: string; icon: keyof typeof Feather.glyphMap; onPress: () => void; secondary?: boolean; luminous?: boolean; disabled?: boolean; testID?: string }) {
  return <Pressable testID={testID} disabled={disabled} onPress={onPress} style={({ pressed }) => [styles.action, secondary && styles.secondary, luminous && styles.luminous, pressed && { transform: [{ translateY: 3 }], opacity: .82 }, disabled && { opacity: .55 }]}>
    {(!secondary || luminous) && <View style={[styles.actionHighlight, { pointerEvents: 'none' }]} />}
    {(!secondary || luminous) && <GoldShimmer />}
    <Feather name={icon} color={secondary ? c.primary : c.primaryForeground} size={17} />
    <Text style={[styles.actionText, secondary && { color: c.primary }]}>{title}</Text>
  </Pressable>;
}

export default function Home() {
  const insets = useSafeAreaInsets();
  const reducedMotion = useReducedMotion();
  const [language, setLanguage] = useState('en');
  const [page, setPage] = useState<Page | null>(null);
  const [step, setStep] = useState<Step>('choose');
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [token, setToken] = useState('');
  const [userId, setUserId] = useState('');
  const [reportPackage, setReportPackage] = useState<PurchasesPackage | null>(null);
  const [purchaseConfirm, setPurchaseConfirm] = useState(false);
  const [promo, setPromo] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [languageOpen, setLanguageOpen] = useState(false);
  const t = (key: string, fallback: string) => page?.translations?.[`ui_${key}`] || fallback;
  const p = purchaseCopy[language] || purchaseCopy.en;

  useEffect(() => {
    let alive = true;
    mobileApi.page(language).then(value => { if (alive) setPage(value); }).catch(() => { if (alive) setNotice('Language data is unavailable. Please retry.'); });
    return () => { alive = false; };
  }, [language]);

  useEffect(() => {
    let alive = true;
    loadSession().then(async saved => {
      if (!saved || !alive) return;
      const result = await mobileApi.result(saved.token).catch(error => {
        if (error instanceof ApiError && error.status === 401) return 'expired' as const;
        if (error instanceof ApiError && error.status === 404) return null;
        throw error;
      });
      if (!alive) return;
      if (result === 'expired') { await saveSession(null); setNotice('Your previous session expired. Start a new one.'); return; }
      setToken(saved.token); setUserId(saved.userId); setAccepted(saved.accepted);
      if (result?.analysis) { setAnalysis(result.analysis); setStep('result'); }
      else setStep('unlock');
    }).catch(() => { if (alive) setNotice('Your previous session could not be restored. You can start a new one.'); });
    return () => { alive = false; };
  }, []);

  useEffect(() => {
    if (step !== 'unlock' || !userId) return;
    let alive = true;
    loginForReport(userId).then(availableReport).then(value => {
      if (alive) setReportPackage(value);
    }).catch(() => { if (alive) setReportPackage(null); });
    return () => { alive = false; };
  }, [step, userId]);

  const handleError = (err: unknown) => {
    setNotice(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    setBusy(false);
  };
  const select = async (camera: boolean) => {
    setNotice('');
    try {
      const permission = camera ? await ImagePicker.requestCameraPermissionsAsync() : await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        setNotice(camera ? t('camera_denied', 'Camera permission is needed to take a portrait.') : 'Photo library permission is needed to choose a portrait.');
        if (!permission.canAskAgain && Platform.OS !== 'web') setNotice('Permission denied. Open device settings to grant access, then retry.');
        return;
      }
      const options: ImagePicker.ImagePickerOptions = { mediaTypes: ['images'], allowsEditing: false, quality: .9 };
      const result = camera ? await ImagePicker.launchCameraAsync(options) : await ImagePicker.launchImageLibraryAsync(options);
      if (result.canceled || !result.assets.length) return;
      const asset = result.assets[0];
      if (asset.fileSize && asset.fileSize > 16 * 1024 * 1024) throw new Error(t('too_large', 'Image must be smaller than 16 MB.'));
      if (asset.width < 256 || asset.height < 256) throw new Error('Choose an image at least 256 × 256 pixels.');
      if (asset.mimeType && !['image/jpeg', 'image/png', 'image/gif'].includes(asset.mimeType)) throw new Error(t('bad_type', 'Use a JPEG, PNG, or GIF image.'));
      setPhoto({ uri: asset.uri, mimeType: asset.mimeType, fileSize: asset.fileSize, width: asset.width, height: asset.height });
      setStep('choose');
      Haptics.selectionAsync();
    } catch (error) { handleError(error); }
  };
  const upload = async () => {
    if (!photo) return setNotice(t('choose_first', 'Choose a portrait first.'));
    setBusy(true); setNotice(''); setStep('upload');
    try {
      const created = token && userId
        ? { access_token: token, rc_app_user_id: userId }
        : await mobileApi.session(await loadDeviceCredential());
      if (created.device_token) await saveDeviceCredential(created.device_token);
      await mobileApi.upload(created.access_token, photo.uri, language, photo.mimeType);
      await saveSession({ token: created.access_token, userId: created.rc_app_user_id, accepted });
      setToken(created.access_token); setUserId(created.rc_app_user_id);
      setStep('unlock'); setPhoto(null);
    } catch (error) { setStep('choose'); handleError(error); }
    finally { setBusy(false); }
  };
  const checkPromo = async () => {
    if (!promo.trim() || !token) return;
    setBusy(true); setNotice('');
    try {
      const result = await mobileApi.promo(token, promo.trim());
      if (!result.success) throw new Error(result.message || t('invalid', 'Invalid code.'));
      setAccepted(true);
      await saveSession({ token, userId, accepted: true });
      setNotice(t('accepted', 'Promo code accepted. One analysis unlocked.'));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) { handleError(error); }
    finally { setBusy(false); }
  };
  const redeem = async () => {
    if (!token || !userId) return;
    const result = await mobileApi.redeem(token);
    if (!result.success) throw new Error(result.message || 'Purchase could not be verified.');
    setAccepted(true);
    await saveSession({ token, userId, accepted: true });
    setNotice(p.verified);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };
  const purchase = async () => {
    if (!reportPackage || !userId || !token) return;
    setPurchaseConfirm(false); setBusy(true); setNotice('');
    try {
      await loginForReport(userId);
      await buyReport(reportPackage);
      await redeem();
    } catch (error) {
      if (!(error && typeof error === 'object' && 'userCancelled' in error && error.userCancelled)) handleError(error);
    } finally { setBusy(false); }
  };
  const restore = async () => {
    if (!token || !userId) return;
    setBusy(true); setNotice('');
    try {
      await loginForReport(userId);
      await restoreReportPurchases();
      await redeem();
    } catch (error) { handleError(error); }
    finally { setBusy(false); }
  };
  const run = async () => {
    if (!token || !accepted) return;
    setBusy(true); setNotice(''); setStep('analysis');
    try {
      const data = await mobileApi.analyze(token);
      setAnalysis(data.analysis); setStep('result');
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch (error) {
      // An interrupted response may still mean the server finished the report.
      const completed = await mobileApi.result(token).catch(() => null);
      if (completed?.analysis) { setAnalysis(completed.analysis); setStep('result'); }
      else if (error instanceof ApiError && (error.status === 400 || error.status === 422)) {
        setStep('choose');
        setNotice(`${error.message} Select another portrait; your unlock is still available.`);
      } else {
        if (error instanceof ApiError && error.status === 403) {
          setAccepted(false);
          await saveSession({ token, userId, accepted: false });
        }
        setStep('unlock'); handleError(error);
      }
    }
    finally { setBusy(false); }
  };
  const startOver = async () => {
    if (token) await mobileApi.cancel(token).catch(() => {});
    await saveSession(null);
    setToken(''); setUserId(''); setReportPackage(null); setPromo(''); setAccepted(false); setAnalysis(null); setPhoto(null); setNotice(''); setStep('choose');
  };
  const retryPermissions = () => Linking.openSettings().catch(handleError);
  const languages = page?.languages || fallbackLanguages;
  return <View style={styles.root}>
    <StarField reduced={reducedMotion} />
    <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={[styles.content, { paddingTop: Platform.OS === 'web' ? 76 : insets.top + 18, paddingBottom: Platform.OS === 'web' ? 48 : insets.bottom + 34 }]}>
      <View style={styles.header}>
        <View style={styles.brand}><View style={styles.mark}><Feather name="star" size={15} color={c.primary} /></View><Text style={styles.brandText}>Face<Text style={styles.brandAccent}>Secrets</Text></Text></View>
        <Pressable accessibilityRole="button" accessibilityLabel="Select language" accessibilityState={{ expanded: languageOpen }} onPress={() => setLanguageOpen(!languageOpen)} style={styles.languageButton} testID="language"><Feather name="globe" size={14} color={c.primary} /><Text style={styles.languageText}>{language.toUpperCase()}</Text><Feather name={languageOpen ? 'chevron-up' : 'chevron-down'} size={13} color={c.primary} /></Pressable>
      </View>
      {languageOpen && <View style={styles.languages}>{Object.entries(languages).map(([code, label]) => <Pressable accessibilityRole="button" key={code} onPress={() => { setLanguage(code); setLanguageOpen(false); }} style={styles.languageItem}><Text style={[styles.body, code === language && { color: c.primary }]}>{label}</Text></Pressable>)}</View>}

      {step === 'choose' && <>
        <PortraitHero language={language} reduced={reducedMotion} />
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>01 / {t('session', 'YOUR SESSION')}</Text><Text style={styles.heading}>{t('session_title', 'Begin your reflection')}</Text><Text style={styles.muted}>A clear, front-facing portrait is all you need.</Text></View>
        {photo ? <Image source={{ uri: photo.uri }} style={styles.photo} /> : <View style={styles.empty}><Feather name="user" color={c.primary} size={29} /><Text style={styles.emptyTitle}>{t('upload', 'Your portrait')}</Text><Text style={styles.muted}>{t('file_help', 'Use a clear front-facing photo in soft, even light.')}</Text></View>}
        <View style={styles.buttons}><Action testID="take-photo" title={t('camera', 'Take a photo')} icon="camera" onPress={() => select(true)} secondary luminous /><Action testID="choose-photo" title={t('upload', 'Choose a photo')} icon="image" onPress={() => select(false)} secondary luminous /></View>
        {photo && <Action testID="continue" title={t('analyze', 'Continue to analysis')} icon="arrow-right" onPress={upload} disabled={busy} />}
        {notice.includes('Open device settings') && <Action title="Open settings" icon="settings" onPress={retryPermissions} secondary />}
        <Traditions language={language} />
        <IllustrativeCarousel reduced={reducedMotion} language={language} />
      </>}

      {step === 'upload' && <View style={styles.wait}><ActivityIndicator color={c.primary} size="large" /><Text style={styles.heading}>{t('uploading', 'Uploading your portrait')}</Text><Text style={styles.muted}>Your image is processed privately and removed after analysis.</Text></View>}
      {step === 'unlock' && <>
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>02 / {t('session', 'YOUR SESSION')}</Text><Text style={styles.heading}>{t('analyze', 'Unlock your report')}</Text></View>
        <View style={styles.panel}><Feather name="lock" color={c.primary} size={22} /><Text style={styles.panelTitle}>Private portrait reading</Text><Text style={styles.body}>Your image is ready. A one-time promotion unlocks a complete analysis and downloadable PDF.</Text>
          {!accepted && reportPackage && <>
            <Text style={styles.body}>One portrait report · {reportPackage.product.priceString}</Text>
            <Action testID="purchase-report" title={`${p.buy} · ${reportPackage.product.priceString}`} icon="credit-card" onPress={() => setPurchaseConfirm(true)} disabled={busy} />
            <Action testID="restore-purchases" title={p.restore} icon="refresh-cw" secondary onPress={restore} disabled={busy} />
          </>}
          {!accepted && <Action testID="verify-purchase" title="Verify an existing purchase" icon="check-circle" secondary onPress={() => { setBusy(true); redeem().catch(handleError).finally(() => setBusy(false)); }} disabled={busy} />}
          {!accepted && !reportPackage && <Text style={styles.muted}>{p.unavailable}</Text>}
          <TextInput testID="promo-code" value={promo} onChangeText={setPromo} placeholder={t('promo', 'Promo code')} placeholderTextColor={c.mutedForeground} style={styles.input} autoCapitalize="none" />
          <Action testID="apply-promo" title={busy ? 'Checking…' : t('check', 'Apply code')} icon="check" onPress={checkPromo} secondary disabled={busy || !promo.trim()} />
          {accepted && <Action testID="run-analysis" title={t('free', 'Start analysis')} icon="arrow-right" onPress={run} disabled={busy} />}
        </View>
        <View style={styles.unavailable}><Feather name="info" color={c.primary} size={18} /><Text style={styles.muted}>One purchase unlocks one portrait report. Purchases are verified before analysis. Use a valid code instead if you have one.</Text></View>
        {purchaseConfirm && <View style={styles.panel}><Text style={styles.panelTitle}>{p.confirm}</Text><Text style={styles.body}>{p.question} {reportPackage?.product.priceString}?{__DEV__ ? ' Test Store — no real charge.' : ''}</Text><Action title={p.confirm} icon="check" onPress={purchase} /><Action title={p.later} icon="x" secondary onPress={() => setPurchaseConfirm(false)} /></View>}
        <Action title={t('cancel_button', 'Cancel session')} icon="x" onPress={startOver} secondary />
      </>}
      {step === 'analysis' && <View style={styles.wait}><ActivityIndicator color={c.primary} size="large" /><Text style={styles.heading}>{t('processing', 'Preparing your reflection')}</Text><Text style={styles.muted}>{t('comparing', 'Considering five ancient perspectives…')}</Text></View>}
      {step === 'result' && <>
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>{t('complete', 'YOUR REPORT IS READY')}</Text><Text style={styles.heading}>{t('success', 'A new perspective')}</Text><Text style={styles.body}>{t('success_detail', 'Your private analysis is complete.')}</Text></View>
        <View style={styles.panel}><Text style={styles.eyebrow}>{t('summary', 'SUMMARY')}</Text><Text style={styles.body}>{String(analysis?.executive_summary || 'Your report is ready to read.')}</Text></View>
        {analysis?.traditional_perspectives && <ReportSection title={t('lenses_title', 'FIVE PERSPECTIVES')} value={analysis.traditional_perspectives} />}
        {analysis?.recomandari_dezvoltare && <ReportSection title={t('recommendations', 'REFLECTION PROMPTS')} value={analysis.recomandari_dezvoltare} />}
        {analysis?.disclaimer && <ReportSection title={t('disclaimer', 'IMPORTANT CONTEXT')} value={analysis.disclaimer} />}
        <Action testID="share-report" title={t('download', 'Save or share your PDF')} icon="download" onPress={() => { setBusy(true); mobileApi.shareReport(token).catch(handleError).finally(() => setBusy(false)); }} disabled={busy} />
        <Action title={t('again', 'Start again')} icon="rotate-ccw" secondary onPress={startOver} />
      </>}
      {!!notice && <View style={styles.notice}><Feather name="info" size={16} color={c.accent} /><Text style={styles.noticeText}>{notice}</Text></View>}
      <View style={styles.footer}><Feather name="shield" color={c.primary} size={15} /><Text style={styles.muted}>{t('privacy', 'Your portrait is used only for your report. For entertainment and self-reflection; not medical, psychological or predictive advice. Photos are deleted after processing. Reports are removed after the session expires.')}</Text></View>
    </ScrollView>
  </View>;
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: c.background },
  content: { paddingHorizontal: 20, maxWidth: 560, width: '100%', alignSelf: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 17, borderBottomWidth: 1, borderBottomColor: c.border },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 8, flexShrink: 1 },
  mark: { width: 31, height: 31, borderRadius: 16, borderWidth: 1, borderColor: c.primary, alignItems: 'center', justifyContent: 'center' },
  markText: { fontFamily: 'InstrumentSerif_400Regular', fontSize: 18, color: c.primary },
  brandText: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 25, letterSpacing: -.6 },
  brandAccent: { color: c.primary },
  languageButton: { paddingHorizontal: 10, paddingVertical: 9, flexDirection: 'row', alignItems: 'center', gap: 5, borderWidth: 1, borderColor: c.border, minHeight: 40 },
  languageText: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 11, letterSpacing: 1 },
  languages: { borderColor: c.border, borderWidth: 1, backgroundColor: c.card, marginTop: 8, paddingVertical: 6, zIndex: 2 },
  languageItem: { paddingVertical: 10, paddingHorizontal: 16 },
  intro: { paddingTop: 45, gap: 18 },
  eyebrow: { color: c.primary, fontFamily: 'DMSans_700Bold', fontSize: 10, letterSpacing: 2, textTransform: 'uppercase' },
  hero: { fontFamily: 'InstrumentSerif_400Regular', fontSize: 58, lineHeight: 58, color: c.foreground },
  body: { fontFamily: 'DMSans_400Regular', color: c.foreground, fontSize: 15, lineHeight: 24 },
  muted: { fontFamily: 'DMSans_400Regular', color: c.mutedForeground, fontSize: 13, lineHeight: 21, flexShrink: 1 },
  orbitWrap: { height: 205, marginTop: 38, backgroundColor: c.card, borderWidth: 1, borderColor: c.border, alignItems: 'center', justifyContent: 'center', overflow: 'hidden' },
  orbitOuter: { width: 163, height: 163, borderRadius: 82, borderWidth: 1, borderColor: c.primary, alignItems: 'center', justifyContent: 'center', opacity: .8 },
  orbitInner: { width: 133, height: 133, borderRadius: 70, borderWidth: 1, borderColor: c.accent, alignItems: 'center', justifyContent: 'center' },
  orb: { width: 105, height: 105, borderRadius: 55, backgroundColor: c.secondary, borderWidth: 17, borderColor: c.background },
  scan: { position: 'absolute', height: 1, left: '18%', right: '18%', backgroundColor: c.primary },
  sectionHead: { marginTop: 48, marginBottom: 24, gap: 8 },
  heading: { fontFamily: 'InstrumentSerif_400Regular', color: c.foreground, fontSize: 38, lineHeight: 42 },
  empty: { minHeight: 175, borderWidth: 1, borderStyle: 'dashed', borderColor: c.primary, backgroundColor: c.card, alignItems: 'center', justifyContent: 'center', gap: 9, padding: 20 },
  emptyTitle: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 23 },
  photo: { width: '100%', height: 240, borderWidth: 1, borderColor: c.border },
  buttons: { marginTop: 16, gap: 10 },
  action: { minHeight: 54, backgroundColor: c.primary, borderColor: '#f1d79e', borderBottomColor: '#896a3c', borderWidth: 1, flexDirection: 'row', gap: 10, alignItems: 'center', justifyContent: 'center', padding: 10, marginTop: 10, overflow: 'hidden', elevation: 4, shadowColor: c.primary, shadowOpacity: .18, shadowRadius: 10, shadowOffset: { width: 0, height: 3 } },
  actionHighlight: { position: 'absolute', top: 1, left: 1, right: 1, height: 2, backgroundColor: '#f7e5bb', opacity: .8 },
  shimmer: { position: 'absolute', top: -15, bottom: -15, left: 0, width: 42, backgroundColor: '#fff4d5' },
  secondary: { backgroundColor: c.card, borderColor: c.border, elevation: 0, shadowOpacity: 0 },
  luminous: { borderColor: c.primary, borderBottomColor: c.border, elevation: 4, shadowOpacity: .28, shadowRadius: 12 },
  actionText: { color: c.primaryForeground, fontFamily: 'DMSans_700Bold', fontSize: 14 },
  panel: { backgroundColor: c.card, borderWidth: 1, borderColor: c.border, padding: 22, gap: 15 },
  panelTitle: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 28 },
  input: { backgroundColor: c.input, borderWidth: 1, borderColor: c.border, color: c.foreground, fontFamily: 'DMSans_400Regular', minHeight: 50, paddingHorizontal: 14, marginTop: 8 },
  unavailable: { flexDirection: 'row', gap: 11, paddingVertical: 25 },
  wait: { paddingVertical: 115, alignItems: 'center', gap: 20 },
  notice: { marginTop: 20, borderLeftWidth: 2, borderLeftColor: c.accent, padding: 12, backgroundColor: c.card, flexDirection: 'row', gap: 10 },
  noticeText: { fontFamily: 'DMSans_400Regular', color: c.foreground, fontSize: 13, flex: 1, lineHeight: 20 },
  footer: { flexDirection: 'row', gap: 12, marginTop: 40, borderTopWidth: 1, borderTopColor: c.border, paddingTop: 24 },
});