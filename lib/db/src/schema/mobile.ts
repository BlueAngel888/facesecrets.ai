import { bigint, index, integer, pgTable, text } from "drizzle-orm/pg-core";

// Mobile payment/session records share the managed PostgreSQL database with
// the workspace. The Flask API uses SQL directly; these definitions make the
// tables part of the standard development push and publish-time schema sync.
export const mobileDevices = pgTable("mobile_devices", {
  deviceTokenHash: text("device_token_hash").primaryKey(),
  rcAppUserId: text("rc_app_user_id").notNull().unique("mobile_devices_rc_app_user_id_key"),
  createdAt: bigint("created_at", { mode: "number" }).notNull(),
});

export const mobileSessions = pgTable("mobile_sessions", {
  tokenHash: text("token_hash").primaryKey(),
  expiresAt: bigint("expires_at", { mode: "number" }).notNull(),
  deviceTokenHash: text("device_token_hash").references(() => mobileDevices.deviceTokenHash),
  rcAppUserId: text("rc_app_user_id").notNull(),
  promoIssued: integer("promo_issued").notNull().default(0),
  uploadedFile: text("uploaded_file"),
  language: text("language"),
  grantExpiresAt: bigint("grant_expires_at", { mode: "number" }),
  grantIssued: integer("grant_issued").notNull().default(0),
  grantUsed: integer("grant_used").notNull().default(0),
  reportId: text("report_id"),
  analysisJson: text("analysis_json"),
}, (table) => [index("idx_mobile_sessions_expires_at").on(table.expiresAt)]);

export const mobilePurchaseRedemptions = pgTable("mobile_purchase_redemptions", {
  transactionId: text("transaction_id").primaryKey(),
  tokenHash: text("token_hash").notNull(),
  redeemedAt: bigint("redeemed_at", { mode: "number" }).notNull(),
});