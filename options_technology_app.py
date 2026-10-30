#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Options Technology - Dark Cyberpunk / Sci-Fi HUD Edition (v2)
شركة أوبشنز تكنولوجي - تصميم مستقبلي
ميزات: Dark Cyberpunk + AR/EN + RTL + Diagnostic + Courses Content
+ Educational Videos + AI Assistant Icon + YouTube + Chatbot + Admin
"""

from flask import (
    Flask, render_template_string, request, redirect, url_for,
    session, jsonify, flash, send_from_directory
)
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import re
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "options-tech-cyber-secret-2026")
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB for video uploads

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
CHATBOT_FILE = os.path.join(DATA_DIR, "chatbot.json")
MESSAGES_FILE = os.path.join(DATA_DIR, "messages.json")
SITE_FILE = os.path.join(DATA_DIR, "site_data.json")
AI_FILE = os.path.join(DATA_DIR, "ai_settings.json")
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
VIDEOS_FILE = os.path.join(DATA_DIR, "videos.json")

ALLOWED_VIDEO_EXT = {"mp4", "webm", "ogg", "mov", "mkv"}

DEFAULT_SITE = {
    "company_name": "Options Technology",
    "company_name_ar": "أوبشنز تكنولوجي",
    "hero_title": "تكنولوجيا المستقبل بين يديك اليوم",
    "hero_title_en": "Future Tech in Your Hands Today",
    "hero_subtitle": "حلول كمبيوتر وشبكات فائقة التطور — صيانة • أمن سيبراني • استرجاع بيانات • تطوير برمجيات",
    "hero_subtitle_en": "Ultra-advanced computer & network solutions — Maintenance • Cybersecurity • Data Recovery • Software Development",
    "about_title": "من نحن",
    "about_title_en": "About Us",
    "about_text": "أوبشنز تكنولوجي شركة متخصصة في تقديم الحلول التقنية الشاملة. نعمل منذ سنوات على خدمة العملاء في مجالات صيانة الأجهزة والسيرفرات، الشبكات، استرجاع البيانات، الأمن السيبراني، تطوير البرمجيات، وأنظمة إدارة المبيعات. هدفنا تقديم خدمة سريعة وموثوقة تلبي احتياجاتك بدقة.",
    "about_text_en": "Options Technology is a specialized company providing comprehensive tech solutions. For years we have served clients in computer & server maintenance, networking, data recovery, cybersecurity, software development, and sales management systems. Our goal is fast, reliable service tailored to your needs.",
    "phone": "01060662414",
    "whatsapp": "01060662414",
    "email": "options013@gmail.com",
    "facebook": "https://www.facebook.com/optionsqalioup",
    "youtube": "",
    "address": "مصر",
    "address_en": "Egypt",
    "primary_color": "#00f0ff",
    "secondary_color": "#9d4edd",
    "accent_color": "#ff2a6d"
}

DEFAULT_SERVICES = [
    {"id": 1, "title": "صيانة الكمبيوتر والسيرفرات", "title_en": "PC & Server Maintenance", "icon": "💻",
     "description": "صيانة وإصلاح أجهزة الكمبيوتر واللابتوب والسيرفرات وحواسيب الألعاب بأعلى جودة وسرعة.",
     "description_en": "Maintenance and repair of PCs, laptops, servers, and Gaming PCs with top quality and speed.",
     "details": "تشخيص الأعطال، استبدال القطع، تنظيف حراري، وتركيب الأنظمة.",
     "details_en": "Fault diagnosis, parts replacement, thermal cleaning, and system installation."},
    {"id": 2, "title": "الأمن السيبراني", "title_en": "Cybersecurity", "icon": "🔒",
     "description": "حماية أنظمتك وبياناتك من الاختراق والبرمجيات الخبيثة وتأمين الشبكات.",
     "description_en": "Protect your systems and data from breaches and malware, and secure your networks.",
     "details": "تأمين الشبكات، مكافحة الفيروسات، جدران الحماية، والنسخ الاحتياطي.",
     "details_en": "Network security, antivirus, firewalls, and backups."},
    {"id": 3, "title": "تطوير البرمجيات والمواقع", "title_en": "Software & Web Development", "icon": "⚙️",
     "description": "تطوير مواقع وتطبيقات وأنظمة برمجية مخصصة لاحتياجات عملك.",
     "description_en": "Custom websites, apps, and software systems tailored to your business needs.",
     "details": "مواقع، تطبيقات ويب، أنظمة إدارة، وواجهات مستخدم حديثة.",
     "details_en": "Websites, web apps, management systems, and modern UIs."},
    {"id": 4, "title": "الدعم الفني عن بُعد", "title_en": "Remote Technical Support", "icon": "🛰️",
     "description": "دعم فني فوري عن بُعد لحل المشاكل بسرعة دون الحاجة للحضور.",
     "description_en": "Instant remote technical support to solve issues quickly without on-site visits.",
     "details": "اتصال آمن، تشخيص فوري، وإصلاح عن بُعد.",
     "details_en": "Secure connection, instant diagnosis, and remote repair."},
    {"id": 5, "title": "أنظمة إدارة المبيعات والمخازن", "title_en": "ERP & Sales Systems", "icon": "📊",
     "description": "أنظمة إدارة مبيعات ومخازن متكاملة لرفع كفاءة عملك.",
     "description_en": "Integrated sales and inventory management systems to boost your business efficiency.",
     "details": "فواتير، مخزون، تقارير، ومتابعة عملاء.",
     "details_en": "Invoices, inventory, reports, and customer tracking."},
    {"id": 6, "title": "استرجاع البيانات", "title_en": "Data Recovery", "icon": "💾",
     "description": "استرجاع البيانات المحذوفة أو التالفة من الهارد ديسك والفلاتشات.",
     "description_en": "Recover deleted or damaged data from hard drives and flash drives.",
     "details": "استرجاع من الأقراص التالفة، الفورمات، الفيروسات، وأعطال النظام.",
     "details_en": "Recovery from damaged disks, formatting, viruses, and system failures."}
]

DEFAULT_CHATBOT = [
    {"id": 1, "question": "ما هي خدماتكم", "question_en": "what are your services",
     "answer": "نقدم: صيانة الكمبيوتر والسيرفرات، الأمن السيبراني، تطوير البرمجيات، الدعم عن بُعد، أنظمة ERP، واسترجاع البيانات. كيف يمكنني مساعدتك؟",
     "answer_en": "We offer: PC & server maintenance, cybersecurity, software development, remote support, ERP systems, and data recovery. How can I help?"},
    {"id": 2, "question": "أسعار الخدمات", "question_en": "prices cost pricing quote",
     "answer": "الأسعار تختلف حسب نوع الخدمة وحجم العمل. تواصل عبر واتساب 01060662414 للحصول على عرض سعر.",
     "answer_en": "Prices vary by service type and scope. Contact us on WhatsApp 01060662414 for a quote."},
    {"id": 3, "question": "موقعكم أين", "question_en": "where location address",
     "answer": "نخدم العملاء في مصر. تواصل عبر واتساب أو الهاتف لتحديد الموعد.",
     "answer_en": "We serve clients in Egypt. Contact us via WhatsApp or phone to arrange."},
    {"id": 4, "question": "كيف أتواصل", "question_en": "how to contact contact us",
     "answer": "📱 واتساب: 01060662414\n📞 هاتف: 01060662414\n📧 إيميل: options013@gmail.com",
     "answer_en": "📱 WhatsApp: 01060662414\n📞 Phone: 01060662414\n📧 Email: options013@gmail.com"},
    {"id": 5, "question": "صيانة منازل", "question_en": "home visit on-site maintenance",
     "answer": "نعم، نقدم خدمة في الموقع (منازل وشركات) حسب الاتفاق.",
     "answer_en": "Yes, we offer on-site service (homes & companies) by arrangement."},
    {"id": 6, "question": "مرحبا", "question_en": "hello hi hey",
     "answer": "أهلاً بك في أوبشنز تكنولوجي! 👋 كيف يمكنني مساعدتك؟",
     "answer_en": "Welcome to Options Technology! 👋 How can I help you?"},
    {"id": 7, "question": "السلام عليكم", "question_en": "assalamu alaikum",
     "answer": "وعليكم السلام ورحمة الله 🌟 أهلاً بك، كيف أقدر أساعدك؟",
     "answer_en": "Wa alaikum assalam 🌟 Welcome, how can I help?"},
    {"id": 8, "question": "الكمبيوتر بطيء", "question_en": "computer slow lagging performance",
     "answer": "بطء الكمبيوتر قد يكون بسبب برامج خلفية أو نقص رام أو هارد قديم أو فيروسات. يمكننا تسريعه بتنظيف أو ترقية SSD/رام.",
     "answer_en": "Slow PC can be background programs, low RAM, old HDD, or malware. We can speed it up with cleanup or SSD/RAM upgrade."},
    {"id": 9, "question": "فيروس", "question_en": "virus malware infected",
     "answer": "إذا كان جهازك مصاباً: لا تدخل بيانات مهمة، افصل الإنترنت، واتصل بنا. نقدم إزالة فيروسات وتأمين الجهاز.",
     "answer_en": "If infected: avoid sensitive data, disconnect internet, contact us. We offer malware removal and securing."},
    {"id": 10, "question": "شاشة زرقاء", "question_en": "blue screen bsod crash",
     "answer": "الشاشة الزرقاء تشير لمشكلة نظام أو هاردوير. نقوم بتشخيص وإصلاحها.",
     "answer_en": "BSOD indicates system or hardware issue. We diagnose and fix it."},
    {"id": 11, "question": "لا يعمل الكمبيوتر", "question_en": "computer not turning on boot",
     "answer": "تحقق من الكهرباء والكيبل. قد تكون مشكلة باور سبلاي أو ماذربورد. أحضره أو نأتي إليك.",
     "answer_en": "Check power and cables. Could be PSU or motherboard. Bring it or we come to you."},
    {"id": 12, "question": "واي فاي ضعيف", "question_en": "wifi weak slow internet",
     "answer": "ضعف الواي فاي قد يكون موقع الراوتر أو تداخل. نقوم بتحسين الشبكة وتركيب نقاط وصول.",
     "answer_en": "Weak WiFi can be router position or interference. We optimize and install access points."},
    {"id": 13, "question": "تركيب شبكة", "question_en": "network setup install lan",
     "answer": "نصمم ونركب شبكات سلكية ولاسلكية للمنازل والشركات مع مراقبة.",
     "answer_en": "We design and install wired/wireless networks for homes and companies with monitoring."},
    {"id": 14, "question": "الراوتر", "question_en": "router setup problem",
     "answer": "نساعدك في إعداد الراوتر وتغيير كلمة المرور وتحسين الأمان.",
     "answer_en": "We help with router setup, password change, and security improvement."},
    {"id": 15, "question": "حماية البيانات", "question_en": "data protection security",
     "answer": "نحمي بياناتك بجدران حماية وبرامج مكافحة فيروسات ونسخ احتياطي.",
     "answer_en": "We protect data with firewalls, antivirus, and backups."},
    {"id": 16, "question": "اختراق", "question_en": "hacked breach",
     "answer": "إذا تعرضت لاختراق: غيّر كلمات المرور فوراً، افصل الجهاز، واتصل بنا.",
     "answer_en": "If hacked: change passwords immediately, disconnect, and contact us."},
    {"id": 17, "question": "نسخ احتياطي", "question_en": "backup data",
     "answer": "نوصي بنسخ احتياطي منتظم. نساعدك في إعداد نظام آمن.",
     "answer_en": "We recommend regular backups. We help set up a secure system."},
    {"id": 18, "question": "استرجاع بيانات", "question_en": "data recovery recover deleted",
     "answer": "نسترجع البيانات المحذوفة أو التالفة. لا تستخدم الجهاز بعد الحذف وأت به فوراً.",
     "answer_en": "We recover deleted/damaged data. Don't use the device after deletion and bring it ASAP."},
    {"id": 19, "question": "ترقية SSD", "question_en": "ssd upgrade ram",
     "answer": "ترقية إلى SSD تزيد السرعة بشكل كبير. نقوم بالترقية ونقل البيانات بأمان.",
     "answer_en": "SSD upgrade greatly increases speed. We upgrade and safely transfer data."},
    {"id": 20, "question": "لابتوب", "question_en": "laptop repair",
     "answer": "نصلح اللابتوب: شاشة، بطارية، كيبورد، ماذربورد، وتنظيف حراري.",
     "answer_en": "We repair laptops: screen, battery, keyboard, motherboard, and thermal cleaning."}
]

DEFAULT_AI = {
    "enabled": False,
    "api_key": "",
    "model": "grok-4.7",
    "base_url": "https://api.x.ai/v1",
    "system_prompt": "أنت مساعد ذكي لشركة أوبشنز تكنولوجي المتخصصة في صيانة الكمبيوتر والشبكات والأمن السيبراني واسترجاع البيانات وتطوير البرمجيات. أجب بشكل احترافي ومفيد باللغة التي يسأل بها العميل. إذا لم تعرف الإجابة، وجهه للتواصل عبر واتساب 01060662414."
}

DEFAULT_COURSES = [
    {"id": 1, "title": "أساسيات صيانة الكمبيوتر", "title_en": "PC Maintenance Basics",
     "description": "تعلم تشخيص الأعطال الشائعة وإصلاحها.", "description_en": "Learn to diagnose and fix common PC issues.",
     "video_url": "", "content": "في هذا الكورس ستتعلم:\n1. التعرف على مكونات الكمبيوتر\n2. تشخيص الأعطال الشائعة (بطء، شاشة زرقاء، عدم التشغيل)\n3. تنظيف الجهاز حرارياً\n4. تثبيت نظام التشغيل والتعريفات\n5. نصائح للصيانة الدورية"},
    {"id": 2, "title": "مقدمة في الأمن السيبراني", "title_en": "Cybersecurity Intro",
     "description": "حماية جهازك وبياناتك من التهديدات.", "description_en": "Protect your device and data from threats.",
     "video_url": "", "content": "محتوى الكورس:\n1. ما هو الأمن السيبراني؟\n2. أنواع التهديدات (فيروسات، فدية، تصيد)\n3. كلمات المرور القوية والمصادقة الثنائية\n4. النسخ الاحتياطي الآمن\n5. أفضل ممارسات الحماية اليومية"}
]

DEFAULT_VIDEOS = []


def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    save_json(filepath, default)
    return default


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_site():
    site = load_json(SITE_FILE, DEFAULT_SITE)
    if "youtube" not in site:
        site["youtube"] = ""
    return site


def get_services():
    return load_json(SERVICES_FILE, DEFAULT_SERVICES)


def get_chatbot():
    return load_json(CHATBOT_FILE, DEFAULT_CHATBOT)


def get_messages():
    return load_json(MESSAGES_FILE, [])


def get_ai():
    return load_json(AI_FILE, DEFAULT_AI)


def get_courses():
    return load_json(COURSES_FILE, DEFAULT_COURSES)


def get_videos():
    return load_json(VIDEOS_FILE, DEFAULT_VIDEOS)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def call_openai(messages, settings):
    try:
        headers = {
            "Authorization": f"Bearer {settings['api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.get("model", "gpt-4o-mini"),
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        url = settings.get("base_url", "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("AI Error:", e)
        return None


def youtube_embed(url):
    """Convert YouTube URL to embed URL."""
    if not url:
        return ""
    m = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{6,})", url)
    if m:
        return f"https://www.youtube.com/embed/{m.group(1)}"
    return url


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
BASE_CSS = r"""
:root {
    --bg: #050714;
    --bg-card: rgba(12, 18, 40, 0.75);
    --bg-glass: rgba(0, 240, 255, 0.06);
    --text: #e0f7ff;
    --text-muted: #7a9bb8;
    --primary: #00f0ff;
    --primary-dim: rgba(0, 240, 255, 0.15);
    --secondary: #9d4edd;
    --accent: #ff2a6d;
    --success: #00ff9f;
    --border: rgba(0, 240, 255, 0.25);
    --glow: 0 0 20px rgba(0, 240, 255, 0.4);
    --glow-strong: 0 0 40px rgba(0, 240, 255, 0.6);
    --radius: 12px;
    --font-ar: 'Cairo', 'Segoe UI', sans-serif;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: var(--font-ar);
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    overflow-x: hidden;
    min-height: 100vh;
}
body[dir="ltr"] { font-family: 'Inter', sans-serif; }
a { text-decoration: none; color: inherit; }
img { max-width: 100%; display: block; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

.cyber-bg {
    position: fixed; inset: 0; z-index: -1;
    background:
        linear-gradient(rgba(0,240,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,240,255,0.03) 1px, transparent 1px),
        radial-gradient(ellipse at 20% 20%, rgba(157,78,221,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(0,240,255,0.08) 0%, transparent 50%),
        var(--bg);
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%, 100% 100%;
}
.particles { position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden; }
.particle {
    position: absolute; width: 2px; height: 2px;
    background: var(--primary); border-radius: 50%;
    box-shadow: 0 0 6px var(--primary);
    animation: floatParticle linear infinite; opacity: 0.6;
}
@keyframes floatParticle {
    0% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 0.6; }
    90% { opacity: 0.6; }
    100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}

.navbar {
    background: rgba(5, 7, 20, 0.9);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 1000;
    padding: 12px 0;
}
.navbar .container { display: flex; justify-content: space-between; align-items: center; }
.logo {
    display: flex; align-items: center; gap: 12px;
    font-size: 1.25rem; font-weight: 800; color: var(--primary);
}
.logo .cpu-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, var(--primary-dim), rgba(157,78,221,0.2));
    border: 1px solid var(--border); border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
    box-shadow: var(--glow); animation: glowPulse 3s ease-in-out infinite;
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 15px rgba(0,240,255,0.4); }
    50% { box-shadow: 0 0 30px rgba(0,240,255,0.7); }
}
.logo span { color: var(--text); letter-spacing: 0.5px; }
.nav-links { display: flex; gap: 6px; list-style: none; align-items: center; flex-wrap: wrap; }
.nav-links a {
    font-weight: 600; color: var(--text-muted);
    padding: 8px 12px; border-radius: 8px; transition: all 0.25s; font-size: 0.88rem;
}
.nav-links a:hover {
    color: var(--primary); background: var(--primary-dim);
    box-shadow: 0 0 12px rgba(0,240,255,0.2);
}
.btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 11px 22px; border-radius: 8px; font-weight: 700;
    border: none; cursor: pointer; transition: all 0.3s; font-size: 0.95rem;
}
.btn-primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #050714; box-shadow: var(--glow);
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: var(--glow-strong); }
.btn-outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
.btn-outline:hover { background: var(--primary-dim); box-shadow: var(--glow); }
.btn-accent {
    background: linear-gradient(135deg, var(--accent), #c9184a);
    color: white; box-shadow: 0 0 20px rgba(255,42,109,0.4);
}
.btn-accent:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(255,42,109,0.6); }
.btn-whatsapp { background: #25D366; color: white; }
.btn-whatsapp:hover { background: #1da851; transform: translateY(-2px); }
.btn-youtube { background: #FF0000; color: white; }
.btn-youtube:hover { background: #cc0000; transform: translateY(-2px); }
.nav-controls { display: flex; align-items: center; gap: 8px; }
.lang-btn {
    width: auto; padding: 0 12px; height: 38px; border-radius: 8px;
    border: 1px solid var(--border); background: var(--bg-card);
    color: var(--text); cursor: pointer; font-size: 0.8rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center; transition: all 0.25s;
}
.lang-btn:hover { border-color: var(--primary); color: var(--primary); box-shadow: var(--glow); }
.menu-toggle {
    display: none; background: none; border: 1px solid var(--border);
    color: var(--text); font-size: 1.4rem; cursor: pointer;
    width: 40px; height: 40px; border-radius: 8px;
    align-items: center; justify-content: center;
}

.hero { position: relative; padding: 80px 0 70px; overflow: hidden; }
.hero .container { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 50px; align-items: center; }
.hero-content h1 {
    font-size: 2.6rem; font-weight: 800; line-height: 1.3; margin-bottom: 18px;
    background: linear-gradient(135deg, #fff 0%, var(--primary) 50%, var(--secondary) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-content p { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 28px; }
.hero-buttons { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 36px; }
.hero-stats { display: flex; gap: 28px; flex-wrap: wrap; }
.hero-stat { text-align: center; }
.hero-stat .num { font-size: 1.6rem; font-weight: 800; color: var(--primary); font-family: 'Share Tech Mono', monospace; }
.hero-stat .label { font-size: 0.8rem; color: var(--text-muted); }

.server-core {
    position: relative; width: 100%; max-width: 380px; margin: 0 auto;
    aspect-ratio: 1; display: flex; align-items: center; justify-content: center;
}
.core-ring { position: absolute; border-radius: 50%; border: 1px solid var(--border); animation: rotate 20s linear infinite; }
.core-ring:nth-child(1) { width: 100%; height: 100%; border-color: rgba(0,240,255,0.3); box-shadow: inset 0 0 40px rgba(0,240,255,0.1), 0 0 40px rgba(0,240,255,0.1); }
.core-ring:nth-child(2) { width: 75%; height: 75%; border-color: rgba(157,78,221,0.4); animation-direction: reverse; animation-duration: 15s; }
.core-ring:nth-child(3) { width: 50%; height: 50%; border-color: rgba(255,42,109,0.3); animation-duration: 10s; }
.core-center {
    width: 100px; height: 100px;
    background: linear-gradient(135deg, var(--primary-dim), rgba(157,78,221,0.3));
    border: 2px solid var(--primary); border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 2.5rem;
    box-shadow: var(--glow-strong); animation: glowPulse 2.5s ease-in-out infinite; z-index: 2;
}
.core-label {
    position: absolute; bottom: -10px; left: 50%; transform: translateX(-50%);
    font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: var(--primary);
    background: var(--bg); padding: 4px 12px; border: 1px solid var(--border); border-radius: 4px; white-space: nowrap;
}
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

section { padding: 80px 0; position: relative; }
.section-header { text-align: center; margin-bottom: 50px; }
.section-badge {
    display: inline-block; background: var(--primary-dim); color: var(--primary);
    border: 1px solid var(--border); padding: 5px 16px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 700; margin-bottom: 12px;
    font-family: 'Share Tech Mono', monospace; letter-spacing: 1px;
}
.section-header h2 { font-size: 2.1rem; font-weight: 800; margin-bottom: 12px; color: var(--text); }
.section-header p { color: var(--text-muted); max-width: 600px; margin: 0 auto; }

.services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
.service-card {
    background: var(--bg-card); backdrop-filter: blur(12px);
    border: 1px solid var(--border); border-radius: var(--radius); padding: 28px;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden;
}
.service-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
    opacity: 0; transition: opacity 0.4s;
}
.service-card:hover {
    transform: translateY(-8px); border-color: var(--primary);
    box-shadow: var(--glow), 0 20px 40px rgba(0,0,0,0.3);
}
.service-card:hover::before { opacity: 1; }
.service-icon {
    width: 60px; height: 60px; background: var(--primary-dim); border: 1px solid var(--border);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 1.7rem; margin-bottom: 18px; transition: all 0.3s;
}
.service-card:hover .service-icon { box-shadow: var(--glow); transform: scale(1.08); }
.service-card h3 { font-size: 1.15rem; margin-bottom: 10px; color: var(--text); }
.service-card p { color: var(--text-muted); font-size: 0.92rem; }

/* Course cards clickable */
.course-card { cursor: pointer; }
.course-card .course-hint {
    margin-top: 12px; font-size: 0.8rem; color: var(--primary); opacity: 0.8;
}

/* Modal */
.modal-overlay {
    display: none; position: fixed; inset: 0; z-index: 10000;
    background: rgba(0,0,0,0.75); backdrop-filter: blur(6px);
    align-items: center; justify-content: center; padding: 20px;
}
.modal-overlay.open { display: flex; }
.modal-box {
    background: rgba(8,12,28,0.98); border: 1px solid var(--border);
    border-radius: 16px; max-width: 640px; width: 100%; max-height: 85vh;
    overflow-y: auto; box-shadow: var(--glow-strong); padding: 32px; position: relative;
}
.modal-close {
    position: absolute; top: 14px; left: 14px; background: none; border: none;
    color: var(--text-muted); font-size: 1.6rem; cursor: pointer; line-height: 1;
}
body[dir="ltr"] .modal-close { left: auto; right: 14px; }
.modal-box h2 { color: var(--primary); margin-bottom: 12px; font-size: 1.4rem; padding-left: 30px; }
body[dir="ltr"] .modal-box h2 { padding-left: 0; padding-right: 30px; }
.modal-box .modal-desc { color: var(--text-muted); margin-bottom: 20px; }
.modal-box .modal-content {
    white-space: pre-wrap; line-height: 1.9; color: var(--text);
    background: rgba(0,240,255,0.04); border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; font-size: 0.95rem;
}
.modal-box .modal-video { margin-top: 20px; }
.modal-box .modal-video iframe, .modal-box .modal-video video {
    width: 100%; aspect-ratio: 16/9; border-radius: 10px; border: 1px solid var(--border);
}

/* Videos grid */
.videos-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
.video-card {
    background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
    overflow: hidden; transition: all 0.3s;
}
.video-card:hover { border-color: var(--primary); box-shadow: var(--glow); transform: translateY(-4px); }
.video-card .video-thumb {
    width: 100%; aspect-ratio: 16/9; background: #0a0e1a;
    display: flex; align-items: center; justify-content: center; position: relative;
}
.video-card .video-thumb iframe, .video-card .video-thumb video {
    width: 100%; height: 100%; border: none;
}
.video-card .video-info { padding: 18px; }
.video-card .video-info h3 { font-size: 1.05rem; margin-bottom: 8px; color: var(--text); }
.video-card .video-info p { color: var(--text-muted); font-size: 0.88rem; }

.diagnostic-section {
    background: rgba(0, 240, 255, 0.02);
    border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.diagnostic-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.diag-panel {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 28px; backdrop-filter: blur(12px);
}
.diag-panel h3 { font-size: 1.2rem; margin-bottom: 20px; color: var(--primary); font-family: 'Share Tech Mono', monospace; }
.diag-group { margin-bottom: 18px; }
.diag-group label { display: block; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 600; }
.diag-options { display: flex; flex-wrap: wrap; gap: 8px; }
.diag-opt {
    padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border);
    background: transparent; color: var(--text-muted); cursor: pointer; font-size: 0.88rem;
    transition: all 0.25s; font-family: inherit;
}
.diag-opt:hover, .diag-opt.active {
    border-color: var(--primary); color: var(--primary);
    background: var(--primary-dim); box-shadow: 0 0 12px rgba(0,240,255,0.2);
}
.terminal {
    background: #0a0e1a; border: 1px solid var(--border); border-radius: var(--radius);
    padding: 20px; font-family: 'Share Tech Mono', monospace; font-size: 0.85rem;
    min-height: 320px; max-height: 400px; overflow-y: auto; color: var(--success); line-height: 1.8;
}
.terminal .line { margin-bottom: 4px; }
.terminal .prompt { color: var(--primary); }
.terminal .cmd { color: var(--text); }
.terminal .ok { color: var(--success); }
.terminal .warn { color: #f59e0b; }
.terminal .err { color: var(--accent); }
.terminal .info { color: var(--secondary); }

.contact-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; }
.contact-info {
    background: linear-gradient(160deg, rgba(0,240,255,0.08), rgba(157,78,221,0.08));
    border: 1px solid var(--border); border-radius: var(--radius); padding: 36px;
}
.contact-info h3 { font-size: 1.3rem; margin-bottom: 24px; color: var(--primary); font-family: 'Share Tech Mono', monospace; }
.contact-item { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.contact-item .icon {
    width: 48px; height: 48px; background: var(--primary-dim); border: 1px solid var(--border);
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
}
.contact-item a:hover { color: var(--primary); }
.contact-form {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 36px; backdrop-filter: blur(12px);
}
.contact-form h3 { font-size: 1.3rem; margin-bottom: 24px; color: var(--primary); font-family: 'Share Tech Mono', monospace; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 0.88rem; color: var(--text-muted); }
.form-group input, .form-group textarea, .form-group select {
    width: 100%; padding: 12px 16px; border: 1px solid var(--border);
    border-radius: 8px; font-size: 0.95rem; font-family: inherit;
    background: rgba(5,7,20,0.6); color: var(--text); transition: all 0.25s;
}
.form-group input:focus, .form-group textarea:focus {
    outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(0,240,255,0.15);
}
.form-group textarea { resize: vertical; min-height: 110px; }
.alert { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-weight: 600; }
.alert-success { background: rgba(0,255,159,0.12); color: var(--success); border: 1px solid rgba(0,255,159,0.3); }
.alert-error { background: rgba(255,42,109,0.12); color: var(--accent); border: 1px solid rgba(255,42,109,0.3); }

.about-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; align-items: center; }
.about-text h2 { font-size: 1.9rem; margin-bottom: 16px; }
.about-text p { color: var(--text-muted); margin-bottom: 20px; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 28px; }
.stat-item {
    text-align: center; padding: 18px; background: var(--bg-card);
    border: 1px solid var(--border); border-radius: var(--radius); transition: all 0.3s;
}
.stat-item:hover { border-color: var(--primary); box-shadow: var(--glow); }
.stat-item .num { font-size: 1.7rem; font-weight: 800; color: var(--primary); }
.stat-item .label { font-size: 0.8rem; color: var(--text-muted); }
.about-visual {
    background: linear-gradient(160deg, rgba(0,240,255,0.1), rgba(157,78,221,0.15));
    border: 1px solid var(--border); border-radius: 16px; padding: 40px; text-align: center; box-shadow: var(--glow);
}
.about-visual .big-icon { font-size: 4rem; margin-bottom: 16px; }

.footer {
    background: rgba(5,7,20,0.95); border-top: 1px solid var(--border); padding: 50px 0 24px;
}
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 36px; margin-bottom: 36px; }
.footer h4 { font-size: 1rem; margin-bottom: 16px; color: var(--primary); font-family: 'Share Tech Mono', monospace; }
.footer p, .footer a { color: var(--text-muted); font-size: 0.92rem; }
.footer a:hover { color: var(--primary); }
.footer-bottom {
    border-top: 1px solid rgba(0,240,255,0.1); padding-top: 20px; text-align: center;
    color: var(--text-muted); font-size: 0.85rem;
}

/* Chatbot */
.chatbot-toggle {
    position: fixed; bottom: 28px; left: 28px; width: 60px; height: 60px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 50%; border: none; color: #050714; font-size: 1.5rem;
    cursor: pointer; box-shadow: var(--glow-strong); z-index: 9999; transition: all 0.3s;
    display: flex; align-items: center; justify-content: center;
}
body[dir="ltr"] .chatbot-toggle { left: auto; right: 28px; }
.chatbot-toggle:hover { transform: scale(1.1); }
.chatbot-window {
    position: fixed; bottom: 100px; left: 28px; width: 370px;
    max-width: calc(100vw - 40px); height: 500px;
    background: rgba(8,12,28,0.95); border: 1px solid var(--border); border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), var(--glow);
    z-index: 9998; display: none; flex-direction: column; overflow: hidden; backdrop-filter: blur(20px);
}
body[dir="ltr"] .chatbot-window { left: auto; right: 28px; }
.chatbot-window.open { display: flex; }
.chatbot-header {
    background: linear-gradient(135deg, rgba(0,240,255,0.15), rgba(157,78,221,0.15));
    border-bottom: 1px solid var(--border); color: var(--text); padding: 14px 18px;
    display: flex; justify-content: space-between; align-items: center;
}
.chatbot-header h4 { font-size: 1rem; color: var(--primary); }
.chatbot-close { background: none; border: none; color: var(--text-muted); font-size: 1.4rem; cursor: pointer; }
.chatbot-messages { flex: 1; overflow-y: auto; padding: 16px; }
.chat-msg {
    margin-bottom: 12px; max-width: 85%; padding: 10px 14px;
    border-radius: 12px; font-size: 0.9rem; line-height: 1.5; white-space: pre-wrap;
}
.chat-msg.bot { background: var(--bg-card); border: 1px solid var(--border); color: var(--text); }
body[dir="rtl"] .chat-msg.bot { border-bottom-right-radius: 4px; }
body[dir="ltr"] .chat-msg.bot { border-bottom-left-radius: 4px; }
.chat-msg.user { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #050714; }
body[dir="rtl"] .chat-msg.user { margin-right: auto; margin-left: 0; border-bottom-left-radius: 4px; }
body[dir="ltr"] .chat-msg.user { margin-left: auto; margin-right: 0; border-bottom-right-radius: 4px; }
.chatbot-input-area { display: flex; padding: 12px; border-top: 1px solid var(--border); gap: 8px; }
.chatbot-input-area input {
    flex: 1; padding: 10px 14px; border: 1px solid var(--border); border-radius: 20px;
    font-size: 0.92rem; outline: none; background: rgba(5,7,20,0.6); color: var(--text);
}
.chatbot-input-area input:focus { border-color: var(--primary); }
.chatbot-send {
    width: 42px; height: 42px; border-radius: 50%; background: var(--primary);
    color: #050714; border: none; cursor: pointer; font-size: 1.1rem; transition: transform 0.2s;
}
.chatbot-send:hover { transform: scale(1.08); }

/* AI Assistant button (separate from chatbot) */
.ai-assist-btn {
    position: fixed; bottom: 100px; left: 28px;
    background: linear-gradient(135deg, #00f0ff, #9d4edd);
    color: #050714; border: none; border-radius: 50px;
    padding: 12px 18px; font-weight: 800; cursor: pointer;
    box-shadow: 0 0 25px rgba(0,240,255,0.5); z-index: 9999;
    display: flex; align-items: center; gap: 8px; font-size: 0.9rem;
    transition: all 0.3s; animation: glowPulse 3s ease-in-out infinite;
}
body[dir="ltr"] .ai-assist-btn { left: auto; right: 28px; }
.ai-assist-btn:hover { transform: scale(1.05); box-shadow: 0 0 35px rgba(0,240,255,0.7); }
.ai-assist-window {
    position: fixed; bottom: 160px; left: 28px; width: 370px;
    max-width: calc(100vw - 40px); height: 480px;
    background: rgba(8,12,28,0.97); border: 1px solid var(--border); border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(157,78,221,0.3);
    z-index: 9997; display: none; flex-direction: column; overflow: hidden; backdrop-filter: blur(20px);
}
body[dir="ltr"] .ai-assist-window { left: auto; right: 28px; }
.ai-assist-window.open { display: flex; }
.ai-assist-header {
    background: linear-gradient(135deg, #00f0ff, #9d4edd); color: #050714;
    padding: 14px 18px; font-weight: 800; display: flex; justify-content: space-between; align-items: center;
}
.ai-assist-header button { background: none; border: none; font-size: 1.4rem; cursor: pointer; color: #050714; }

/* Admin */
.admin-body { background: var(--bg); min-height: 100vh; }
.admin-login-page {
    min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg);
}
.login-box {
    background: var(--bg-card); padding: 40px; border-radius: 16px; width: 100%; max-width: 400px;
    border: 1px solid var(--border); box-shadow: var(--glow); color: var(--text);
}
.login-box h2 { text-align: center; margin-bottom: 28px; color: var(--primary); }
.admin-layout { display: flex; min-height: 100vh; }
.admin-sidebar {
    width: 260px; background: rgba(8,12,28,0.95); border-left: 1px solid var(--border);
    color: white; padding: 24px 0; position: fixed; height: 100vh; overflow-y: auto;
}
body[dir="ltr"] .admin-sidebar { border-left: none; border-right: 1px solid var(--border); }
.admin-sidebar .logo {
    padding: 0 24px 24px; border-bottom: 1px solid var(--border);
    margin-bottom: 18px; color: var(--primary);
}
.admin-nav a {
    display: flex; align-items: center; gap: 10px; padding: 13px 24px;
    color: var(--text-muted); font-weight: 600; transition: all 0.25s;
}
.admin-nav a:hover, .admin-nav a.active { background: var(--primary-dim); color: var(--primary); }
.admin-main { margin-right: 260px; flex: 1; padding: 28px; }
body[dir="ltr"] .admin-main { margin-right: 0; margin-left: 260px; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; flex-wrap: wrap; gap: 12px; }
.admin-header h1 { font-size: 1.5rem; color: var(--text); }
.stat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 18px; margin-bottom: 28px; }
.stat-card {
    background: var(--bg-card); padding: 22px; border-radius: var(--radius);
    border: 1px solid var(--border); transition: all 0.3s;
}
.stat-card:hover { border-color: var(--primary); box-shadow: var(--glow); }
.stat-card .num { font-size: 1.9rem; font-weight: 800; color: var(--primary); }
.stat-card .label { color: var(--text-muted); font-size: 0.85rem; }
.admin-card {
    background: var(--bg-card); border-radius: var(--radius);
    border: 1px solid var(--border); padding: 28px; margin-bottom: 24px;
}
.admin-card h3 {
    margin-bottom: 18px; font-size: 1.15rem; border-bottom: 1px solid var(--border);
    padding-bottom: 12px; color: var(--primary);
}
.table { width: 100%; border-collapse: collapse; }
.table th, .table td {
    padding: 12px 14px; text-align: right;
    border-bottom: 1px solid rgba(0,240,255,0.1); color: var(--text);
}
body[dir="ltr"] .table th, body[dir="ltr"] .table td { text-align: left; }
.table th { background: rgba(0,240,255,0.05); font-weight: 700; font-size: 0.88rem; }
.table tr:hover { background: rgba(0,240,255,0.03); }
.btn-sm { padding: 6px 14px; font-size: 0.82rem; border-radius: 6px; }
.btn-danger { background: var(--accent); color: white; }
.btn-danger:hover { background: #c9184a; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-actions { display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
.toggle-switch { position: relative; display: inline-block; width: 48px; height: 24px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-slider {
    position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
    background: #333; transition: .4s; border-radius: 24px;
}
.toggle-slider:before {
    position: absolute; content: ""; height: 18px; width: 18px;
    left: 3px; bottom: 3px; background: white; transition: .4s; border-radius: 50%;
}
input:checked + .toggle-slider { background: var(--primary); }
input:checked + .toggle-slider:before { transform: translateX(24px); }

@media (max-width: 900px) {
    .hero .container { grid-template-columns: 1fr; text-align: center; }
    .hero-content h1 { font-size: 2rem; }
    .hero-buttons, .hero-stats { justify-content: center; }
    .server-core { max-width: 280px; }
    .about-grid, .contact-grid, .diagnostic-grid { grid-template-columns: 1fr; }
    .footer-grid { grid-template-columns: 1fr; }
    .nav-links {
        display: none; flex-direction: column; position: absolute;
        top: 100%; right: 0; left: 0; background: rgba(5,7,20,0.98);
        padding: 18px; border-bottom: 1px solid var(--border); gap: 4px;
    }
    .nav-links.show { display: flex; }
    .menu-toggle { display: flex; }
    .admin-sidebar { width: 100%; height: auto; position: relative; }
    .admin-main { margin-right: 0 !important; margin-left: 0 !important; }
    .admin-layout { flex-direction: column; }
    .form-row { grid-template-columns: 1fr; }
    .stats { grid-template-columns: 1fr; }
    .ai-assist-btn { bottom: 100px; }
    .ai-assist-window { bottom: 160px; }
}
"""

# ═══════════════════════════════════════════════════════════════
# HOME TEMPLATE
# ═══════════════════════════════════════════════════════════════
HOME_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site.company_name }} | {{ site.company_name_ar }}</title>
    <meta name="description" content="{{ site.hero_subtitle }}">
    <link rel="icon" href="/static/logo.jpg" type="image/jpeg">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Orbitron:wght@500;700&family=Share+Tech+Mono&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>{{ css }}
:root {
    --primary: {{ site.primary_color|default("#00f0ff") }};
    --secondary: {{ site.secondary_color|default("#9d4edd") }};
    --accent: {{ site.accent_color|default("#ff2a6d") }};
}
</style>
</head>
<body dir="rtl">
    <div class="cyber-bg"></div>
    <div class="particles" id="particles"></div>

    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">
                <div class="cpu-icon">⚡</div>
                <span class="lang-ar">{{ site.company_name_ar }}</span>
                <span class="lang-en" style="display:none;">{{ site.company_name }}</span>
            </a>
            <div style="display:flex;align-items:center;gap:10px;">
                <div class="nav-controls">
                    <button class="lang-btn" id="langBtn" title="Language">EN</button>
                </div>
                <button class="menu-toggle" onclick="document.querySelector('.nav-links').classList.toggle('show')">☰</button>
                <ul class="nav-links">
                    <li><a href="#home"><span class="lang-ar">الرئيسية</span><span class="lang-en" style="display:none;">Home</span></a></li>
                    <li><a href="#services"><span class="lang-ar">خدماتنا</span><span class="lang-en" style="display:none;">Services</span></a></li>
                    <li><a href="#diagnostic"><span class="lang-ar">التشخيص الذكي</span><span class="lang-en" style="display:none;">Diagnostic</span></a></li>
                    <li><a href="#courses"><span class="lang-ar">كورسات</span><span class="lang-en" style="display:none;">Courses</span></a></li>
                    <li><a href="#videos"><span class="lang-ar">فيديوهات تعليمية</span><span class="lang-en" style="display:none;">Videos</span></a></li>
                    <li><a href="#about"><span class="lang-ar">من نحن</span><span class="lang-en" style="display:none;">About</span></a></li>
                    <li><a href="#contact"><span class="lang-ar">اتصل بنا</span><span class="lang-en" style="display:none;">Contact</span></a></li>
                    <li><a href="https://wa.me/2{{ site.whatsapp }}" target="_blank" class="btn btn-accent" style="padding:8px 14px;font-size:0.82rem;">
                        <span class="lang-ar">طلب خدمة</span>
                        <span class="lang-en" style="display:none;">Request</span>
                    </a></li>
                </ul>
            </div>
        </div>
    </nav>

    <section class="hero" id="home">
        <div class="container">
            <div class="hero-content">
                <h1>
                    <span class="lang-ar">{{ site.hero_title }}</span>
                    <span class="lang-en" style="display:none;">{{ site.hero_title_en }}</span>
                </h1>
                <p>
                    <span class="lang-ar">{{ site.hero_subtitle }}</span>
                    <span class="lang-en" style="display:none;">{{ site.hero_subtitle_en }}</span>
                </p>
                <div class="hero-buttons">
                    <a href="#services" class="btn btn-primary">
                        <span class="lang-ar">استكشف الخدمات</span>
                        <span class="lang-en" style="display:none;">Explore Services</span>
                    </a>
                    <a href="#diagnostic" class="btn btn-outline">
                        <span class="lang-ar">تشخيص فوري</span>
                        <span class="lang-en" style="display:none;">Instant Diagnostic</span>
                    </a>
                </div>
                <div class="hero-stats">
                    <div class="hero-stat"><div class="num">+500</div><div class="label"><span class="lang-ar">عميل</span><span class="lang-en" style="display:none;">Clients</span></div></div>
                    <div class="hero-stat"><div class="num">&lt;24h</div><div class="label"><span class="lang-ar">استجابة</span><span class="lang-en" style="display:none;">Response</span></div></div>
                    <div class="hero-stat"><div class="num">99.9%</div><div class="label"><span class="lang-ar">نجاح</span><span class="lang-en" style="display:none;">Success</span></div></div>
                </div>
            </div>
            <div class="hero-visual">
                <div class="server-core">
                    <div class="core-ring"></div>
                    <div class="core-ring"></div>
                    <div class="core-ring"></div>
                    <div class="core-center">⚡</div>
                    <div class="core-label">SERVER CORE // ACTIVE</div>
                </div>
            </div>
        </div>
    </section>

    <section id="services">
        <div class="container">
            <div class="section-header">
                <span class="section-badge">// SERVICES</span>
                <h2><span class="lang-ar">خدماتنا المتقدمة</span><span class="lang-en" style="display:none;">Advanced Services</span></h2>
                <p><span class="lang-ar">حلول تقنية شاملة تلبي جميع احتياجاتك باحترافية عالية</span><span class="lang-en" style="display:none;">Comprehensive tech solutions with high professionalism</span></p>
            </div>
            <div class="services-grid">
                {% for s in services %}
                <div class="service-card">
                    <div class="service-icon">{{ s.icon }}</div>
                    <h3><span class="lang-ar">{{ s.title }}</span><span class="lang-en" style="display:none;">{{ s.title_en }}</span></h3>
                    <p><span class="lang-ar">{{ s.description }}</span><span class="lang-en" style="display:none;">{{ s.description_en }}</span></p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <section class="diagnostic-section" id="diagnostic">
        <div class="container">
            <div class="section-header">
                <span class="section-badge">// DIAGNOSTIC TOOL</span>
                <h2><span class="lang-ar">أداة التشخيص الفوري الذكية</span><span class="lang-en" style="display:none;">Smart Instant Diagnostic Tool</span></h2>
                <p><span class="lang-ar">اختر نوع جهازك والمشكلة، واحصل على تحليل فوري وحل مقترح</span><span class="lang-en" style="display:none;">Select your device type and issue for instant analysis</span></p>
            </div>
            <div class="diagnostic-grid">
                <div class="diag-panel">
                    <h3>&gt; INPUT_PARAMS</h3>
                    <div class="diag-group">
                        <label><span class="lang-ar">نوع الجهاز</span><span class="lang-en" style="display:none;">Device Type</span></label>
                        <div class="diag-options" id="deviceOpts">
                            <button class="diag-opt active" data-val="pc">PC</button>
                            <button class="diag-opt" data-val="laptop"><span class="lang-ar">لابتوب</span><span class="lang-en" style="display:none;">Laptop</span></button>
                            <button class="diag-opt" data-val="server"><span class="lang-ar">سيرفر</span><span class="lang-en" style="display:none;">Server</span></button>
                            <button class="diag-opt" data-val="network"><span class="lang-ar">شبكات</span><span class="lang-en" style="display:none;">Network</span></button>
                        </div>
                    </div>
                    <div class="diag-group">
                        <label><span class="lang-ar">المشكلة</span><span class="lang-en" style="display:none;">Issue</span></label>
                        <div class="diag-options" id="issueOpts">
                            <button class="diag-opt active" data-val="slow"><span class="lang-ar">بطء وحرارة</span><span class="lang-en" style="display:none;">Slow & Heat</span></button>
                            <button class="diag-opt" data-val="network"><span class="lang-ar">انقطاع شبكة</span><span class="lang-en" style="display:none;">Network Drop</span></button>
                            <button class="diag-opt" data-val="system"><span class="lang-ar">عطل نظام</span><span class="lang-en" style="display:none;">System Fault</span></button>
                            <button class="diag-opt" data-val="data"><span class="lang-ar">فقدان بيانات</span><span class="lang-en" style="display:none;">Data Loss</span></button>
                            <button class="diag-opt" data-val="virus"><span class="lang-ar">فيروس</span><span class="lang-en" style="display:none;">Virus</span></button>
                        </div>
                    </div>
                    <button class="btn btn-primary" style="width:100%;justify-content:center;margin-top:10px;" onclick="runDiagnostic()">
                        <span class="lang-ar">▶ بدء الفحص والتحليل</span>
                        <span class="lang-en" style="display:none;">▶ Start Scan & Analysis</span>
                    </button>
                </div>
                <div class="diag-panel">
                    <h3>&gt; TERMINAL_OUTPUT</h3>
                    <div class="terminal" id="terminal">
                        <div class="line"><span class="prompt">OPT-TECH$</span> <span class="cmd">waiting for input...</span></div>
                        <div class="line"><span class="info">// Select device & issue, then run scan</span></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Courses -->
    <section id="courses">
        <div class="container">
            <div class="section-header">
                <span class="section-badge">// COURSES</span>
                <h2><span class="lang-ar">كورسات تعليمية</span><span class="lang-en" style="display:none;">Educational Courses</span></h2>
                <p><span class="lang-ar">اضغط على الكورس لعرض المحتوى الكامل</span><span class="lang-en" style="display:none;">Click a course to view full content</span></p>
            </div>
            <div class="services-grid">
                {% for c in courses %}
                <div class="service-card course-card" onclick='openCourseModal({{ c|tojson }})'>
                    <h3><span class="lang-ar">{{ c.title }}</span><span class="lang-en" style="display:none;">{{ c.title_en }}</span></h3>
                    <p><span class="lang-ar">{{ c.description }}</span><span class="lang-en" style="display:none;">{{ c.description_en }}</span></p>
                    <div class="course-hint">
                        <span class="lang-ar">👆 اضغط لعرض المحتوى</span>
                        <span class="lang-en" style="display:none;">👆 Click to view content</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Educational Videos -->
    <section id="videos">
        <div class="container">
            <div class="section-header">
                <span class="section-badge">// VIDEOS</span>
                <h2><span class="lang-ar">فيديوهات تعليمية</span><span class="lang-en" style="display:none;">Educational Videos</span></h2>
                <p><span class="lang-ar">شروحات ومقاطع تعليمية في التقنية والصيانة</span><span class="lang-en" style="display:none;">Tutorials and educational tech videos</span></p>
            </div>
            {% if videos %}
            <div class="videos-grid">
                {% for v in videos %}
                <div class="video-card">
                    <div class="video-thumb">
                        {% if v.file_path %}
                        <video controls src="/static/videos/{{ v.file_path }}"></video>
                        {% elif v.embed_url %}
                        <iframe src="{{ v.embed_url }}" allowfullscreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
                        {% elif v.video_url %}
                        <iframe src="{{ v.video_url }}" allowfullscreen></iframe>
                        {% else %}
                        <span style="color:var(--text-muted);font-size:2rem;">🎬</span>
                        {% endif %}
                    </div>
                    <div class="video-info">
                        <h3><span class="lang-ar">{{ v.title }}</span><span class="lang-en" style="display:none;">{{ v.title_en or v.title }}</span></h3>
                        <p><span class="lang-ar">{{ v.description }}</span><span class="lang-en" style="display:none;">{{ v.description_en or v.description }}</span></p>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p style="text-align:center;color:var(--text-muted);padding:40px;">
                <span class="lang-ar">لا توجد فيديوهات حالياً — سيتم إضافتها قريباً</span>
                <span class="lang-en" style="display:none;">No videos yet — coming soon</span>
            </p>
            {% endif %}
        </div>
    </section>

    <section id="about">
        <div class="container">
            <div class="about-grid">
                <div class="about-text">
                    <span class="section-badge">// ABOUT</span>
                    <h2><span class="lang-ar">{{ site.about_title }}</span><span class="lang-en" style="display:none;">{{ site.about_title_en }}</span></h2>
                    <p><span class="lang-ar">{{ site.about_text }}</span><span class="lang-en" style="display:none;">{{ site.about_text_en }}</span></p>
                    <div class="stats">
                        <div class="stat-item"><div class="num">+500</div><div class="label"><span class="lang-ar">عميل سعيد</span><span class="lang-en" style="display:none;">Happy Clients</span></div></div>
                        <div class="stat-item"><div class="num">6</div><div class="label"><span class="lang-ar">خدمات</span><span class="lang-en" style="display:none;">Services</span></div></div>
                        <div class="stat-item"><div class="num">24/7</div><div class="label"><span class="lang-ar">دعم</span><span class="lang-en" style="display:none;">Support</span></div></div>
                    </div>
                </div>
                <div class="about-visual">
                    <div class="big-icon">⚡</div>
                    <h3 style="color:var(--primary);margin-bottom:8px;">{{ site.company_name }}</h3>
                    <p style="color:var(--text-muted);"><span class="lang-ar">شريكك التقني الموثوق</span><span class="lang-en" style="display:none;">Your Trusted Tech Partner</span></p>
                </div>
            </div>
        </div>
    </section>

    <section id="contact">
        <div class="container">
            <div class="section-header">
                <span class="section-badge">// CONTACT TERMINAL</span>
                <h2><span class="lang-ar">تواصل معنا</span><span class="lang-en" style="display:none;">Contact Us</span></h2>
                <p><span class="lang-ar">أرسل طلب صيانة أو استفسار — سنرد في أقرب وقت</span><span class="lang-en" style="display:none;">Send a maintenance request or inquiry</span></p>
            </div>
            <div class="contact-grid">
                <div class="contact-info">
                    <h3>&gt; CONTACT_INFO</h3>
                    <div class="contact-item">
                        <div class="icon">📱</div>
                        <div>
                            <div style="font-size:0.8rem;color:var(--text-muted);">WhatsApp / Phone</div>
                            <a href="https://wa.me/2{{ site.whatsapp }}" target="_blank">{{ site.phone }}</a>
                        </div>
                    </div>
                    <div class="contact-item">
                        <div class="icon">📧</div>
                        <div>
                            <div style="font-size:0.8rem;color:var(--text-muted);">Email</div>
                            <a href="mailto:{{ site.email }}">{{ site.email }}</a>
                        </div>
                    </div>
                    <div class="contact-item">
                        <div class="icon">📘</div>
                        <div>
                            <div style="font-size:0.8rem;color:var(--text-muted);">Facebook</div>
                            <a href="{{ site.facebook }}" target="_blank"><span class="lang-ar">صفحة الشركة</span><span class="lang-en" style="display:none;">Our Page</span></a>
                        </div>
                    </div>
                    {% if site.youtube %}
                    <div class="contact-item">
                        <div class="icon">▶️</div>
                        <div>
                            <div style="font-size:0.8rem;color:var(--text-muted);">YouTube</div>
                            <a href="{{ site.youtube }}" target="_blank"><span class="lang-ar">قناتنا على يوتيوب</span><span class="lang-en" style="display:none;">Our YouTube Channel</span></a>
                        </div>
                    </div>
                    {% endif %}
                    <div style="margin-top:24px;display:flex;flex-direction:column;gap:10px;">
                        <a href="https://wa.me/2{{ site.whatsapp }}" target="_blank" class="btn btn-whatsapp" style="width:100%;justify-content:center;">💬 WhatsApp</a>
                        {% if site.youtube %}
                        <a href="{{ site.youtube }}" target="_blank" class="btn btn-youtube" style="width:100%;justify-content:center;">▶️ YouTube</a>
                        {% endif %}
                    </div>
                </div>
                <div class="contact-form">
                    <h3>&gt; SEND_REQUEST</h3>
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, msg in messages %}
                                <div class="alert alert-{{ category }}">{{ msg }}</div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    <form method="POST" action="/contact">
                        <div class="form-group">
                            <label><span class="lang-ar">الاسم الكامل</span><span class="lang-en" style="display:none;">Full Name</span></label>
                            <input type="text" name="name" required>
                        </div>
                        <div class="form-group">
                            <label><span class="lang-ar">البريد الإلكتروني</span><span class="lang-en" style="display:none;">Email</span></label>
                            <input type="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label><span class="lang-ar">رقم الهاتف</span><span class="lang-en" style="display:none;">Phone</span></label>
                            <input type="tel" name="phone" required>
                        </div>
                        <div class="form-group">
                            <label><span class="lang-ar">الرسالة / وصف المشكلة</span><span class="lang-en" style="display:none;">Message / Issue</span></label>
                            <textarea name="message" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;">
                            <span class="lang-ar">إرسال الطلب</span>
                            <span class="lang-en" style="display:none;">Send Request</span>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div>
                    <h4 style="display:flex;align-items:center;gap:10px;"><span style="font-size:1.4rem;">⚡</span> {{ site.company_name }}</h4>
                    <p><span class="lang-ar">{{ site.hero_subtitle }}</span><span class="lang-en" style="display:none;">{{ site.hero_subtitle_en }}</span></p>
                </div>
                <div>
                    <h4><span class="lang-ar">روابط سريعة</span><span class="lang-en" style="display:none;">Quick Links</span></h4>
                    <p><a href="#services"><span class="lang-ar">خدماتنا</span><span class="lang-en" style="display:none;">Services</span></a></p>
                    <p><a href="#videos"><span class="lang-ar">فيديوهات</span><span class="lang-en" style="display:none;">Videos</span></a></p>
                    <p><a href="#contact"><span class="lang-ar">تواصل معنا</span><span class="lang-en" style="display:none;">Contact</span></a></p>
                    <p><a href="{{ site.facebook }}" target="_blank">Facebook</a></p>
                    {% if site.youtube %}<p><a href="{{ site.youtube }}" target="_blank">YouTube</a></p>{% endif %}
                </div>
                <div>
                    <h4><span class="lang-ar">تواصل</span><span class="lang-en" style="display:none;">Contact</span></h4>
                    <p>📱 {{ site.phone }}</p>
                    <p>📧 {{ site.email }}</p>
                </div>
            </div>
            <div class="footer-bottom">
                © {{ year }} {{ site.company_name }}.
                <span class="lang-ar">جميع الحقوق محفوظة.</span>
                <span class="lang-en" style="display:none;">All rights reserved.</span>
            </div>
        </div>
    </footer>

    <!-- Course Modal -->
    <div class="modal-overlay" id="courseModal">
        <div class="modal-box">
            <button class="modal-close" onclick="closeCourseModal()">×</button>
            <h2 id="modalTitle"></h2>
            <p class="modal-desc" id="modalDesc"></p>
            <div class="modal-content" id="modalContent"></div>
            <div class="modal-video" id="modalVideo" style="display:none;"></div>
        </div>
    </div>

    <!-- Chatbot -->
    <button class="chatbot-toggle" id="chatToggle" title="Chat">💬</button>
    <div class="chatbot-window" id="chatWindow">
        <div class="chatbot-header">
            <h4>
                <span class="lang-ar">🤖 مساعد أوبشنز</span>
                <span class="lang-en" style="display:none;">🤖 Options Assistant</span>
            </h4>
            <button class="chatbot-close" id="chatClose">×</button>
        </div>
        <div class="chatbot-messages" id="chatMessages">
            <div class="chat-msg bot">
                <span class="lang-ar">أهلاً بك في أوبشنز تكنولوجي! 👋 كيف يمكنني مساعدتك؟</span>
                <span class="lang-en" style="display:none;">Welcome to Options Technology! 👋 How can I help you?</span>
            </div>
        </div>
        <div class="chatbot-input-area">
            <input type="text" id="chatInput" placeholder="..." onkeypress="if(event.key==='Enter')sendChat()">
            <button class="chatbot-send" onclick="sendChat()">➤</button>
        </div>
    </div>

    {% if ai.enabled %}
    <!-- AI Assistant (only when enabled) -->
    <button class="ai-assist-btn" id="aiAssistBtn">
        🧠 <span class="lang-ar">مساعدة AI</span><span class="lang-en" style="display:none;">AI Help</span>
    </button>
    <div class="ai-assist-window" id="aiAssistWin">
        <div class="ai-assist-header">
            <span><span class="lang-ar">مساعد الذكاء الاصطناعي</span><span class="lang-en" style="display:none;">AI Assistant</span></span>
            <button id="aiAssistClose">×</button>
        </div>
        <div class="chatbot-messages" id="aiAssistMsgs" style="flex:1;overflow-y:auto;padding:16px;">
            <div class="chat-msg bot">
                <span class="lang-ar">أهلاً! أنا مساعد أوبشنز الذكي. اسألني عن أي خدمة أو مشكلة تقنية.</span>
                <span class="lang-en" style="display:none;">Hi! I'm Options AI assistant. Ask me about any service or tech issue.</span>
            </div>
        </div>
        <div class="chatbot-input-area">
            <input type="text" id="aiAssistInput" placeholder="..." onkeypress="if(event.key==='Enter')sendAIAssist()">
            <button class="chatbot-send" onclick="sendAIAssist()">➤</button>
        </div>
    </div>
    {% endif %}

    <script>
    (function() {
        const container = document.getElementById('particles');
        for (let i = 0; i < 30; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            p.style.left = Math.random() * 100 + '%';
            p.style.animationDuration = (8 + Math.random() * 15) + 's';
            p.style.animationDelay = Math.random() * 10 + 's';
            p.style.width = p.style.height = (1 + Math.random() * 2) + 'px';
            container.appendChild(p);
        }
    })();

    let currentLang = localStorage.getItem('lang') || 'ar';
    const langBtn = document.getElementById('langBtn');
    function applyLang(lang) {
        currentLang = lang;
        localStorage.setItem('lang', lang);
        const isAr = lang === 'ar';
        document.body.setAttribute('dir', isAr ? 'rtl' : 'ltr');
        document.documentElement.lang = lang;
        langBtn.textContent = isAr ? 'EN' : 'عر';
        document.querySelectorAll('.lang-ar').forEach(el => { el.style.display = isAr ? '' : 'none'; });
        document.querySelectorAll('.lang-en').forEach(el => { el.style.display = isAr ? 'none' : ''; });
        const chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.placeholder = isAr ? 'اكتب سؤالك...' : 'Type your question...';
        const aiInput = document.getElementById('aiAssistInput');
        if (aiInput) aiInput.placeholder = isAr ? 'اسأل الذكاء الاصطناعي...' : 'Ask AI...';
    }
    applyLang(currentLang);
    langBtn.onclick = () => applyLang(currentLang === 'ar' ? 'en' : 'ar');

    // Course Modal
    function openCourseModal(c) {
        const isAr = currentLang === 'ar';
        document.getElementById('modalTitle').textContent = isAr ? c.title : (c.title_en || c.title);
        document.getElementById('modalDesc').textContent = isAr ? c.description : (c.description_en || c.description);
        document.getElementById('modalContent').textContent = c.content || (isAr ? 'لا يوجد محتوى تفصيلي.' : 'No detailed content.');
        const videoEl = document.getElementById('modalVideo');
        if (c.video_url) {
            videoEl.style.display = 'block';
            const embed = c.video_url.includes('youtube') || c.video_url.includes('youtu.be')
                ? c.video_url.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
                : c.video_url;
            if (embed.includes('youtube.com/embed') || embed.includes('youtu')) {
                videoEl.innerHTML = '<iframe src="' + embed + '" allowfullscreen></iframe>';
            } else {
                videoEl.innerHTML = '<video controls src="' + c.video_url + '"></video>';
            }
        } else {
            videoEl.style.display = 'none';
            videoEl.innerHTML = '';
        }
        document.getElementById('courseModal').classList.add('open');
    }
    function closeCourseModal() {
        document.getElementById('courseModal').classList.remove('open');
    }
    document.getElementById('courseModal').addEventListener('click', function(e) {
        if (e.target === this) closeCourseModal();
    });

    // Chatbot
    const toggle = document.getElementById('chatToggle');
    const win = document.getElementById('chatWindow');
    const closeBtn = document.getElementById('chatClose');
    const messages = document.getElementById('chatMessages');
    const input = document.getElementById('chatInput');
    toggle.onclick = () => win.classList.toggle('open');
    closeBtn.onclick = () => win.classList.remove('open');

    function addMsg(container, text, type) {
        const div = document.createElement('div');
        div.className = 'chat-msg ' + type;
        div.textContent = text;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    async function sendChat() {
        const text = input.value.trim();
        if (!text) return;
        addMsg(messages, text, 'user');
        input.value = '';
        try {
            const res = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text, lang: currentLang})
            });
            const data = await res.json();
            addMsg(messages, data.reply, 'bot');
        } catch(e) {
            addMsg(messages, currentLang === 'ar'
                ? 'حدث خطأ، تواصل عبر واتساب: 01060662414'
                : 'Error. Contact WhatsApp: 01060662414', 'bot');
        }
    }

    // AI Assistant
    {% if ai.enabled %}
    const aiBtn = document.getElementById('aiAssistBtn');
    const aiWin = document.getElementById('aiAssistWin');
    const aiClose = document.getElementById('aiAssistClose');
    const aiMsgs = document.getElementById('aiAssistMsgs');
    const aiInput = document.getElementById('aiAssistInput');
    if (aiBtn) {
        aiBtn.onclick = () => aiWin.classList.toggle('open');
        aiClose.onclick = () => aiWin.classList.remove('open');
    }
    async function sendAIAssist() {
        const text = aiInput.value.trim();
        if (!text) return;
        addMsg(aiMsgs, text, 'user');
        aiInput.value = '';
        addMsg(aiMsgs, currentLang === 'ar' ? 'جاري التفكير...' : 'Thinking...', 'bot');
        try {
            const res = await fetch('/api/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text, lang: currentLang})
            });
            const data = await res.json();
            aiMsgs.removeChild(aiMsgs.lastChild);
            addMsg(aiMsgs, data.reply, 'bot');
        } catch(e) {
            aiMsgs.removeChild(aiMsgs.lastChild);
            addMsg(aiMsgs, currentLang === 'ar'
                ? 'خطأ في الاتصال بالـ AI. تأكد من تفعيل المفتاح في لوحة التحكم.'
                : 'AI connection error. Check API key in admin.', 'bot');
        }
    }
    {% endif %}

    // Diagnostic
    let selectedDevice = 'pc';
    let selectedIssue = 'slow';
    document.querySelectorAll('#deviceOpts .diag-opt').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('#deviceOpts .diag-opt').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedDevice = btn.dataset.val;
        };
    });
    document.querySelectorAll('#issueOpts .diag-opt').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('#issueOpts .diag-opt').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedIssue = btn.dataset.val;
        };
    });

    const solutions = {
        pc: {
            slow: { ar: ['فحص درجة حرارة المعالج والمراوح', 'تنظيف النظام من البرامج غير الضرورية', 'فحص الرام والهارد', 'ترقية مقترحة: SSD + تنظيف حراري', 'الوقت التقديري: 1-2 ساعة'], en: ['Check CPU temp & fans', 'Clean unnecessary programs', 'Check RAM & storage', 'Suggested: SSD + thermal cleaning', 'Est. time: 1-2 hours'] },
            network: { ar: ['فحص كابل الشبكة وبطاقة الشبكة', 'تحديث تعريفات الشبكة', 'إعادة ضبط إعدادات TCP/IP', 'الوقت التقديري: 30-60 دقيقة'], en: ['Check network cable & NIC', 'Update network drivers', 'Reset TCP/IP', 'Est. time: 30-60 min'] },
            system: { ar: ['فحص ملفات النظام (SFC / DISM)', 'فحص الهاردوير (رام/هارد)', 'استعادة النظام أو إعادة تثبيت', 'الوقت التقديري: 2-4 ساعات'], en: ['System file check (SFC/DISM)', 'Hardware check', 'System restore or reinstall', 'Est. time: 2-4 hours'] },
            data: { ar: ['عدم استخدام الجهاز فوراً', 'فحص القرص ببرامج استرجاع متخصصة', 'نسخ البيانات المسترجعة لهارد خارجي', 'الوقت التقديري: 2-8 ساعات'], en: ['Stop using the device', 'Scan with recovery tools', 'Copy to external drive', 'Est. time: 2-8 hours'] },
            virus: { ar: ['فصل الإنترنت فوراً', 'فحص بمضاد فيروسات متقدم', 'تنظيف وإزالة البرمجيات الخبيثة', 'تأمين النظام', 'الوقت التقديري: 1-3 ساعات'], en: ['Disconnect internet', 'Advanced antivirus scan', 'Remove malware', 'Secure system', 'Est. time: 1-3 hours'] }
        },
        laptop: {
            slow: { ar: ['تنظيف فتحات التهوية والمعجون الحراري', 'فحص البطارية', 'ترقية SSD/رام إن أمكن', 'الوقت التقديري: 1-2 ساعة'], en: ['Clean vents & thermal paste', 'Check battery', 'SSD/RAM upgrade', 'Est. time: 1-2 hours'] },
            network: { ar: ['فحص محول الواي فاي', 'تحديث التعريفات', 'إعادة ضبط الشبكة', 'الوقت التقديري: 30-45 دقيقة'], en: ['Check WiFi adapter', 'Update drivers', 'Reset network', 'Est. time: 30-45 min'] },
            system: { ar: ['فحص النظام والهاردوير', 'استعادة أو إعادة تثبيت Windows', 'الوقت التقديري: 2-4 ساعات'], en: ['System & hardware check', 'Restore or reinstall', 'Est. time: 2-4 hours'] },
            data: { ar: ['عدم استخدام اللابتوب', 'استرجاع البيانات ببرامج متخصصة', 'الوقت التقديري: 2-8 ساعات'], en: ['Stop using laptop', 'Recover with specialized tools', 'Est. time: 2-8 hours'] },
            virus: { ar: ['فصل الإنترنت', 'فحص وتنظيف شامل', 'تأمين النظام', 'الوقت التقديري: 1-3 ساعات'], en: ['Disconnect internet', 'Full scan & cleanup', 'Secure system', 'Est. time: 1-3 hours'] }
        },
        server: {
            slow: { ar: ['مراقبة الموارد (CPU/RAM/Disk I/O)', 'تحسين الخدمات', 'فحص التخزين والشبكات', 'الوقت التقديري: 2-4 ساعات'], en: ['Monitor resources', 'Optimize services', 'Check storage & network', 'Est. time: 2-4 hours'] },
            network: { ar: ['فحص السويتشات والرواتر', 'تحليل حركة الشبكة', 'ضبط الجدران النارية', 'الوقت التقديري: 1-3 ساعات'], en: ['Check switches & routers', 'Analyze traffic', 'Tune firewalls', 'Est. time: 1-3 hours'] },
            system: { ar: ['فحص سجلات النظام', 'تحديثات الأمان', 'نسخ احتياطي واستعادة', 'الوقت التقديري: 2-6 ساعات'], en: ['Check system logs', 'Security updates', 'Backup & restore', 'Est. time: 2-6 hours'] },
            data: { ar: ['إيقاف الكتابة على القرص', 'استرجاع من النسخ الاحتياطي', 'الوقت التقديري: حسب الحجم'], en: ['Stop disk writes', 'Recover from backup', 'Est. time: depends on size'] },
            virus: { ar: ['عزل السيرفر عن الشبكة', 'فحص شامل وتنظيف', 'مراجعة سياسات الأمان', 'الوقت التقديري: 2-6 ساعات'], en: ['Isolate server', 'Full scan & cleanup', 'Review security policies', 'Est. time: 2-6 hours'] }
        },
        network: {
            slow: { ar: ['تحليل سرعة الاتصال', 'فحص الراوتر ونقاط الوصول', 'تحسين القنوات', 'الوقت التقديري: 1-2 ساعة'], en: ['Analyze speed', 'Check router & APs', 'Optimize channels', 'Est. time: 1-2 hours'] },
            network: { ar: ['فحص الكابلات والأجهزة', 'إعادة ضبط الراوتر', 'تكوين VLAN إن لزم', 'الوقت التقديري: 1-3 ساعات'], en: ['Check cables & devices', 'Reset router', 'Configure VLAN', 'Est. time: 1-3 hours'] },
            system: { ar: ['فحص إعدادات الشبكة', 'تحديث firmware', 'الوقت التقديري: 1-2 ساعة'], en: ['Check network settings', 'Update firmware', 'Est. time: 1-2 hours'] },
            data: { ar: ['فحص خوادم الملفات والنسخ الاحتياطي', 'استرجاع من النسخ', 'الوقت التقديري: حسب الحجم'], en: ['Check file servers & backups', 'Recover from backups', 'Est. time: depends on size'] },
            virus: { ar: ['فحص جميع الأجهزة المتصلة', 'عزل الأجهزة المصابة', 'تحديث الحماية', 'الوقت التقديري: 2-4 ساعات'], en: ['Scan all devices', 'Isolate infected', 'Update protection', 'Est. time: 2-4 hours'] }
        }
    };

    function runDiagnostic() {
        const term = document.getElementById('terminal');
        const isAr = currentLang === 'ar';
        const deviceNames = { pc: 'PC', laptop: isAr ? 'لابتوب' : 'Laptop', server: isAr ? 'سيرفر' : 'Server', network: isAr ? 'شبكات' : 'Network' };
        const issueNames = {
            slow: isAr ? 'بطء وحرارة' : 'Slow & Heat',
            network: isAr ? 'انقطاع شبكة' : 'Network Drop',
            system: isAr ? 'عطل نظام' : 'System Fault',
            data: isAr ? 'فقدان بيانات' : 'Data Loss',
            virus: isAr ? 'فيروس' : 'Virus'
        };
        term.innerHTML = '';
        const lines = [
            { cls: 'prompt', text: 'OPT-TECH$ ' },
            { cls: 'cmd', text: 'scan --device=' + selectedDevice + ' --issue=' + selectedIssue },
            { cls: 'info', text: isAr ? '// بدء الفحص...' : '// Starting scan...' },
            { cls: 'ok', text: isAr ? '[✓] الاتصال بالجهاز... OK' : '[✓] Connecting... OK' },
            { cls: 'ok', text: isAr ? '[✓] قراءة معلومات النظام... OK' : '[✓] Reading system info... OK' },
            { cls: 'ok', text: isAr ? '[✓] تحليل المشكلة... OK' : '[✓] Analyzing... OK' },
            { cls: 'warn', text: isAr ? '[!] تم اكتشاف: ' + issueNames[selectedIssue] + ' على ' + deviceNames[selectedDevice] : '[!] Detected: ' + issueNames[selectedIssue] + ' on ' + deviceNames[selectedDevice] },
            { cls: 'info', text: isAr ? '// الحل المقترح:' : '// Suggested solution:' }
        ];
        const sol = (solutions[selectedDevice] && solutions[selectedDevice][selectedIssue])
            ? solutions[selectedDevice][selectedIssue][isAr ? 'ar' : 'en']
            : (isAr ? ['تواصل معنا للتشخيص الدقيق'] : ['Contact us for precise diagnosis']);
        let i = 0;
        function addLine() {
            if (i < lines.length) {
                const l = lines[i];
                const div = document.createElement('div');
                div.className = 'line';
                if (l.cls === 'prompt') {
                    div.innerHTML = '<span class="prompt">' + l.text + '</span><span class="cmd">' + (lines[i+1] ? lines[i+1].text : '') + '</span>';
                    i += 2;
                } else {
                    div.innerHTML = '<span class="' + l.cls + '">' + l.text + '</span>';
                    i++;
                }
                term.appendChild(div);
                term.scrollTop = term.scrollHeight;
                setTimeout(addLine, 350);
            } else {
                sol.forEach((s, idx) => {
                    setTimeout(() => {
                        const div = document.createElement('div');
                        div.className = 'line';
                        div.innerHTML = '<span class="ok">  → ' + s + '</span>';
                        term.appendChild(div);
                        term.scrollTop = term.scrollHeight;
                    }, idx * 200);
                });
                setTimeout(() => {
                    const div = document.createElement('div');
                    div.className = 'line';
                    div.innerHTML = '<span class="info">' + (isAr ? '// للتشخيص الكامل تواصل: 01060662414' : '// Full diagnosis: 01060662414') + '</span>';
                    term.appendChild(div);
                    term.scrollTop = term.scrollHeight;
                }, sol.length * 200 + 300);
            }
        }
        addLine();
    }
    </script>
</body>
</html>
"""

ADMIN_LOGIN_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login | Options Technology</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>{{ css }}</style>
</head>
<body class="admin-login-page">
    <div class="cyber-bg"></div>
    <div class="login-box">
        <div style="text-align:center;margin-bottom:16px;font-size:2.5rem;">⚡</div>
        <h2>🔐 Admin Panel</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
        {% endwith %}
        <form method="POST">
            <div class="form-group"><label>Username</label><input type="text" name="username" required autofocus></div>
            <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
            <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:10px;">Login</button>
        </form>
        <p style="text-align:center;margin-top:18px;"><a href="/" style="color:var(--primary);">← Back to Site</a></p>
    </div>
</body>
</html>
"""

ADMIN_DASHBOARD_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin | {{ site.company_name }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>{{ css }}</style>
</head>
<body class="admin-body" dir="rtl">
    <div class="cyber-bg"></div>
    <div class="admin-layout">
        <aside class="admin-sidebar">
            <div class="logo"><span style="font-size:1.3rem;">⚡</span> {{ site.company_name }}</div>
            <nav class="admin-nav">
                <a href="/admin" class="{{ 'active' if page=='dashboard' else '' }}">📊 Dashboard</a>
                <a href="/admin/site" class="{{ 'active' if page=='site' else '' }}">✏️ Site Data</a>
                <a href="/admin/services" class="{{ 'active' if page=='services' else '' }}">🛠️ Services</a>
                <a href="/admin/chatbot" class="{{ 'active' if page=='chatbot' else '' }}">🤖 Chatbot</a>
                <a href="/admin/ai" class="{{ 'active' if page=='ai' else '' }}">🧠 AI Settings</a>
                <a href="/admin/courses" class="{{ 'active' if page=='courses' else '' }}">📚 Courses</a>
                <a href="/admin/videos" class="{{ 'active' if page=='videos' else '' }}">🎬 Videos</a>
                <a href="/admin/messages" class="{{ 'active' if page=='messages' else '' }}">📧 Messages ({{ messages|length }})</a>
                <a href="/admin/logout">🚪 Logout</a>
                <a href="/" target="_blank">🌐 View Site</a>
            </nav>
        </aside>
        <main class="admin-main">
            {% if page == 'dashboard' %}
            <div class="admin-header"><h1>Dashboard</h1></div>
            <div class="stat-cards">
                <div class="stat-card"><div class="num">{{ messages|length }}</div><div class="label">Messages</div></div>
                <div class="stat-card"><div class="num">{{ services|length }}</div><div class="label">Services</div></div>
                <div class="stat-card"><div class="num">{{ chatbot|length }}</div><div class="label">Chatbot Q&A</div></div>
                <div class="stat-card"><div class="num">{{ courses|length }}</div><div class="label">Courses</div></div>
                <div class="stat-card"><div class="num">{{ videos|length }}</div><div class="label">Videos</div></div>
                <div class="stat-card"><div class="num">{{ 'ON' if ai.enabled else 'OFF' }}</div><div class="label">AI Model</div></div>
            </div>
            <div class="admin-card">
                <h3>Latest Messages</h3>
                {% if messages %}
                <table class="table">
                    <thead><tr><th>Name</th><th>Phone</th><th>Date</th></tr></thead>
                    <tbody>
                    {% for m in messages[-5:]|reverse %}
                        <tr><td>{{ m.name }}</td><td>{{ m.phone }}</td><td>{{ m.date }}</td></tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p style="color:var(--text-muted);">No messages yet.</p>
                {% endif %}
            </div>

            {% elif page == 'site' %}
            <div class="admin-header"><h1>Edit Site Data</h1></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                <form method="POST">
                    <div class="form-row">
                        <div class="form-group"><label>Company Name (AR)</label><input type="text" name="company_name_ar" value="{{ site.company_name_ar }}" required></div>
                        <div class="form-group"><label>Company Name (EN)</label><input type="text" name="company_name" value="{{ site.company_name }}" required></div>
                    </div>
                    <div class="form-group"><label>Hero Title (AR)</label><input type="text" name="hero_title" value="{{ site.hero_title }}" required></div>
                    <div class="form-group"><label>Hero Title (EN)</label><input type="text" name="hero_title_en" value="{{ site.hero_title_en }}" required></div>
                    <div class="form-group"><label>Hero Subtitle (AR)</label><textarea name="hero_subtitle" required>{{ site.hero_subtitle }}</textarea></div>
                    <div class="form-group"><label>Hero Subtitle (EN)</label><textarea name="hero_subtitle_en" required>{{ site.hero_subtitle_en }}</textarea></div>
                    <div class="form-group"><label>About Title (AR)</label><input type="text" name="about_title" value="{{ site.about_title }}" required></div>
                    <div class="form-group"><label>About Title (EN)</label><input type="text" name="about_title_en" value="{{ site.about_title_en }}" required></div>
                    <div class="form-group"><label>About Text (AR)</label><textarea name="about_text" required style="min-height:100px;">{{ site.about_text }}</textarea></div>
                    <div class="form-group"><label>About Text (EN)</label><textarea name="about_text_en" required style="min-height:100px;">{{ site.about_text_en }}</textarea></div>
                    <div class="form-row">
                        <div class="form-group"><label>Phone</label><input type="text" name="phone" value="{{ site.phone }}" required></div>
                        <div class="form-group"><label>WhatsApp</label><input type="text" name="whatsapp" value="{{ site.whatsapp }}" required></div>
                    </div>
                    <div class="form-row">
                        <div class="form-group"><label>Email</label><input type="email" name="email" value="{{ site.email }}" required></div>
                        <div class="form-group"><label>Facebook URL</label><input type="url" name="facebook" value="{{ site.facebook }}"></div>
                    </div>
                    <div class="form-group">
                        <label>YouTube Channel URL</label>
                        <input type="url" name="youtube" value="{{ site.youtube or '' }}" placeholder="https://www.youtube.com/@YourChannel">
                        <small style="color:var(--text-muted);">رابط قناة اليوتيوب — يظهر في صفحة التواصل والفوتر</small>
                    </div>
                    <h3 style="margin:20px 0 12px;color:var(--primary);">ألوان الموقع</h3>
                    <div class="form-row">
                        <div class="form-group"><label>Primary</label><input type="color" name="primary_color" value="{{ site.primary_color|default('#00f0ff') }}"></div>
                        <div class="form-group"><label>Secondary</label><input type="color" name="secondary_color" value="{{ site.secondary_color|default('#9d4edd') }}"></div>
                    </div>
                    <div class="form-group"><label>Accent</label><input type="color" name="accent_color" value="{{ site.accent_color|default('#ff2a6d') }}"></div>
                    <div class="form-actions"><button type="submit" class="btn btn-primary">💾 Save</button></div>
                </form>
            </div>

            {% elif page == 'services' %}
            <div class="admin-header"><h1>Services</h1><a href="/admin/services/add" class="btn btn-primary">➕ Add</a></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                <table class="table">
                    <thead><tr><th>Icon</th><th>Title AR</th><th>Title EN</th><th>Actions</th></tr></thead>
                    <tbody>
                    {% for s in services %}
                        <tr>
                            <td style="font-size:1.4rem;">{{ s.icon }}</td>
                            <td>{{ s.title }}</td><td>{{ s.title_en }}</td>
                            <td>
                                <a href="/admin/services/edit/{{ s.id }}" class="btn btn-sm btn-outline">Edit</a>
                                <a href="/admin/services/delete/{{ s.id }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>

            {% elif page == 'service_form' %}
            <div class="admin-header"><h1>{{ 'Edit Service' if service else 'Add Service' }}</h1></div>
            <div class="admin-card">
                <form method="POST">
                    <div class="form-row">
                        <div class="form-group"><label>Title (AR)</label><input type="text" name="title" value="{{ service.title if service else '' }}" required></div>
                        <div class="form-group"><label>Title (EN)</label><input type="text" name="title_en" value="{{ service.title_en if service else '' }}" required></div>
                    </div>
                    <div class="form-group"><label>Icon (emoji)</label><input type="text" name="icon" value="{{ service.icon if service else '🔧' }}" required></div>
                    <div class="form-group"><label>Description (AR)</label><textarea name="description" required>{{ service.description if service else '' }}</textarea></div>
                    <div class="form-group"><label>Description (EN)</label><textarea name="description_en" required>{{ service.description_en if service else '' }}</textarea></div>
                    <div class="form-group"><label>Details (AR)</label><textarea name="details">{{ service.details if service else '' }}</textarea></div>
                    <div class="form-group"><label>Details (EN)</label><textarea name="details_en">{{ service.details_en if service else '' }}</textarea></div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">💾 Save</button>
                        <a href="/admin/services" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>

            {% elif page == 'chatbot' %}
            <div class="admin-header"><h1>Chatbot Q&A</h1><a href="/admin/chatbot/add" class="btn btn-primary">➕ Add</a></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                <table class="table">
                    <thead><tr><th>Question AR</th><th>Answer</th><th>Actions</th></tr></thead>
                    <tbody>
                    {% for c in chatbot %}
                        <tr>
                            <td>{{ c.question }}</td><td>{{ c.answer[:50] }}...</td>
                            <td>
                                <a href="/admin/chatbot/edit/{{ c.id }}" class="btn btn-sm btn-outline">Edit</a>
                                <a href="/admin/chatbot/delete/{{ c.id }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>

            {% elif page == 'chatbot_form' %}
            <div class="admin-header"><h1>{{ 'Edit Q&A' if item else 'Add Q&A' }}</h1></div>
            <div class="admin-card">
                <form method="POST">
                    <div class="form-group"><label>Question keywords (AR)</label><input type="text" name="question" value="{{ item.question if item else '' }}" required></div>
                    <div class="form-group"><label>Question keywords (EN)</label><input type="text" name="question_en" value="{{ item.question_en if item else '' }}"></div>
                    <div class="form-group"><label>Answer (AR)</label><textarea name="answer" required style="min-height:90px;">{{ item.answer if item else '' }}</textarea></div>
                    <div class="form-group"><label>Answer (EN)</label><textarea name="answer_en" style="min-height:90px;">{{ item.answer_en if item else '' }}</textarea></div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">💾 Save</button>
                        <a href="/admin/chatbot" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>

            {% elif page == 'ai' %}
            <div class="admin-header"><h1>AI Model Settings</h1></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                <form method="POST">
                    <div class="form-group">
                        <label style="display:flex;align-items:center;gap:12px;">
                            Enable AI Model
                            <label class="toggle-switch">
                                <input type="checkbox" name="enabled" {{ 'checked' if ai.enabled else '' }}>
                                <span class="toggle-slider"></span>
                            </label>
                        </label>
                        <small style="color:var(--text-muted);display:block;margin-top:8px;">عند التفعيل تظهر أيقونة مساعدة AI منفصلة عن الشات بوت في الموقع</small>
                    </div>
                    <div class="form-group">
                        <label>API Key</label>
                        <input type="password" name="api_key" value="{{ ai.api_key }}" placeholder="sk-... or xai-...">
                    </div>
                    <div class="form-row">
                        <div class="form-group"><label>Model</label><input type="text" name="model" value="{{ ai.model }}" placeholder="grok-4.7 / gpt-4o-mini"></div>
                        <div class="form-group"><label>Base URL</label><input type="text" name="base_url" value="{{ ai.base_url }}" placeholder="https://api.x.ai/v1"></div>
                    </div>
                    <div class="form-group">
                        <label>System Prompt</label>
                        <textarea name="system_prompt" style="min-height:110px;">{{ ai.system_prompt }}</textarea>
                    </div>
                    <div class="form-actions"><button type="submit" class="btn btn-primary">💾 Save AI Settings</button></div>
                </form>
                <p style="margin-top:16px;color:var(--text-muted);font-size:0.9rem;">
                    يدعم OpenAI-compatible APIs (xAI / OpenAI / Groq ...). ضع المفتاح وفعّل النموذج لتظهر أيقونة AI في الموقع.
                </p>
            </div>

            {% elif page == 'courses' %}
            <div class="admin-header"><h1>Courses</h1><a href="/admin/courses/add" class="btn btn-primary">➕ Add Course</a></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                <table class="table">
                    <thead><tr><th>Title</th><th>Description</th><th>Actions</th></tr></thead>
                    <tbody>
                    {% for c in courses %}
                        <tr>
                            <td>{{ c.title }}</td>
                            <td>{{ c.description[:50] }}...</td>
                            <td>
                                <a href="/admin/courses/edit/{{ c.id }}" class="btn btn-sm btn-outline">Edit</a>
                                <a href="/admin/courses/delete/{{ c.id }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</a>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>

            {% elif page == 'course_form' %}
            <div class="admin-header"><h1>{{ 'Edit Course' if course else 'Add Course' }}</h1></div>
            <div class="admin-card">
                <form method="POST">
                    <div class="form-group"><label>Title (AR)</label><input type="text" name="title" value="{{ course.title if course else '' }}" required></div>
                    <div class="form-group"><label>Title (EN)</label><input type="text" name="title_en" value="{{ course.title_en if course else '' }}"></div>
                    <div class="form-group"><label>Description (AR)</label><textarea name="description">{{ course.description if course else '' }}</textarea></div>
                    <div class="form-group"><label>Description (EN)</label><textarea name="description_en">{{ course.description_en if course else '' }}</textarea></div>
                    <div class="form-group"><label>Video URL (optional)</label><input type="url" name="video_url" value="{{ course.video_url if course else '' }}"></div>
                    <div class="form-group"><label>Content (محتوى الكورس الكامل)</label><textarea name="content" style="min-height:150px;">{{ course.content if course else '' }}</textarea></div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">💾 Save</button>
                        <a href="/admin/courses" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>

            {% elif page == 'videos' %}
            <div class="admin-header"><h1>فيديوهات تعليمية</h1><a href="/admin/videos/add" class="btn btn-primary">➕ إضافة فيديو</a></div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}{% for category, msg in messages %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                {% if videos %}
                <table class="table">
                    <thead><tr><th>العنوان</th><th>النوع</th><th>Actions</th></tr></thead>
                    <tbody>
                    {% for v in videos %}
                        <tr>
                            <td>{{ v.title }}</td>
                            <td>{% if v.file_path %}ملف محلي{% elif v.embed_url or v.video_url %}رابط{% else %}-{% endif %}</td>
                            <td>
                                <a href="/admin/videos/delete/{{ v.id }}" class="btn btn-sm btn-danger" onclick="return confirm('حذف؟')">Delete</a>
                            </td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p style="color:var(--text-muted);text-align:center;padding:30px;">لا توجد فيديوهات بعد. أضف فيديو عبر رابط يوتيوب أو رفع ملف.</p>
                {% endif %}
            </div>

            {% elif page == 'video_form' %}
            <div class="admin-header"><h1>إضافة فيديو تعليمي</h1></div>
            <div class="admin-card">
                <form method="POST" enctype="multipart/form-data">
                    <div class="form-group"><label>العنوان (AR)</label><input type="text" name="title" required></div>
                    <div class="form-group"><label>العنوان (EN)</label><input type="text" name="title_en"></div>
                    <div class="form-group"><label>الوصف (AR)</label><textarea name="description"></textarea></div>
                    <div class="form-group"><label>الوصف (EN)</label><textarea name="description_en"></textarea></div>
                    <div class="form-group">
                        <label>رابط يوتيوب (أو أي رابط فيديو)</label>
                        <input type="url" name="video_url" placeholder="https://www.youtube.com/watch?v=...">
                        <small style="color:var(--text-muted);">يُفضّل رابط يوتيوب — سيتم تحويله تلقائياً لـ embed</small>
                    </div>
                    <div class="form-group">
                        <label>أو ارفع ملف فيديو (mp4, webm, mov...)</label>
                        <input type="file" name="video_file" accept="video/*">
                        <small style="color:var(--text-muted);">الحد الأقصى ~200MB</small>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">💾 حفظ</button>
                        <a href="/admin/videos" class="btn btn-outline">إلغاء</a>
                    </div>
                </form>
            </div>

            {% elif page == 'messages' %}
            <div class="admin-header"><h1>Incoming Messages</h1></div>
            {% with messages_flash = get_flashed_messages(with_categories=true) %}
                {% if messages_flash %}{% for category, msg in messages_flash %}<div class="alert alert-{{ category }}">{{ msg }}</div>{% endfor %}{% endif %}
            {% endwith %}
            <div class="admin-card">
                {% if messages %}
                <table class="table">
                    <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Message</th><th>Date</th><th></th></tr></thead>
                    <tbody>
                    {% for m in messages|reverse %}
                        <tr>
                            <td>{{ m.name }}</td>
                            <td><a href="mailto:{{ m.email }}">{{ m.email }}</a></td>
                            <td><a href="https://wa.me/2{{ m.phone }}" target="_blank">{{ m.phone }}</a></td>
                            <td>{{ m.message }}</td>
                            <td>{{ m.date }}</td>
                            <td><a href="/admin/messages/delete/{{ m.id }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">🗑️</a></td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p style="color:var(--text-muted);text-align:center;padding:40px;">No messages yet.</p>
                {% endif %}
            </div>
            {% endif %}
        </main>
    </div>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route("/")
def home():
    videos = get_videos()
    for v in videos:
        if v.get("video_url") and not v.get("embed_url") and not v.get("file_path"):
            v["embed_url"] = youtube_embed(v["video_url"])
    return render_template_string(
        HOME_TEMPLATE,
        site=get_site(),
        services=get_services(),
        courses=get_courses(),
        videos=videos,
        css=BASE_CSS,
        year=datetime.now().year,
        ai=get_ai()
    )


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()
    if not all([name, email, phone, message]):
        flash("Please fill all fields / يرجى ملء جميع الحقول", "error")
        return redirect(url_for("home") + "#contact")
    messages = get_messages()
    new_id = max([m.get("id", 0) for m in messages], default=0) + 1
    messages.append({
        "id": new_id, "name": name, "email": email, "phone": phone,
        "message": message, "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_json(MESSAGES_FILE, messages)
    flash("Message sent successfully! / تم إرسال رسالتك بنجاح!", "success")
    return redirect(url_for("home") + "#contact")


@app.route("/api/ai", methods=["POST"])
def api_ai():
    data = request.get_json() or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "اكتب سؤالك"})
    ai = get_ai()
    if ai.get("enabled") and ai.get("api_key"):
        reply = call_openai(
            [{"role": "system", "content": ai.get("system_prompt", "")}, {"role": "user", "content": msg}],
            ai
        )
        if reply:
            return jsonify({"reply": reply})
        return jsonify({"reply": "تعذر الاتصال بنموذج الـ AI. تحقق من المفتاح والإعدادات."})
    return jsonify({"reply": "الـ AI غير مفعّل حالياً. تواصل على واتساب: 01060662414"})


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    data = request.get_json() or {}
    user_msg = (data.get("message") or "").strip().lower()
    lang = data.get("lang", "ar")
    if not user_msg:
        return jsonify({"reply": "Please type your question." if lang == "en" else "من فضلك اكتب سؤالك."})

    chatbot = get_chatbot()
    site = get_site()
    ai_settings = get_ai()

    best_match = None
    best_score = 0
    for item in chatbot:
        q_ar = (item.get("question") or "").lower()
        q_en = (item.get("question_en") or "").lower()
        for q in [q_ar, q_en]:
            if not q:
                continue
            if q in user_msg or user_msg in q:
                score = len(q)
                if score > best_score:
                    best_score = score
                    best_match = item
            else:
                q_words = set(q.split())
                u_words = set(user_msg.split())
                common = q_words & u_words
                if common and len(common) > best_score:
                    best_score = len(common)
                    best_match = item

    if best_match and best_score > 0:
        if lang == "en" and best_match.get("answer_en"):
            return jsonify({"reply": best_match["answer_en"]})
        return jsonify({"reply": best_match["answer"]})

    if ai_settings.get("enabled") and ai_settings.get("api_key"):
        system = ai_settings.get("system_prompt", DEFAULT_AI["system_prompt"])
        services_text = "\n".join([f"- {s['title']}: {s['description']}" for s in get_services()])
        system += f"\n\nخدمات الشركة:\n{services_text}\nالهاتف: {site.get('phone')}"
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]
        ai_reply = call_openai(messages, ai_settings)
        if ai_reply:
            return jsonify({"reply": ai_reply})

    wa = site.get("whatsapp", "01060662414")
    if lang == "en":
        return jsonify({"reply": f"Sorry, I couldn't find an answer.\nPlease contact us on WhatsApp:\n📱 {wa}"})
    return jsonify({"reply": f"عذراً، لم أجد إجابة مناسبة.\nتواصل معنا عبر واتساب:\n📱 {wa}"})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "123456":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password", "error")
    return render_template_string(ADMIN_LOGIN_TEMPLATE, css=BASE_CSS)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


def _admin_ctx(page, **extra):
    ctx = dict(
        page=page, site=get_site(), services=get_services(),
        chatbot=get_chatbot(), messages=get_messages(),
        ai=get_ai(), courses=get_courses(), videos=get_videos(),
        css=BASE_CSS
    )
    ctx.update(extra)
    return ctx


@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("dashboard"))


@app.route("/admin/site", methods=["GET", "POST"])
@admin_required
def admin_site():
    if request.method == "POST":
        site = get_site()
        for key in ["company_name_ar", "company_name", "hero_title", "hero_title_en",
                    "hero_subtitle", "hero_subtitle_en", "about_title", "about_title_en",
                    "about_text", "about_text_en", "phone", "whatsapp", "email", "facebook",
                    "youtube", "primary_color", "secondary_color", "accent_color"]:
            val = request.form.get(key)
            if val is not None:
                site[key] = val
        save_json(SITE_FILE, site)
        flash("Saved successfully", "success")
        return redirect(url_for("admin_site"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("site"))


@app.route("/admin/services")
@admin_required
def admin_services():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("services"))


@app.route("/admin/services/add", methods=["GET", "POST"])
@admin_required
def admin_service_add():
    if request.method == "POST":
        services = get_services()
        new_id = max([s.get("id", 0) for s in services], default=0) + 1
        services.append({
            "id": new_id,
            "title": request.form.get("title", "").strip(),
            "title_en": request.form.get("title_en", "").strip(),
            "icon": request.form.get("icon", "🔧").strip(),
            "description": request.form.get("description", "").strip(),
            "description_en": request.form.get("description_en", "").strip(),
            "details": request.form.get("details", "").strip(),
            "details_en": request.form.get("details_en", "").strip()
        })
        save_json(SERVICES_FILE, services)
        flash("Service added", "success")
        return redirect(url_for("admin_services"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("service_form", service=None))


@app.route("/admin/services/edit/<int:sid>", methods=["GET", "POST"])
@admin_required
def admin_service_edit(sid):
    services = get_services()
    service = next((s for s in services if s["id"] == sid), None)
    if not service:
        flash("Not found", "error")
        return redirect(url_for("admin_services"))
    if request.method == "POST":
        for key in ["title", "title_en", "icon", "description", "description_en", "details", "details_en"]:
            service[key] = request.form.get(key, "").strip()
        save_json(SERVICES_FILE, services)
        flash("Updated", "success")
        return redirect(url_for("admin_services"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("service_form", service=service))


@app.route("/admin/services/delete/<int:sid>")
@admin_required
def admin_service_delete(sid):
    services = [s for s in get_services() if s["id"] != sid]
    save_json(SERVICES_FILE, services)
    flash("Deleted", "success")
    return redirect(url_for("admin_services"))


@app.route("/admin/chatbot")
@admin_required
def admin_chatbot():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("chatbot"))


@app.route("/admin/chatbot/add", methods=["GET", "POST"])
@admin_required
def admin_chatbot_add():
    if request.method == "POST":
        chatbot = get_chatbot()
        new_id = max([c.get("id", 0) for c in chatbot], default=0) + 1
        chatbot.append({
            "id": new_id,
            "question": request.form.get("question", "").strip(),
            "question_en": request.form.get("question_en", "").strip(),
            "answer": request.form.get("answer", "").strip(),
            "answer_en": request.form.get("answer_en", "").strip()
        })
        save_json(CHATBOT_FILE, chatbot)
        flash("Added", "success")
        return redirect(url_for("admin_chatbot"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("chatbot_form", item=None))


@app.route("/admin/chatbot/edit/<int:cid>", methods=["GET", "POST"])
@admin_required
def admin_chatbot_edit(cid):
    chatbot = get_chatbot()
    item = next((c for c in chatbot if c["id"] == cid), None)
    if not item:
        flash("Not found", "error")
        return redirect(url_for("admin_chatbot"))
    if request.method == "POST":
        for key in ["question", "question_en", "answer", "answer_en"]:
            item[key] = request.form.get(key, "").strip()
        save_json(CHATBOT_FILE, chatbot)
        flash("Updated", "success")
        return redirect(url_for("admin_chatbot"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("chatbot_form", item=item))


@app.route("/admin/chatbot/delete/<int:cid>")
@admin_required
def admin_chatbot_delete(cid):
    chatbot = [c for c in get_chatbot() if c["id"] != cid]
    save_json(CHATBOT_FILE, chatbot)
    flash("Deleted", "success")
    return redirect(url_for("admin_chatbot"))


@app.route("/admin/ai", methods=["GET", "POST"])
@admin_required
def admin_ai():
    if request.method == "POST":
        ai = get_ai()
        ai["enabled"] = "enabled" in request.form
        ai["api_key"] = request.form.get("api_key", "").strip()
        ai["model"] = request.form.get("model", "gpt-4o-mini").strip()
        ai["base_url"] = request.form.get("base_url", "https://api.openai.com/v1").strip()
        ai["system_prompt"] = request.form.get("system_prompt", "").strip()
        save_json(AI_FILE, ai)
        flash("AI settings saved successfully", "success")
        return redirect(url_for("admin_ai"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("ai"))


@app.route("/admin/messages")
@admin_required
def admin_messages():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("messages"))


@app.route("/admin/messages/delete/<int:mid>")
@admin_required
def admin_message_delete(mid):
    messages = [m for m in get_messages() if m["id"] != mid]
    save_json(MESSAGES_FILE, messages)
    flash("Deleted", "success")
    return redirect(url_for("admin_messages"))


@app.route("/admin/courses")
@admin_required
def admin_courses():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("courses"))


@app.route("/admin/courses/add", methods=["GET", "POST"])
@admin_required
def admin_course_add():
    if request.method == "POST":
        courses = get_courses()
        new_id = max([c.get("id", 0) for c in courses], default=0) + 1
        courses.append({
            "id": new_id,
            "title": request.form.get("title", "").strip(),
            "title_en": request.form.get("title_en", "").strip(),
            "description": request.form.get("description", "").strip(),
            "description_en": request.form.get("description_en", "").strip(),
            "video_url": request.form.get("video_url", "").strip(),
            "content": request.form.get("content", "").strip()
        })
        save_json(COURSES_FILE, courses)
        flash("Course added", "success")
        return redirect(url_for("admin_courses"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("course_form", course=None))


@app.route("/admin/courses/edit/<int:cid>", methods=["GET", "POST"])
@admin_required
def admin_course_edit(cid):
    courses = get_courses()
    course = next((c for c in courses if c["id"] == cid), None)
    if not course:
        flash("Not found", "error")
        return redirect(url_for("admin_courses"))
    if request.method == "POST":
        for key in ["title", "title_en", "description", "description_en", "video_url", "content"]:
            course[key] = request.form.get(key, "").strip()
        save_json(COURSES_FILE, courses)
        flash("Updated", "success")
        return redirect(url_for("admin_courses"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("course_form", course=course))


@app.route("/admin/courses/delete/<int:cid>")
@admin_required
def admin_course_delete(cid):
    courses = [c for c in get_courses() if c["id"] != cid]
    save_json(COURSES_FILE, courses)
    flash("Deleted", "success")
    return redirect(url_for("admin_courses"))


@app.route("/admin/videos")
@admin_required
def admin_videos():
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("videos"))


@app.route("/admin/videos/add", methods=["GET", "POST"])
@admin_required
def admin_video_add():
    if request.method == "POST":
        videos = get_videos()
        new_id = max([v.get("id", 0) for v in videos], default=0) + 1
        video_url = request.form.get("video_url", "").strip()
        file_path = ""
        f = request.files.get("video_file")
        if f and f.filename:
            ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
            if ext in ALLOWED_VIDEO_EXT:
                fname = secure_filename(f"{new_id}_{f.filename}")
                f.save(os.path.join(VIDEOS_DIR, fname))
                file_path = fname
            else:
                flash("صيغة الفيديو غير مدعومة", "error")
                return redirect(url_for("admin_video_add"))
        if not video_url and not file_path:
            flash("أدخل رابط يوتيوب أو ارفع ملفاً", "error")
            return redirect(url_for("admin_video_add"))
        videos.append({
            "id": new_id,
            "title": request.form.get("title", "").strip(),
            "title_en": request.form.get("title_en", "").strip(),
            "description": request.form.get("description", "").strip(),
            "description_en": request.form.get("description_en", "").strip(),
            "video_url": video_url,
            "embed_url": youtube_embed(video_url) if video_url else "",
            "file_path": file_path
        })
        save_json(VIDEOS_FILE, videos)
        flash("تم إضافة الفيديو", "success")
        return redirect(url_for("admin_videos"))
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, **_admin_ctx("video_form"))


@app.route("/admin/videos/delete/<int:vid>")
@admin_required
def admin_video_delete(vid):
    videos = get_videos()
    for v in videos:
        if v["id"] == vid and v.get("file_path"):
            fp = os.path.join(VIDEOS_DIR, v["file_path"])
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass
    videos = [v for v in videos if v["id"] != vid]
    save_json(VIDEOS_FILE, videos)
    flash("Deleted", "success")
    return redirect(url_for("admin_videos"))


if __name__ == "__main__":
    get_site()
    get_services()
    get_chatbot()
    get_messages()
    get_ai()
    get_courses()
    get_videos()
    print("=" * 60)
    print("  Options Technology — Cyberpunk HUD v2")
    print("  http://127.0.0.1:5000")
    print("  Admin: http://127.0.0.1:5000/admin/login")
    print("  User: admin | Pass: 123456")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
