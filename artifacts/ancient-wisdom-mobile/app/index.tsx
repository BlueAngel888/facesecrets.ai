import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Image, Linking, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { Feather } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import colors from '@/constants/colors';
import { mobileApi, type Analysis, type Page } from '@/lib/mobile-api';

const c = colors.light;
const fallbackLanguages = { en: 'English', ro: 'Română', de: 'Deutsch', it: 'Italiano', fr: 'Français', es: 'Español', zh: '中文', ar: 'العربية', ja: '日本語' };
type Step = 'choose' | 'upload' | 'unlock' | 'analysis' | 'result';
type Photo = { uri: string; mimeType?: string; fileSize?: number; width: number; height: number };

function Action({ title, icon, onPress, secondary, disabled, testID }: { title: string; icon: keyof typeof Feather.glyphMap; onPress: () => void; secondary?: boolean; disabled?: boolean; testID?: string }) {
  return <Pressable testID={testID} disabled={disabled} onPress={onPress} style={({ pressed }) => [styles.action, secondary && styles.secondary, (pressed || disabled) && { opacity: .55 }]}>
    <Feather name={icon} color={secondary ? c.primary : c.primaryForeground} size={17} />
    <Text style={[styles.actionText, secondary && { color: c.primary }]}>{title}</Text>
  </Pressable>;
}

export default function Home() {
  const insets = useSafeAreaInsets();
  const [language, setLanguage] = useState('en');
  const [page, setPage] = useState<Page | null>(null);
  const [step, setStep] = useState<Step>('choose');
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [token, setToken] = useState('');
  const [promo, setPromo] = useState('');
  const [accepted, setAccepted] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [languageOpen, setLanguageOpen] = useState(false);
  const t = (key: string, fallback: string) => page?.translations?.[`ui_${key}`] || fallback;

  useEffect(() => {
    let alive = true;
    mobileApi.page(language).then(value => { if (alive) setPage(value); }).catch(() => { if (alive) setNotice('Language data is unavailable. Please retry.'); });
    return () => { alive = false; };
  }, [language]);

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
      const created = await mobileApi.session();
      setToken(created.token);
      await mobileApi.upload(created.token, photo.uri, language, photo.mimeType);
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
      setNotice(t('accepted', 'Promo code accepted. One analysis unlocked.'));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
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
    } catch (error) { setStep('unlock'); handleError(error); }
    finally { setBusy(false); }
  };
  const startOver = async () => {
    if (token) await mobileApi.cancel(token).catch(() => {});
    setToken(''); setPromo(''); setAccepted(false); setAnalysis(null); setPhoto(null); setNotice(''); setStep('choose');
  };
  const retryPermissions = () => Linking.openSettings().catch(handleError);
  const languages = page?.languages || fallbackLanguages;
  return <View style={styles.root}>
    <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={[styles.content, { paddingTop: Platform.OS === 'web' ? 76 : insets.top + 18, paddingBottom: Platform.OS === 'web' ? 48 : insets.bottom + 34 }]}>
      <View style={styles.header}>
        <View style={styles.brand}><View style={styles.mark}><Text style={styles.markText}>a</Text></View><Text style={styles.brandText}>ANCIENT WISDOM</Text></View>
        <Pressable onPress={() => setLanguageOpen(!languageOpen)} style={styles.languageButton} testID="language"><Text style={styles.languageText}>{language.toUpperCase()}  ⌄</Text></Pressable>
      </View>
      {languageOpen && <View style={styles.languages}>{Object.entries(languages).map(([code, label]) => <Pressable key={code} onPress={() => { setLanguage(code); setLanguageOpen(false); }} style={styles.languageItem}><Text style={[styles.body, code === language && { color: c.primary }]}>{label}</Text></Pressable>)}</View>}

      <View style={styles.intro}>
        <Text style={styles.eyebrow}>{t('hero_eyebrow', 'A PRIVATE REFLECTION')}</Text>
        <Text style={styles.hero}>{t('title_before', 'Discover your ')}<Text style={{ color: c.primary }}>{t('title_emphasis', 'inner world')}</Text>{t('title_after', '.')}</Text>
        <Text style={styles.body}>{t('subtitle', 'Ancient perspectives and modern AI, for personal reflection.')}</Text>
      </View>

      {step === 'choose' && <>
        <View style={styles.orbitWrap}><View style={styles.orbitOuter}><View style={styles.orbitInner}><View style={styles.orb} /></View></View><View style={styles.scan} /></View>
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>01 / {t('session', 'YOUR SESSION')}</Text><Text style={styles.heading}>{t('session_title', 'Begin your reflection')}</Text></View>
        {photo ? <Image source={{ uri: photo.uri }} style={styles.photo} /> : <View style={styles.empty}><Feather name="user" color={c.primary} size={29} /><Text style={styles.emptyTitle}>{t('upload', 'Your portrait')}</Text><Text style={styles.muted}>{t('file_help', 'Use a clear front-facing photo in soft, even light.')}</Text></View>}
        <View style={styles.buttons}><Action testID="take-photo" title={t('camera', 'Take a photo')} icon="camera" onPress={() => select(true)} secondary /><Action testID="choose-photo" title={t('upload', 'Choose a photo')} icon="image" onPress={() => select(false)} secondary /></View>
        {photo && <Action testID="continue" title={t('analyze', 'Continue to analysis')} icon="arrow-right" onPress={upload} disabled={busy} />}
        {notice.includes('Open device settings') && <Action title="Open settings" icon="settings" onPress={retryPermissions} secondary />}
      </>}

      {step === 'upload' && <View style={styles.wait}><ActivityIndicator color={c.primary} size="large" /><Text style={styles.heading}>{t('uploading', 'Uploading your portrait')}</Text><Text style={styles.muted}>Your image is processed privately and removed after analysis.</Text></View>}
      {step === 'unlock' && <>
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>02 / {t('session', 'YOUR SESSION')}</Text><Text style={styles.heading}>{t('analyze', 'Unlock your report')}</Text></View>
        <View style={styles.panel}><Feather name="lock" color={c.primary} size={22} /><Text style={styles.panelTitle}>Private portrait reading</Text><Text style={styles.body}>Your image is ready. A one-time promotion unlocks a complete analysis and downloadable PDF.</Text>
          <TextInput testID="promo-code" value={promo} onChangeText={setPromo} placeholder={t('promo', 'Promo code')} placeholderTextColor={c.mutedForeground} style={styles.input} autoCapitalize="none" />
          <Action testID="apply-promo" title={busy ? 'Checking…' : t('check', 'Apply code')} icon="check" onPress={checkPromo} secondary disabled={busy || !promo.trim()} />
          {accepted && <Action testID="run-analysis" title={t('free', 'Start analysis')} icon="arrow-right" onPress={run} disabled={busy} />}
        </View>
        <View style={styles.unavailable}><Feather name="info" color={c.primary} size={18} /><Text style={styles.muted}>In-app purchases are not available yet. The owner must connect RevenueCat before paid analyses can be enabled. No payment will be taken.</Text></View>
        <Action title={t('cancel_button', 'Cancel session')} icon="x" onPress={startOver} secondary />
      </>}
      {step === 'analysis' && <View style={styles.wait}><ActivityIndicator color={c.primary} size="large" /><Text style={styles.heading}>{t('processing', 'Preparing your reflection')}</Text><Text style={styles.muted}>{t('comparing', 'Considering five ancient perspectives…')}</Text></View>}
      {step === 'result' && <>
        <View style={styles.sectionHead}><Text style={styles.eyebrow}>{t('complete', 'YOUR REPORT IS READY')}</Text><Text style={styles.heading}>{t('success', 'A new perspective')}</Text><Text style={styles.body}>{t('success_detail', 'Your private analysis is complete.')}</Text></View>
        <View style={styles.panel}><Text style={styles.eyebrow}>{t('summary', 'SUMMARY')}</Text><Text style={styles.body}>{String(analysis?.executive_summary || 'Your report is ready to read.')}</Text></View>
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
  content: { paddingHorizontal: 24, maxWidth: 560, width: '100%', alignSelf: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingBottom: 22, borderBottomWidth: 1, borderBottomColor: c.border },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  mark: { width: 32, height: 32, borderRadius: 16, borderWidth: 1, borderColor: c.primary, alignItems: 'center', justifyContent: 'center' },
  markText: { fontFamily: 'InstrumentSerif_400Regular', fontSize: 23, color: c.primary, marginTop: -4 },
  brandText: { color: c.foreground, fontFamily: 'DMSans_700Bold', fontSize: 11, letterSpacing: 1.7 },
  languageButton: { padding: 10 },
  languageText: { color: c.primary, fontFamily: 'SpaceMono_400Regular', fontSize: 11 },
  languages: { borderColor: c.border, borderWidth: 1, backgroundColor: c.card, marginTop: 8, paddingVertical: 6 },
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
  sectionHead: { marginTop: 38, marginBottom: 24, gap: 8 },
  heading: { fontFamily: 'InstrumentSerif_400Regular', color: c.foreground, fontSize: 38, lineHeight: 42 },
  empty: { minHeight: 165, borderWidth: 1, borderStyle: 'dashed', borderColor: c.primary, alignItems: 'center', justifyContent: 'center', gap: 9, padding: 20 },
  emptyTitle: { color: c.foreground, fontFamily: 'InstrumentSerif_400Regular', fontSize: 23 },
  photo: { width: '100%', height: 240, borderWidth: 1, borderColor: c.border },
  buttons: { marginTop: 16, gap: 10 },
  action: { minHeight: 50, backgroundColor: c.primary, borderColor: c.primary, borderWidth: 1, flexDirection: 'row', gap: 10, alignItems: 'center', justifyContent: 'center', padding: 10, marginTop: 10 },
  secondary: { backgroundColor: 'transparent' },
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