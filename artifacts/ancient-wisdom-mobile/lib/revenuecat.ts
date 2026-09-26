import { Platform } from 'react-native';
import Constants from 'expo-constants';
import Purchases, { LOG_LEVEL, type PurchasesPackage } from 'react-native-purchases';

let configured = false;
let currentUser = '';

function apiKey(): string {
  const key = __DEV__ || Platform.OS === 'web' || Constants.executionEnvironment === 'storeClient'
    ? process.env.EXPO_PUBLIC_REVENUECAT_TEST_API_KEY
    : Platform.OS === 'ios'
      ? process.env.EXPO_PUBLIC_REVENUECAT_IOS_API_KEY
      : process.env.EXPO_PUBLIC_REVENUECAT_ANDROID_API_KEY;
  if (!key) throw new Error('Purchases are not configured on this device.');
  return key;
}

export async function loginForReport(userId: string) {
  if (!configured) {
    Purchases.setLogLevel(__DEV__ ? LOG_LEVEL.DEBUG : LOG_LEVEL.ERROR);
    Purchases.configure({ apiKey: apiKey() });
    configured = true;
  }
  if (currentUser !== userId) {
    await Purchases.logIn(userId);
    currentUser = userId;
  }
}

export async function availableReport(): Promise<PurchasesPackage | null> {
  const offerings = await Purchases.getOfferings();
  return offerings.current?.availablePackages.find(p => p.product.identifier === 'ancient_wisdom_report') ?? null;
}

export async function buyReport(reportPackage: PurchasesPackage) {
  return Purchases.purchasePackage(reportPackage);
}

export async function restoreReportPurchases() {
  return Purchases.restorePurchases();
}