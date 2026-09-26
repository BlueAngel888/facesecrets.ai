import { File, Paths } from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Platform } from 'react-native';

export type Analysis = Record<string, unknown> & { executive_summary?: string };
export type Page = { languages: Record<string, string>; translations: Record<string, string> };
export class ApiError extends Error {
  constructor(message: string, readonly status: number) { super(message); }
}

const host = process.env.EXPO_PUBLIC_DOMAIN;
const base = host ? `https://${host}/api` : '/api';

async function response<T>(res: Response): Promise<T> {
  if (res.ok) return res.json() as Promise<T>;
  const body = await res.json().catch(() => ({})) as { error?: string };
  throw new ApiError(body.error || `Request failed (${res.status})`, res.status);
}

async function authed<T>(path: string, token: string, method = 'GET', body?: FormData | object): Promise<T> {
  const multipart = body instanceof FormData;
  return response<T>(await fetch(`${base}/mobile/${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, ...(!multipart && body ? { 'Content-Type': 'application/json' } : {}) },
    body: multipart ? body : body ? JSON.stringify(body) : undefined,
  }));
}

export const mobileApi = {
  page: async (language: string) => response<Page>(await fetch(`${base}/page?lang=${encodeURIComponent(language)}`)),
  session: async (deviceToken?: string | null) => response<{ access_token: string; rc_app_user_id: string; device_token?: string }>(await fetch(`${base}/mobile/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(deviceToken ? { device_token: deviceToken } : {}),
  })),
  upload: (token: string, uri: string, language: string, type = 'image/jpeg') => {
    const form = new FormData();
    form.append('language', language);
    if (Platform.OS === 'web') {
      return fetch(uri).then(r => r.blob()).then(blob => {
        form.append('file', blob, 'portrait.jpg');
        return authed<{ success: boolean }>('upload', token, 'POST', form);
      });
    }
    form.append('file', { uri, name: 'portrait.jpg', type } as unknown as Blob);
    return authed<{ success: boolean }>('upload', token, 'POST', form);
  },
  promo: (token: string, promo_code: string) => authed<{ success: boolean; message?: string }>('promo', token, 'POST', { promo_code }),
  redeem: (token: string) => authed<{ success: boolean; message?: string }>('redeem', token, 'POST'),
  analyze: (token: string) => authed<{ analysis: Analysis; success: boolean }>('analyze', token, 'POST'),
  result: (token: string) => authed<{ analysis: Analysis }>('result', token),
  cancel: (token: string) => authed<{ success: boolean }>('cancel', token, 'POST'),
  shareReport: async (token: string) => {
    const res = await fetch(`${base}/mobile/report`, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) {
      const body = await res.json().catch(() => ({})) as { error?: string };
      throw new Error(body.error || 'Report unavailable');
    }
    const bytes = new Uint8Array(await res.arrayBuffer());
    if (Platform.OS === 'web') {
      const url = URL.createObjectURL(new Blob([bytes], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'ancient-wisdom-report.pdf';
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
    } else {
      const file = new File(Paths.cache, 'ancient-wisdom-report.pdf');
      file.write(bytes);
      try {
        if (!await Sharing.isAvailableAsync()) throw new Error('Sharing is unavailable on this device');
        await Sharing.shareAsync(file.uri, { mimeType: 'application/pdf', UTI: 'com.adobe.pdf' });
      } finally { if (file.exists) file.delete(); }
    }
  },
};