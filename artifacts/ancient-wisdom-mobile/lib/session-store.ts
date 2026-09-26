import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

export type SavedSession = { token: string; userId: string; accepted: boolean };
const key = 'ancient-wisdom-mobile-session';
const deviceKey = 'ancient-wisdom-device-credential';

export async function loadDeviceCredential(): Promise<string | null> {
  return Platform.OS === 'web' ? localStorage.getItem(deviceKey) : SecureStore.getItemAsync(deviceKey);
}

export async function saveDeviceCredential(value: string): Promise<void> {
  if (Platform.OS === 'web') localStorage.setItem(deviceKey, value);
  else await SecureStore.setItemAsync(deviceKey, value);
}

export async function loadSession(): Promise<SavedSession | null> {
  const value = Platform.OS === 'web' ? sessionStorage.getItem(key) : await SecureStore.getItemAsync(key);
  if (!value) return null;
  try {
    const parsed = JSON.parse(value) as SavedSession;
    if (typeof parsed.token === 'string' && typeof parsed.userId === 'string') return parsed;
  } catch { /* Invalid or old state must not authorize analysis. */ }
  return null;
}

export async function saveSession(value: SavedSession | null): Promise<void> {
  if (Platform.OS === 'web') {
    if (value) sessionStorage.setItem(key, JSON.stringify(value));
    else sessionStorage.removeItem(key);
  } else if (value) {
    await SecureStore.setItemAsync(key, JSON.stringify(value));
  } else {
    await SecureStore.deleteItemAsync(key);
  }
}