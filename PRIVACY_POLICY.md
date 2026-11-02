# Privacy Policy — Junior Doctor

**Last updated:** 2 November 2026

**Effective date:** 2 November 2026

---

## 1. Introduction

Junior Doctor ("the App", "we", "our") is a medical reference application intended for healthcare professionals and medical trainees. This Privacy Policy explains what information the App collects, how it is used, and how it is protected.

**We are committed to protecting your privacy.** The App is designed to work with minimal data collection and without accounts.

---

## 2. Information We Do NOT Collect

The App does **NOT** collect or transmit any of the following:

- Personal identifiers (name, email, phone number, address)
- Patient data or medical records
- Location data
- Device identifiers (IMEI, MAC address, advertising ID)
- Usage analytics or behavioral tracking
- Crash reports or diagnostic data sent to third parties
- Photos, contacts, calendar, or any files on your device
- Financial information or payment data

**The App does not require an account or login.**

---

## 3. Data Stored Locally on Your Device

All data you create in the App is stored **only on your device**, in the App's private storage directory. This data is never transmitted to us or any third party.

### 3.1 Data You Enter
- **Personal Notes:** Written by you. Stored locally in `notes.json`. Not transmitted.
- **Favorites:** Topics you mark with the heart icon. Stored locally in `favorites.json`. Not transmitted.
- **Settings:** Theme choice (light/dark) and welcome screen status. Stored locally in `settings.json`. Not transmitted.

### 3.2 Data Downloaded for Content Updates
- **Medical Content:** The App downloads JSON files from GitHub containing medical reference content. These are cached locally in `downloaded_data.json`.
- **Update Metadata:** The App tracks version information and downloaded topics for update purposes.

**No personal data is included in these files.**

### 3.3 Data Removal

You can delete all your data at any time by:
- Uninstalling the App (removes all local data permanently)
- Clearing App data in Android Settings → Apps → Junior Doctor → Storage → Clear data
- Using in-App options: Settings → Clear All Favorites; Notes → Delete individual notes

---

## 4. Network Activity

### 4.1 Content Updates from GitHub

The App downloads medical content from GitHub when:
- The App is opened (automatic, in background)
- You tap "Force Refresh" in Settings

**What is transmitted to GitHub:**
- Your IP address (standard for any HTTP request)
- User-agent string (identifies the App version)
- Requested file URLs

**What is NOT transmitted:**
- Any personal data
- Any notes or favorites
- Any device identifiers

GitHub's own privacy policy applies to these requests:  
https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement

### 4.2 External Links

The App contains a link to WhatsApp for contacting the developer. Tapping it opens WhatsApp (if installed) — WhatsApp's privacy policy applies.

---

## 5. Permissions Explained

The App requests the following Android permissions:

### 5.1 INTERNET
- **Purpose:** Download updated medical content from GitHub.
- **Used for:** Content updates only.
- **Not used for:** Analytics, tracking, or transmitting personal data.

### 5.2 WAKE_LOCK
- **Purpose:** Ensure content updates complete reliably even if the screen turns off during download.

**The App does not request any other permissions.**

---

## 6. Data Security

- **Local data:** Stored in the App's private sandbox (Android's `user_data_dir`), which is inaccessible to other apps.
- **Network traffic:** All requests use HTTPS with SSL certificate validation (via `certifi`).
- **No cloud storage:** We do not operate any server that receives or stores your data.

**No security system is 100% secure.** We recommend:
- Keeping your device locked with a PIN/biometric
- Not sharing your device with untrusted users if you store sensitive notes

---

## 7. Children's Privacy

The App is intended for healthcare professionals and medical trainees. It is **not directed at children under 13**.

We do not knowingly collect any data from children. If you are a parent/guardian and believe a child under 13 has used the App, please contact us — the App collects no data, but we will assist with any concerns.

---

## 8. Medical Disclaimer

**The App is a clinical reference tool for educational purposes only.** It does not provide medical advice, diagnosis, or treatment. All medical decisions must be made by qualified healthcare professionals using clinical judgment and local protocols.

See the in-App disclaimer for full details.

---

## 9. Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last updated" date.

**Significant changes** will be announced in the App (via an in-App announcement).

Continued use of the App after changes means you accept the updated policy.

---

## 10. Your Rights

Because the App does not collect personal data on any server, there is no personal data for us to access, modify, or delete. **You have full control over all data on your device.**

If you have concerns, you may contact us (see Section 11).

---

## 11. Contact

For questions, concerns, or reports about this Privacy Policy:

- **Email:** almnsob001@gmail.com
- **GitHub:** https://github.com/almnsob001-gif/junior_doctor_updater
- **WhatsApp (developer):** +967 774 602 007

We aim to respond within 7 days.

---

## 12. Legal Basis (GDPR — EU Users)

For users in the European Union, our legal basis for processing is:

- **Legitimate interest** (Article 6(1)(f) GDPR): Downloading content updates to keep the App functional and accurate.

**We do not process personal data** beyond what is technically necessary for content delivery (IP address during GitHub fetch, which is handled by GitHub, not us).

**You may contact us to exercise GDPR rights** (access, rectification, erasure, restriction, objection). Since we hold no personal data, most requests will be fulfilled by the fact that there is nothing to access or delete.

---

## 13. Summary (TL;DR)

| Question | Answer |
|---|---|
| Do you collect personal data? | ❌ No |
| Do you track me? | ❌ No |
| Do you use analytics? | ❌ No |
| Do you show ads? | ❌ No |
| Where is my data stored? | 📱 Only on my device |
| Can you see my notes? | ❌ No |
| Can you see my favorites? | ❌ No |
| Do you have a server? | ❌ No |
| Is my data backed up to your cloud? | ❌ No |

---

**Junior Doctor is a reference tool for healthcare professionals. It is not a medical device and does not provide medical advice.**

---

*This policy is effective as of the date stated above. By using the App, you acknowledge you have read and understood this Privacy Policy.*
