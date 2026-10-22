import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Camera, Check, ChevronDown, CircleAlert, FileImage, LockKeyhole, RotateCcw, Sparkles, Upload, X } from "lucide-react";

const defaultLanguages = { en: "English", ro: "Română", de: "Deutsch", it: "Italiano", fr: "Français", es: "Español", zh: "中文", ar: "العربية", ja: "日本語" };

function postJSON(path, body) { return fetch(`/api${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include", body: JSON.stringify(body) }); }

export default function App({ page = "home", language: initialLanguage = "en", languages = defaultLanguages, translations = {}, analysis = null, error = "", navigate = url => window.location.assign(url) }) {
  const [language, setLanguage] = useState(initialLanguage);
  const [file, setFile] = useState(null), [preview, setPreview] = useState(""), [drag, setDrag] = useState(false);
  const [promo, setPromo] = useState(""), [promoState, setPromoState] = useState(""), [notice, setNotice] = useState("");
  const [stage, setStage] = useState("idle"), [progress, setProgress] = useState(0), [cameraOpen, setCameraOpen] = useState(false), [cameraError, setCameraError] = useState("");
  const inputRef = useRef(null), videoRef = useRef(null), streamRef = useRef(null), cameraRequestRef = useRef(0);
  const t = key => translations[`ui_${key}`] || key;
  const localizedError = message => {
    const known = {
      "No file uploaded": "choose_first", "No file selected": "choose_first",
      "Invalid image file": "bad_type", "Invalid file type": "bad_type",
      "Image must be smaller than 16 MB": "too_large",
      "Upload failed": "upload_failed", "Analysis failed": "analysis_failed",
      "Payment setup failed": "payment_failed",
      "Payment setup failed - no checkout URL": "payment_failed",
    };
    return t(known[message] || "error_detail");
  };
  const traditions = [1, 2, 3, 4, 5].map((number, index) => [
    String(index + 1).padStart(2, "0"), t(`tradition_${number}_title`), t(`tradition_${number}_desc`)
  ]);

  const stopCamera = () => { if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop()); streamRef.current = null; if (videoRef.current) videoRef.current.srcObject = null; };
  useEffect(() => () => { cameraRequestRef.current += 1; stopCamera(); }, []);
  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === "ar" ? "rtl" : "ltr";
    // Home pages keep the descriptive, localized <title> served in the HTML.
    if (page !== "home") document.title = t("brand");
  }, [language]);
  const validate = (candidate) => {
    if (!candidate) return;
    if (!["image/jpeg", "image/png", "image/gif"].includes(candidate.type)) return setNotice(t("bad_type"));
    if (candidate.size > 16 * 1024 * 1024) return setNotice(t("too_large"));
    setNotice(""); setFile(candidate); setPreview(URL.createObjectURL(candidate));
  };
  const upload = async () => {
    if (!file) return setNotice(t("choose_first"));
    setStage("upload"); setProgress(12); setNotice("");
    const data = new FormData(); data.append("file", file); data.append("language", language);
    try {
      const res = await fetch("/api/upload", { method: "POST", credentials: "include", body: data });
      const json = await res.json().catch(() => ({})); if (!res.ok) throw new Error(localizedError(json.error));
      setProgress(38); setStage("analysis");
      if (promoState === "accepted") {
        setProgress(57); const free = await fetch("/api/free-analysis", { method: "POST", credentials: "include" }); const result = await free.json().catch(() => ({}));
        if (!free.ok) throw new Error(localizedError(result.error));
        setProgress(100);
        navigate(result.redirect_url || "/success");
      } else {
        setProgress(62); const checkout = await fetch("/api/create-checkout-session", { method: "POST", credentials: "include", headers: { Accept: "application/json" } });
        const result = await checkout.json().catch(() => ({}));
        if (!checkout.ok || !result.checkout_url) throw new Error(localizedError(result.error));
        navigate(result.checkout_url);
      }
    } catch (error) { setNotice(localizedError(error.message)); setStage("error"); }
  };
  const checkPromo = async () => { if (!promo.trim()) return; setPromoState("checking"); try { const res = await postJSON("/check-promo-code", { promo_code: promo }); const json = await res.json(); setPromoState(json.success ? "accepted" : "invalid"); } catch { setPromoState("invalid"); } };
  const openCamera = async () => {
    setCameraOpen(true); setCameraError("");
    const request = ++cameraRequestRef.current;
    if (!navigator.mediaDevices?.getUserMedia) return setCameraError(t("camera_denied"));
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "user" } }, audio: false });
      if (request !== cameraRequestRef.current) return stream.getTracks().forEach(track => track.stop());
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch {
      if (request === cameraRequestRef.current) setCameraError(t("camera_denied"));
    }
  };
  const closeCamera = () => { cameraRequestRef.current += 1; stopCamera(); setCameraOpen(false); };
  const capture = () => { const video = videoRef.current; if (!video?.videoWidth) return setCameraError(t("camera_starting")); const canvas = document.createElement("canvas"); canvas.width = video.videoWidth; canvas.height = video.videoHeight; canvas.getContext("2d").drawImage(video, 0, 0); canvas.toBlob(blob => { if (blob) validate(new File([blob], "camera-portrait.jpg", { type: "image/jpeg" })); closeCamera(); }, "image/jpeg", .92); };
  const reset = () => { setStage("idle"); setProgress(0); setFile(null); setPreview(""); setNotice(""); setPromoState(""); setPromo(""); };
  if (page !== "home") return <StatusPage page={page} t={t} analysis={analysis} error={error} />;
  return <div className="shell" dir={language === "ar" ? "rtl" : "ltr"}><header className="container nav"><a className="brand" href="/"><span className="brand-mark">F</span> {t("brand")}</a><div className="nav-tools"><span className="mono">{t("private")}</span><select className="language" aria-label={t("language")} value={language} onChange={e => window.location.assign(e.target.value === "en" ? "/" : `/${e.target.value}/`)}>{Object.entries(languages).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></div></header>
    <main><section className="container hero"><motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .7 }}><div className="eyebrow">{t("hero_eyebrow")}</div><h1 className="serif">{t("title_before")}<em>{t("title_emphasis")}</em>{t("title_after")}</h1><p className="hero-copy">{t("subtitle")}</p><p className="hero-note">{t("hook")}</p></motion.div><motion.div className="scanner" initial={{ opacity: 0, scale: .96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: .9, delay: .15 }}><div className="eyebrow">{t("instrument")}</div><div className="orb"><span className="scanline" /></div><div className="scanner-caption"><span>{t("scanner_caption")}</span><span className="mono">{t("encrypted")}</span></div></motion.div></section>
      <section className="section"><div className="container"><div className="section-heading"><div className="eyebrow">{t("lenses_eyebrow")}</div><h2 className="serif">{t("lenses_title")}</h2><p>{t("lenses_intro")}</p></div><div className="traditions">{traditions.map(([n, title, desc]) => <article className="tradition" key={n}><span className="tradition-index mono">{n}</span><h3>{title}</h3><p>{desc}</p></article>)}</div></div></section>
      <section className="section" id="begin"><div className="container"><div className="section-heading"><div className="eyebrow">{t("session")}</div><h2 className="serif">{t("session_title")}</h2></div>{stage !== "idle" && stage !== "error" ? <Progress stage={stage} progress={progress} t={t} /> : <div className="workbench"><div className="card"><div className={`upload-zone ${drag ? "active" : ""}`} onDragOver={e => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={e => { e.preventDefault(); setDrag(false); validate(e.dataTransfer.files[0]); }} onClick={() => inputRef.current?.click()} role="button" tabIndex="0" onKeyDown={e => e.key === "Enter" && inputRef.current?.click()}><input ref={inputRef} type="file" accept="image/jpeg,image/png,image/gif" onChange={e => validate(e.target.files[0])} />{preview ? <img className="preview" src={preview} alt={t("preview_alt")} /> : <div><div className="upload-icon"><FileImage size={21} /></div><strong>{t("upload")}</strong><p className="hero-note">{t("file_help")}<br />{t("portrait_help")}</p></div>}</div><div className="actions"><button className="btn secondary" type="button" onClick={openCamera}><Camera size={16} /> {t("camera")}</button>{preview && <button className="btn secondary" type="button" onClick={() => { setFile(null); setPreview(""); }}>{t("remove")}</button>}</div></div><div className="card"><div className="eyebrow">{t("before")}</div><h3 className="serif" style={{ fontSize: 34, fontWeight: 400 }}>{t("clarity")}</h3><div className="quality"><div className="quality-item"><span className="dot" />{t("quality_1")}</div><div className="quality-item"><span className="dot" />{t("quality_2")}</div><div className="quality-item"><span className="dot" />{t("quality_3")}</div></div><div className="promo"><input aria-label={t("promo")} placeholder={t("promo")} value={promo} onChange={e => setPromo(e.target.value)} /><button className="btn secondary" type="button" onClick={checkPromo}>{t("check")}</button></div>{promoState === "accepted" && <div className="notice">{t("accepted")}</div>}{promoState === "invalid" && <div className="notice error">{t("invalid")}</div>}{notice && <div className="notice error"><CircleAlert size={15} /> {notice}</div>}<button className="btn" type="button" onClick={upload} style={{ width: "100%", marginTop: 22 }}>{promoState === "accepted" ? t("free") : `${t("analyze")} · ${t("price")}`}</button><p className="hero-note" style={{ marginTop: 18 }}><LockKeyhole size={13} /> {t("privacy")}</p></div></div>}</div></section></main>
    <footer className="container footer"><span>{t("footer")}</span><span className="mono">{t("footer_privacy")}</span></footer>
    <AnimatePresence>{cameraOpen && <motion.div className="dialog-backdrop" role="dialog" aria-modal="true" aria-label={t("camera_studio")} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onKeyDown={e => e.key === "Escape" && closeCamera()}><motion.div className="dialog" initial={{ y: 20 }} animate={{ y: 0 }}><div className="dialog-head"><div><div className="eyebrow">{t("camera_studio")}</div><h3 className="serif" style={{ fontSize: 30, margin: "8px 0 0" }}>{t("face_light")}</h3></div><button className="icon-btn" onClick={closeCamera} aria-label={t("close_camera")}><X /></button></div><div className="video-frame"><video className="video" ref={videoRef} autoPlay playsInline muted /><span className="camera-scan" /><div className="face-guide" /><div className="camera-quality"><span><i /> {t("lighting")}</span><span><i /> {t("position")}</span><span><i /> {t("distance")}</span></div></div>{cameraError ? <div className="notice error">{cameraError}</div> : <p className="hero-note">{t("camera_help")}</p>}<div className="actions"><button className="btn" onClick={capture} disabled={!!cameraError}><Camera size={16} /> {t("capture")}</button><button className="btn secondary" onClick={closeCamera}>{t("cancel_button")}</button></div></motion.div></motion.div>}</AnimatePresence>
  </div>;
}
function Progress({ stage, progress, t }) { return <motion.div className="progress-wrap" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><Sparkles color="var(--gold)" size={26} /><h3 className="serif" style={{ fontSize: 48, fontWeight: 400 }}>{t("processing")}</h3><p className="hero-copy" style={{ margin: "auto" }}>{stage === "upload" ? t("uploading") : t("comparing")}</p><div className="progress-line"><span style={{ width: `${progress}%` }} /></div><div className="stages"><div className={`stage ${stage === "upload" ? "active" : ""}`}><strong>01</strong>{t("stage_1")}</div><div className={`stage ${stage === "analysis" ? "active" : ""}`}><strong>02</strong>{t("stage_2")}</div><div className="stage"><strong>03</strong>{t("stage_3")}</div></div></motion.div>; }
function StatusPage({ page, t, analysis, error }) { const isSuccess = page === "success"; const isCancel = page === "cancel"; return <div className="shell"><header className="container nav"><a className="brand" href="/"><span className="brand-mark">F</span> {t("brand")}</a></header><main className="container result"><div><div className="eyebrow">{isSuccess ? t("complete") : isCancel ? t("checkout") : t("notice")}</div><h1 className="serif">{isSuccess ? t("success") : isCancel ? t("cancel") : t("error")}</h1><p>{isSuccess ? t("success_detail") : isCancel ? t("cancel_detail") : error || t("error_detail")}</p>{isSuccess && analysis?.executive_summary && <section className="report-preview"><div className="eyebrow">{t("summary")}</div><p>{analysis.executive_summary}</p></section>}<div className="actions" style={{ justifyContent: "center" }}>{isSuccess && <form method="post" action="/api/download-pdf"><button className="btn" type="submit"><Check size={16} /> {t("download")}</button></form>}{isCancel ? <form method="post" action="/api/cancel"><button className="btn secondary" type="submit"><RotateCcw size={16} /> {t("again")}</button></form> : <a className="btn secondary" href="/"><RotateCcw size={16} /> {t("again")}</a>}</div></div></main></div>; }
