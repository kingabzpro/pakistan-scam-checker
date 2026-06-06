# Research Notes: Pakistan Scam & Fraud Message Patterns

## Overview

This document summarizes publicly available research on scam, fraud, and confusing official-looking messages targeting Pakistani citizens. Sources include public advisories from PTA, FIA, FBR, State Bank of Pakistan, bank social media pages, Reddit discussions, and cybersecurity reports.

**Goal:** Build a local dataset of 50+ safe, anonymized examples for the "Pakistan Notice Helper" hackathon app.

---

## 1. FBR (Federal Board of Revenue) Scams

### Pattern: Fake Tax Notices & Refund Scams
- **Source:** FBR official website (fbr.gov.pk/beware-fradulant-sms)
- **Description:** Scammers send SMS claiming to be from FBR, offering tax refunds or threatening penalties. They ask victims to call a mobile number and disclose bank account details.
- **Red flags:** FBR never sends SMS to obtain banking information; messages ask for bank details; urgency language
- **Example text:** "Dear Taxpayer, your refund of Rs. XX,XXX is pending. Call [number] to claim."
- **Official advisory:** FBR warns taxpayers never to share banking info via SMS/email

### Pattern: Fake Income Tax Return Filing Reminders
- **Source:** Reddit r/pakistan
- **Description:** Users report receiving SMS about filing income tax returns that look official but contain suspicious links
- **Red flags:** Links to non-official domains, pressure to act immediately

### Pattern: Fake Invoices/Receipts
- **Source:** FBR Facebook page (Oct 2024)
- **Description:** FBR warns about fake invoices circulating; encourages using TaxAsaan App to verify receipts via QR codes
- **Red flags:** Receipts that cannot be verified through official app

---

## 2. Bank Scams (HBL, UBL, Meezan, Bank Alfalah, etc.)

### Pattern: Fake Reward Points
- **Source:** HBL official Facebook page
- **Description:** Scammers send SMS claiming reward points are about to expire, with a link to "redeem" them
- **Red flags:** Suspicious links, banks never ask for sensitive info via SMS/calls/emails
- **Example text:** "Dear HBL customer, your 5000 reward points expire today! Redeem now: [link]"

### Pattern: Account Blocking/KYC Update
- **Source:** Meezan Bank Facebook page
- **Description:** Messages claiming account will be blocked unless KYC is updated immediately
- **Red flags:** Urgency, links to non-bank domains, requests for personal/financial details
- **Example text:** "Your account will be blocked in 24 hours. Update KYC: [link]"

### Pattern: Fake Fraud Alerts
- **Source:** Aura.com analysis, HBL advisories
- **Description:** Scammers send fake "fraud alert" messages asking customers to verify transactions
- **Red flags:** Requests to transfer money to "stop fraud", messages from unknown numbers

### Pattern: Bank Impersonation Calls
- **Source:** Instagram (HBL scam alert)
- **Description:** Fraudsters call posing as bank officials, trick people into transferring funds via mobile app
- **Red flags:** Calls from non-bank numbers, pressure to act immediately

---

## 3. Mobile Wallet Scams (Easypaisa, JazzCash)

### Pattern: Fake Payment Confirmation
- **Source:** Reddit r/PakistaniTech, YouTube
- **Description:** Scammer sends fake payment screenshot claiming money was sent "by mistake" and asks for refund
- **Red flags:** Payment not actually received, pressure to return money quickly
- **Example text:** "Maine galti se 5000 bhej diye hain aap ko. Please wapas kar dein."

### Pattern: "Mistaken Transfer" Call
- **Source:** Reddit (JazzCash employee account)
- **Description:** Caller claims they accidentally sent money to victim's account and wants it back
- **Red flags:** Actual balance doesn't match claimed amount, requests to send to different account
- **Notable:** JazzCash employee reported disabling 7 scam wallets in one session

### Pattern: Account Verification Scam
- **Source:** Reddit r/PakistaniTech
- **Description:** Call from number appearing as "+1950" claiming unauthorized transactions on JazzCash account
- **Red flags:** International-looking numbers, requests for account details

### Pattern: SBP Cooling Period Exploitation
- **Source:** Reddit r/PakistaniTech
- **Description:** State Bank introduced 2-hour hold on transfers to prevent fraud; scammers try to exploit this window
- **Context:** Legitimate policy to protect users

---

## 4. PTA & FIA Impersonation

### Pattern: PTA SIM Verification/Blocking
- **Source:** PTA Facebook page, PTA website
- **Description:** Messages claiming PTA will block SIM/phone unless verification is completed via a link
- **Red flags:** PTA never asks for personal details via SMS; suspicious links
- **Example text:** "PTA Alert: Your SIM will be blocked. Verify now: [link]"
- **Official advisory:** PTA warns citizens never to click suspicious links or share personal details

### Pattern: FIA Cyber Crime Threat Messages
- **Source:** Dawn.com (FIA warning)
- **Description:** Fake messages using FIA name and DG FIA position, with "Top Secret" stamp, accusing victims of cyber crimes
- **Red flags:** WhatsApp/email messages (FIA doesn't send these), blackmail attempts, fake stamps
- **Example text:** "FIA has detected illegal activity from your device. Contact immediately or face arrest."
- **Official statement:** "The FIA does not send such messages to any individual through WhatsApp or email"

### Pattern: WhatsApp Account Hijacking via OTP Scam
- **Source:** National CERT Pakistan advisory, LinkedIn, multiple sources
- **Description:** Attacker poses as trusted contact or WhatsApp support, requests 6-digit verification code
- **Methods:** Social engineering (OTP request), call forwarding exploits (USSD codes), phishing links
- **Red flags:** Request for verification code, messages from "new number claiming to be friend"
- **Official advisory:** National CERT issued detailed advisory (NCA-01.011226)

---

## 5. Courier & Customs Scams

### Pattern: Fake Delivery Notifications
- **Source:** PTA Instagram/Facebook, Group-IB research
- **Description:** SMS claiming package delivery failed, asking to click link to update address or pay fees
- **Red flags:** Sender ID spoofing, urgency, requests for "handling fees" or "taxes"
- **Example text:** "Your parcel could not be delivered. Update address: [link]"
- **Technical detail:** Scammers use SMS gateway sender ID spoofing to merge with legitimate message threads

### Pattern: Fake Customs Duty Payment
- **Source:** Facebook groups (Voice of Customer PK)
- **Description:** Messages claiming customs duty must be paid before package release
- **Red flags:** Links to payment portals, requests for advance payment

### Pattern: Parcel Content Replacement
- **Source:** Facebook groups
- **Description:** Riders from various courier companies allegedly replacing package contents
- **Context:** Reported with Daraz, TCS, Pakistan Post, Daewoo, Leopards

---

## 6. E-Challan & Traffic Fine Scams

### Pattern: Fake E-Challan SMS
- **Source:** Facebook (Cars of Pak), Reddit r/pakistan, multiple news sources
- **Description:** SMS claiming traffic violation with link to pay fine online
- **Red flags:** Links not from official PSCA (9915) or Safe City Authority, urgent payment requests
- **Example text:** "Traffic police: Your vehicle has an overdue challan. Pay now: [link]"
- **Official advisory:** PSCA e-challan messages come only from 9915; Islamabad Police warned about fake pop-ups

### Pattern: Motorway Phishing Pop-ups
- **Source:** Instagram
- **Description:** Fake pop-ups claiming unpaid motorway tolls/challans
- **Red flags:** Pop-up format, requests for payment details

---

## 7. Utility Bill Scams

### Pattern: Electricity Disconnection Threat
- **Source:** Connected Pakistan (Power Division warning), Facebook
- **Description:** Messages claiming power will be disconnected in 30 minutes unless bill is paid immediately
- **Red flags:** Extreme urgency, personal payment links, QR codes
- **Example text:** "K-Electric Alert: Your electricity will be disconnected in 30 minutes. Pay now: [link]"
- **Context:** Pakistan's Power Division issued warning after hackers reportedly created fake QR codes on bills

### Pattern: Fake Gas/Water Bill Links
- **Source:** SNGC/LESCO advisories
- **Description:** Messages with links to pay overdue utility bills
- **Red flags:** Links to non-official domains, requests for immediate payment

---

## 8. Prize, Lottery & Refund Scams

### Pattern: Congratulations Winner Messages
- **Source:** PTA Facebook, HBL Facebook, Soneri Bank Facebook
- **Description:** Messages/calls claiming you've won a prize in a lottery you never entered
- **Red flags:** You didn't enter any lottery, requests for "processing fees" or "taxes"
- **Example text:** "Congratulations! You have won Rs. 500,000 in lucky draw. Send Rs. 2,000 processing fee to claim."

### Pattern: Fake Tax Refund
- **Source:** FBR advisory
- **Description:** Messages claiming FBR has a tax refund ready, need bank details to process
- **Red flags:** FBR never asks for banking info via SMS

### Pattern: Fake Cashback/Reward
- **Source:** Various bank advisories
- **Description:** Messages offering cashback or rewards for clicking links
- **Red flags:** Too-good-to-be-true offers, suspicious links

---

## 9. Job & Employment Scams

### Pattern: WhatsApp Job Offers (Daraz/company impersonation)
- **Source:** LinkedIn, Facebook groups
- **Description:** WhatsApp messages offering part-time jobs with daily earnings of Rs. 25,000-68,000
- **Red flags:** Unsolicited offers, requests to join Telegram groups, "add products to wishlist" tasks
- **Example text:** "Congratulations! You have been selected for online employee position. Daily salary Rs. 25,000-68,000. Contact recruiter on WhatsApp."
- **Modus operandi:** Start with small payments (Rs. 100 per task) to build trust, then ask for "investment"

### Pattern: Fake Overseas Job Ads
- **Source:** ICMPD research
- **Description:** Fraudulent job ads on Facebook/WhatsApp/Instagram for Gulf countries
- **Red flags:** Requests for upfront fees, "car registration" or "insurance" charges
- **Context:** Pakistan has 9M+ workers who migrated between 2011-2024

### Pattern: Recruitment Scam (Lahore-based)
- **Source:** LinkedIn
- **Description:** Scammers create professional-looking fake job listings, conduct fake interviews
- **Red flags:** Vague job details, pressure to complete "new hire paperwork" before meeting employer

---

## 10. University & Education Scams

### Pattern: Fake HEC Scholarship Announcements
- **Source:** HEC Pakistan Facebook page
- **Description:** Fake scholarship announcements asking for money to secure spots
- **Red flags:** HEC warns that anyone demanding money for scholarships is fake/fraud

### Pattern: Fake University Admissions
- **Source:** BBC News, Inside Higher Ed
- **Description:** AI-generated fake university websites designed to steal money and personal data
- **Context:** Axact scandal (2015) - Pakistan's largest fake degree operation

---

## 11. Account Blocking & Verification Scams

### Pattern: WhatsApp Account Blocking
- **Source:** PTA Facebook, Express News
- **Description:** Messages claiming WhatsApp account will be blocked on fake/inactive numbers
- **Red flags:** Links to verify account, requests for personal information

### Pattern: NADRA/CNIC Verification
- **Source:** Facebook (Aniqa Nisar)
- **Description:** Calls claiming to be from NADRA/Army/FIA asking for OTP to "unblock" account
- **Red flags:** "NADRA, Army, or FIA NEVER call you via WhatsApp"
- **Example text:** "Your CNIC has been blocked. Share the OTP code to verify your identity."

### Pattern: SIM Blocking Threats
- **Source:** PTA advisories
- **Description:** Messages threatening SIM blockage unless action is taken
- **Red flags:** PTA official channels don't send such messages

---

## 12. General Red Flags (Cross-Category)

1. **Urgency:** "Act now", "24 hours", "immediately", "or else..."
2. **Requests for personal info:** Bank details, CNIC, OTP codes, passwords
3. **Suspicious links:** Non-official domains, URL shorteners, misspelled domains
4. **Threats:** Account blocking, service disconnection, legal action
5. **Too-good-to-be-true:** Prizes, refunds, job offers with high pay
6. **Sender mismatch:** Messages from personal numbers claiming to be organizations
7. **Grammar/spelling errors:** Common in phishing messages
8. **Requests to call unknown numbers:** Especially mobile numbers for "official" matters
9. **Requests to transfer money:** "Return" mistaken transfers, pay "fees" to claim prizes
10. **Pressure to bypass security:** "Ignore warnings", "don't tell anyone"

---

## Official Reporting Channels

| Organization | Channel | Contact |
|---|---|---|
| PTA | Complaint portal | complaints.pta.gov.pk |
| FIA/NCCIA | Cyber crime helpline | 1991 |
| SBP | Banking complaints | 021-111-727-727 |
| FBR | Tax fraud | fbr.gov.pk |
| National CERT | pkcert.gov.pk | pkcert.gov.pk |

---

## Sources Used

1. FBR Official Website - Beware of Fraudulent SMS advisory
2. PTA Facebook/Instagram - Multiple scam warnings
3. HBL Facebook - Fake Reward Point Scam warning
4. Meezan Bank Facebook - Impersonation fraud warning
5. UBL Facebook - Prize scam awareness
6. Dawn.com - FIA warns against fake messages
7. Reddit r/pakistan - FBR SMS, e-challan scam discussions
8. Reddit r/PakistaniTech - Easypaisa/JazzCash scam reports
9. National CERT Pakistan - WhatsApp hijacking advisory (NCA-01.011226)
10. Connected Pakistan - Power Division warning about QR codes
11. Facebook groups (Voice of Customer PK) - Courier scam reports
12. Cars of Pak Facebook - E-challan scam alert
13. LinkedIn - Job scam reports, WhatsApp hacking analysis
14. Group-IB - Fake shipment tracking scam research
15. ICMPD - Fake job ads research
16. HEC Pakistan Facebook - Fake scholarship warnings
17. BBC News - Axact fake degree scandal
18. Soneri Bank Facebook - Lottery scam warning
19. CyberPeace - E-challan scam advisory
20. FBR Facebook - Fake invoices/receipts warning

---

## Notes on Data Privacy

- All examples in the dataset are anonymized
- Phone numbers, CNIC numbers, account numbers, addresses are masked
- No personal data from private individuals is stored
- Examples are recreated based on public patterns, not copied verbatim from private messages
- Source URLs are included only for public advisories and official pages

---

## Publicly Available Scam Advisory Images

These images are from official advisories and are publicly shared for awareness purposes. They have been downloaded to `sample_inputs/` for reference.

### E-Challan Scam Advisory (Associated Press of Pakistan)
- **Source:** APP.com.pk - CTO Islamabad advisory (Sep 2025)
- **Image 1:** `sample_inputs/echallan_scam_advisory_app.jpeg`
  - URL: https://www.app.com.pk/wp-content/uploads/2025/09/7c3a2991-d26f-4d2f-bc26-cc69b1707237.jpeg
- **Image 2:** `sample_inputs/echallan_scam_advisory_detail.jpeg`
  - URL: https://www.app.com.pk/wp-content/uploads/2025/09/ce896b99-e57d-419d-814c-c022ddadb1ea.jpeg

### Pakistan Post Fake SMS (Resecurity Research)
- **Source:** Resecurity - Smishing Triad targeting Pakistan
- **Image 1:** `sample_inputs/pakistan_post_fake_sms_resecurity.jpeg`
  - URL: https://www.resecurity.com/uploads/post/331/a900a7a910364a6ba3a9a15524e32886.jpeg
  - Description: Fake SMS claiming package cannot be delivered due to incorrect address
- **Image 2:** `sample_inputs/pakistan_post_fake_sms_2_resecurity.png`
  - URL: https://www.resecurity.com/uploads/post/331/4ef4601adbde0a5ec50e4453a3ac0df5.png
  - Description: Fake Pakistan Post SMS with suspicious link

### Additional Public Image References (Not Downloaded - For Reference Only)

#### E-Challan Scam Images (Instagram/Facebook)
- PSCA Official Warning: https://www.instagram.com/reel/DV0dOC7ADYf
  - Description: Official PSCA warning about fake e-challan SMS from non-9915 numbers
- Punjab Safe Cities: https://www.facebook.com/punjabsafecities/posts/1146666947636867
  - Description: E-challan scam alert with example messages

#### Bank Scam Images (Facebook)
- HBL Fake Reward Points: https://www.facebook.com/HBLBank/posts/1300972745547014
  - Description: HBL warning about fake reward point SMS scams
- Meezan Bank Impersonation: https://www.facebook.com/MeezanBank/posts/1404461508375967
  - Description: Warning about fraudsters impersonating Meezan Bank

#### Courier Scam Images (NCERT Advisory)
- NCERT Advisory PDF: https://pkcert.gov.pk/advisory/24-11.pdf
  - Description: Contains examples of fake Pakistan Post SMS and counterfeit websites
- TCS Scam Alert: https://www.facebook.com/tcscouriers/posts/1146049587565703
  - Description: TCS warning about fake SMS and WhatsApp messages

#### PTA Advisories
- PTA Phishing Warning: https://www.facebook.com/PTAOfficialPK/posts/1306871771606204
  - Description: PTA warning about phishing scams
- PTA Fake Courier Warning: https://www.pta.gov.pk/category/beware-of-fake-courier-messages-1528511679-2025-07-28
  - Description: Official PTA advisory about fake courier messages

#### WhatsApp Hijacking (National CERT)
- CERT Advisory: https://pkcert.gov.pk/advisory/26/1.pdf
  - Description: Detailed advisory on WhatsApp account hijacking methods including OTP scams, call forwarding exploits, and phishing links

### Image Dataset (Updated)
The `data/examples.jsonl` file now contains 27 image-based examples with the following structure:
- `image`: Path to the screenshot in `sample_inputs/`
- `category`: traffic_challan, courier, FBR, bank, wallet, unknown
- `risk_label`: Likely scam, Suspicious, Verify first, Looks normal
- `source_type`: reddit, official_advisory, other
- `source_url`: Public URL where the image was found
- `description`: What the screenshot shows
- `red_flags`: Array of warning signs visible in the image

### Image Categories in Dataset
- **E-Challan Scams (3 images)**: Fake traffic fine SMS from non-9915 numbers
- **Courier Scams (18 images)**: Pakistan Post, TCS, Leopards fake delivery SMS
- **Bank Scams (3 images)**: HBL, generic bank fraud alerts
- **FBR Tax Scams (2 images)**: Fake tax refund messages
- **WhatsApp Scams (1 image)**: Verification code request scam

### Image Usage Notes
- All downloaded images are from official government advisories, security research reports, and public Reddit/social media posts
- These are shared publicly for awareness and educational purposes
- No private or personal data is included in these images
- Images show real scam patterns that Pakistani citizens encounter daily
- For the hackathon app, use these as training data for scam detection
