# Firebase Firestore O'rnatish Qo'llanmasi

## 1. Firebase Project Yaratish

1. [Firebase Console](https://console.firebase.google.com/) ga kiring
2. "Add project" tugmasini bosing
3. Project nomini kiriting (masalan: `fath-unified-bot`)
4. Google Analytics ni yoqing yoki o'chiring (ixtiyoriy)
5. "Create project" tugmasini bosing

## 2. Firestore Database Yaratish

1. Firebase Console da "Firestore Database" bo'limiga kiring
2. "Create database" tugmasini bosing
3. "Start in production mode" ni tanlang
4. Location ni tanlang (masalan: `us-central1`)
5. "Enable" tugmasini bosing

## 3. Service Account Key Olish

1. Firebase Console da "Project Settings" ga kiring (⚙️ ikonka)
2. "Service accounts" tabiga o'ting
3. "Generate new private key" tugmasini bosing
4. JSON fayl yuklab olinadi
5. Bu faylni `firebase_credentials.json` nomi bilan bot papkasiga qo'ying

## 4. Firestore Security Rules

Firestore Database → Rules bo'limida quyidagi rules ni qo'ying:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection
    match /users/{userId} {
      allow read, write: if request.auth != null || request.resource.data.user_id == int(userId);
    }
    
    // Analyses collection
    match /analyses/{analysisId} {
      allow read, write: if request.auth != null;
    }
    
    // Licenses collection
    match /licenses/{licenseId} {
      allow read, write: if request.auth != null;
    }
    
    // Pricing plans collection
    match /pricing_plans/{planId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // Referrals collection
    match /referrals/{referralId} {
      allow read, write: if request.auth != null;
    }
    
    // Referral codes collection
    match /referral_codes/{codeId} {
      allow read, write: if request.auth != null;
    }
    
    // Economic data collection
    match /economic_data/{dataId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    
    // Insider news collection
    match /insider_news/{newsId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

**Eslatma:** Production uchun security rules ni qattiqroq qilish kerak. Yuqoridagi rules development uchun.

## 5. Botni Sozlash

1. `firebase_credentials.json` faylini bot papkasiga qo'ying
2. `config.py` faylida `USE_FIRESTORE = True` ni tekshiring
3. `config.py` faylida `FIREBASE_CREDENTIALS_PATH = "firebase_credentials.json"` ni tekshiring

## 6. Dependencies O'rnatish

```bash
pip install -r requirements.txt
```

## 7. Botni Ishga Tushirish

```bash
python main.py
```

Agar hamma narsa to'g'ri bo'lsa, terminalda quyidagi xabar ko'rinadi:
```
✅ Firestore database ishlatilmoqda
```

## 8. SQLite dan Firestore ga Migratsiya (Ixtiyoriy)

Agar eski SQLite ma'lumotlarini Firestore ga ko'chirmoqchi bo'lsangiz, migratsiya script yozish kerak.

## Xatoliklar

### Xatolik: `FileNotFoundError: firebase_credentials.json`
**Yechim:** `firebase_credentials.json` faylini bot papkasiga qo'ying.

### Xatolik: `Permission denied`
**Yechim:** Firestore Security Rules ni tekshiring va service account key to'g'ri ekanligini tekshiring.

### Xatolik: `Collection not found`
**Yechim:** Firestore da collections avtomatik yaratiladi. Birinchi marta ishlatganda avtomatik yaratiladi.

## SQLite ga Qaytish

Agar Firestore ishlamasa, `config.py` da:
```python
USE_FIRESTORE = False
```
qilib qo'ying. Bot SQLite ga qaytadi.

