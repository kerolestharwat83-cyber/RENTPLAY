# RENTPLAY v2.0 - الدليل الشامل للرفع على GitHub + DigitalOcean

> هذا الدليل مخصص للرفع من المتصفح فقط - لا تحتاج تثبيت Git

---

## الجزء الأول: رفع المشروع على GitHub (من المتصفح)

### الخطوة 1: إنشاء حساب GitHub
1. افتح المتصفح وروح على: https://github.com
2. اضغط "Sign up" وسجل بحساب جديد (البريد + باسورد)
3. أكد بريدك الإلكتروني

### الخطوة 2: إنشاء مستودع جديد (Repository)
1. بعد تسجيل الدخول، اضغط الزر الأخضر **"New"** أو **"+"** فوق
2. اكتب اسم المستودع: `rentplay`
3. اختر **"Public"** (أو Private لو عايز)
4. اضغط **"Create repository"**

### الخطوة 3: رفع الملفات من المتصفح
1. هتفتح صفحة المستودع الجديد
2. اضغط على **"uploading an existing file"**
3. هيفتحلك صفحة رفع الملفات
4. افتح مجلد `rentplay_v2.0/project/` على جهازك
5. حدد كل الملفات والمجلدات (config, rentplay, templates, static, manage.py, requirements.txt, Dockerfile, run.bat, init_demo_data.py, README.md)
6. اسحبهم حطهم في صفحة GitHub أو اضغط **"choose your files"** واختارهم
7. تحت اكتب في "Commit changes": `Initial upload of RENTPLAY v2.0`
8. اضغط **"Commit changes"**

> ملاحظة: لو الملفات كتير، ارفعها على دفعات (config الأول، بعدين rentplay، بعدين templates، بعدين static، بعدين الباقي)

---

## الجزء الثاني: ربط DigitalOcean Spaces (للصور والملفات)

### القصة:
في الكود القديم كان فيه مفاتيح DigitalOcean مكشوفة:
```
DO00BF3GCRAV4KGEY3XU
0dx1tEOOKHFQ8UdLrcIfRzXmdsDPTkkbCBPD8C9WwhQ
rentplay-media
https://fra1.digitaloceanspaces.com
```

أنا شلتها من الكود في v2.0 وعملتها تتقرأ من "متغيرات البيئة" (Environment Variables).

### الخطوة 1: الدخول على DigitalOcean
1. روح على: https://cloud.digitalocean.com
2. سجل دخول بحسابك

### الخطوة 2: إنشاء Spaces (مخزن الصور)
1. من القائمة الجانبية، اضغط على **"Spaces"** (أو **"Spaces Object Storage"**)
2. اضغط **"Create a Space"**
3. اختار المنطقة: **Frankfurt (fra1)** (أو اي منطقة قريبة)
4. اكتب اسم فريد للمخزن: `rentplay-media` (أو أي اسم تاني)
5. اختر **"Restrict File Listing"** (للأمان)
6. اضغط **"Create a Space"**

### الخطوة 3: إنشاء API Key
1. اضغط على صورتك فوق يمين ← **"API"**
2. روح على تبويب **"Spaces Access Keys"**
3. اضغط **"Generate New Key"**
4. اكتب اسم: `rentplay-app`
5. اضغط **"Create Access Key"**
6. هتظهرلك مفتاحين:
   - **Key**: (مثلاً: `DO00XXXXXX...`) ← انسخه
   - **Secret**: (مثلاً: `xxxxxxxx...`) ← انسخه برضه
   
> ⚠️ ملاحظة مهمة: السيكريت هيختفي بعد ما تسكر الصفحة! انسخه وحطه في ملف تكست عندك

### الخطوة 4: إعداد CORS (عشان الموقع يقدر يوصل للصور)
1. افتح الـ Space اللي انشأته
2. اضغط على **"Settings"**
3. روح على **"CORS Configurations"**
4. اضغط **"Add"**
5. في حقل "Origin": اكتب رابط موقعك (هناخده من DigitalOcean App Platform بعدين)
6. في "Allowed Methods": حدد GET, POST, PUT, DELETE
7. اضغط **"Save Options"**

---

## الجزء الثالث: رفع الموقع على DigitalOcean App Platform

### الخطوة 1: الدخول على App Platform
1. روح على: https://cloud.digitalocean.com
2. من القائمة الجانبية، اضغط **"App Platform"**
3. اضغط **"Create App"** (أو **"Launch Your App"**)

### الخطوة 2: ربط GitHub
1. اختر **"GitHub"** كمصدر
2. هيفتحلك نافذة تربط GitHub بـ DigitalOcean - اضغط **"Authorize"**
3. اختار المستودع: `rentplay`
4. اختتر الفرع: `main` أو `master`
5. اضغط **"Next"**

### الخطوة 3: إعدادات التطبيق
1. **Type**: اختار **"Web Service"**
2. **Build Command**: سيبه فاضي أو اكتب:
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
3. **Run Command**: غيره لـ:
   ```
   gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 config.wsgi:application
   ```
4. اضغط **"Next"**

### الخطوة 4: اختيار الباقة
1. اختار **"Basic"** (تكفي للبداية)
2. اختار الحجم: **512 MB RAM / 1 CPU** (تكفي)
3. اضغط **"Next"**

### الخطوة 5: إضافة Environment Variables (متغيرات البيئة) - مهم جداً!

هنا هنضيف كل الإعدادات السرية. اضغط **"Edit"** عند "Environment Variables" وضف المتغيرات دي:

| المتغير | القيمة |
|---------|--------|
| `DJANGO_SECRET_KEY` | `django-insecure-change-me-in-production-7a8b9c0d1e2f3g4h` (غيرها لأي نص عشوائي طويل) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `YOUR_APP_NAME.ondigitalocean.app` (هناخده بعدين) |
| `CSRF_TRUSTED_ORIGINS` | `https://YOUR_APP_NAME.ondigitalocean.app` |
| `DATABASE_URL` | `sqlite:///db.sqlite3` (مؤقتاً - SQLite) |
| `ADMIN_URL` | `a7x9k2m1` (أو أي نص عشوائي لإخفاء لوحة التحكم) |
| `DO_SPACES_KEY` | المفتاح اللي نسخته من Spaces (DO00XXXX...) |
| `DO_SPACES_SECRET` | السيكريت اللي نسخته |
| `DO_SPACES_BUCKET` | اسم الـ Space (مثلاً: `rentplay-media`) |
| `DO_SPACES_ENDPOINT` | `https://fra1.digitaloceanpaces.com` (حسب منطقتك) |

> ⚠️ لو مش حابب تربط Spaces دلوقتي، سيب `DO_SPACES_KEY` و `DO_SPACES_SECRET` فاضيين وهيشتغل على التخزين المحلي.

### الخطوة 6: إطلاق التطبيق
1. اضغط **"Launch App"** أو **"Create Resources"**
2. انتظر 5-10 دقايق لحد ما يبني وينشر
3. هتاخد رابط الموقع (مثلاً: `https://rentplay-xxx.ondigitalocean.app`)

### الخطوة 7: إنشاء Super Admin
1. من صفحة التطبيق في DigitalOcean، اضغط **"Console"**
2. اكتب الأوامر دي واحدة واحدة:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. اكتب يوزر: `admin`
4. اكتب بريد: `admin@rentplay.sa`
5. اكتب باسورد: `admin123` (وأكده)
6. بعدين:
   ```bash
   python manage.py init_demo_data
   ```

### الخطوة 8: تحديث ALLOWED_HOSTS
1. روح **"Settings"** → **"App-Level Environment Variables"**
2. عدل `ALLOWED_HOSTS` واكتب الرابط الفعلي بتاعك
3. عدل `CSRF_TRUSTED_ORIGINS` برضه
4. اضغط **"Save"** - هيعيد النشر أوتوماتيك

---

## الجزء الرابع: الدخول على لوحة التحكم

لوحة التحكم مخفية عشان الأمان. الرابط بيكون:
```
https://YOUR_APP_NAME.ondigitalocean.app/a7x9k2m1/
```

> غير `a7x9k2m1` للقيمة اللي حطيتها في `ADMIN_URL`

سجل دخول بالـ `admin` / `admin123` اللي عملتهم.

---

## الجزء الخامس: لو حابب تربط قاعدة بيانات PostgreSQL (موصى بيه)

### إنشاء قاعدة بيانات
1. من DigitalOcean dashboard، اضغط **"Databases"**
2. اضغط **"Create Database Cluster"**
3. اختار **PostgreSQL** - اختار **15** - اختار أقل باقة
4. اختار نفس منطقة التطبيق (Frankfurt)
5. اضغط **"Create a Database Cluster"**
6. انتظر 5 دقايق لحد ما تكون جاهزة
7. افتح الـ Database Cluster
8. روح على **"Users & Databases"**
9. اضغط **"Add New Database"** واكتب اسم: `rentplay`
10. روح على **"Connection Details"**
11. انسخ الـ "Connection String" (المعروف بـ "URI")
    - هيكون شكله: `postgres://doadmin:password@host:25060/rentplay?sslmode=require`

### ربط قاعدة البيانات بالتطبيق
1. روح على App Platform → تطبيقك → Settings
2. عدل `DATABASE_URL` واكتب الـ Connection String اللي نسخته
3. احذف ملف `db.sqlite3` لو موجود (من Console اكتب: `rm db.sqlite3`)
4. في Console اكتب:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py init_demo_data
   ```

---

## الجزء السادس: تحديث مستمر (بعد التعديلات)

### لو عدلت ملف على جهازك وعايز ترفعه:

#### الطريقة 1: من GitHub مباشرة (أسهل)
1. روح على مستودعك في GitHub
2. اضغط على الملف اللي عايز تعدله
3. اضغط **"Edit"** (أيقونة القلم ✏️)
4. عدل الكود
5. تحت اكتب وصف: `Update filename.py`
6. اضغط **"Commit changes"**
7. DigitalOcean هيشوف التعديل ويعيد النشر أوتوماتيك!

#### الطريقة 2: رفع ملف جديد
1. في صفحة المستودع، اضغط **"Add file"** → **"Upload files"**
2. ارفع الملف الجديد
3. اضغط **"Commit changes"**

#### الطريقة 3: إنشاء ملف جديد
1. اضغط **"Add file"** → **"Create new file"**
2. اكتب اسم الملف (مثلاً: `rentplay/new_file.py`)
3. اكتب الكود
4. اضغط **"Commit new file"**

> كل تعديل على GitBox هيفتح DigitalOcean App Platform يعيد النشر تلقائياً!

---

## ملخص سريع للروابط

| الخدمة | الرابط |
|--------|--------|
| GitHub | https://github.com |
| DigitalOcean Cloud | https://cloud.digitalocean.com |
| موقعك بعد الرفع | https://YOUR_APP_NAME.ondigitalocean.app |
| لوحة التحكم | https://YOUR_APP_NAME.ondigitalocean.app/a7x9k2m1/ |
| API | https://YOUR_APP_NAME.ondigitalocean.app/api/properties/ |
| Sitemap | https://YOUR_APP_NAME.ondigitalocean.app/sitemap.xml |

---

## ⚠️ نصائح أمان مهمة

1. **غير SECRET_KEY** لنص عشوائي طويل (50+ حرف)
2. **غير ADMIN_URL** لأي نص عشوائي (مش حد يعرفه)
3. **متنشرش** `DO_SPACES_SECRET` مع حد
4. **اعمل disable** لحساب `admin` بعد ما تعمل حساب جديد Super Admin
5. **خل DEBUG = False** دايماً في الإنتاج
