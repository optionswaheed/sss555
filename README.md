# Options Technology — Dark Cyberpunk HUD Edition

تطبيق ويب كامل لشركة **أوبشنز تكنولوجي** بتصميم مستقبلي (Dark Cyberpunk / Sci-Fi HUD).

## المميزات

- **تصميم Dark Cyberpunk**: خلفية داكنة `#050714` + نيون Cyan/Purple/Red + خطوط شبكية + جزيئات مضيئة
- **شريط Telemetry** علوي (حالة النظام، Latency، التشفير)
- **Hero** مع عرض بصري تفاعلي (Server Core) وإحصائيات
- **خدمات** ببطاقات Glassmorphism
- **أداة التشخيص الذكي** التفاعلية (Terminal Output)
- **نموذج اتصال** بتصميم Terminal
- دعم **عربي/إنجليزي** + RTL
- **Chatbot** موسّع + دعم AI Model
- **لوحة تحكم Admin** كاملة

## التشغيل

```bash
cd options_tech_cyber
pip install flask requests
python app.py
```

ثم افتح: http://127.0.0.1:5000

### Admin
- الرابط: http://127.0.0.1:5000/admin/login
- المستخدم: `admin`
- كلمة المرور: `123456`

## هيكل المجلدات

```
options_tech_cyber/
├── app.py          # التطبيق الكامل (ملف واحد)
├── data/           # ملفات JSON (تُنشأ تلقائياً)
├── static/         # ضع logo.jpg هنا (اختياري)
└── README.md
```

## الخدمات الافتراضية

1. صيانة الكمبيوتر والسيرفرات (بما فيها Gaming PCs)
2. الأمن السيبراني
3. تطوير البرمجيات والمواقع
4. الدعم الفني عن بُعد
5. أنظمة إدارة المبيعات والمخازن (ERP)
6. استرجاع البيانات

## ملاحظات

- ضع `logo.jpg` داخل مجلد `static` إن أردت شعاراً مخصصاً.
- لتفعيل الـ AI: ادخل Admin → AI Settings → ضع API Key وفعّل النموذج.
