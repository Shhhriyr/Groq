# Groq AI Chat Pro

https://drive.google.com/file/d/1CYVzdHX3I46XkxWC70RZYaz0P37z6k0F/view?usp=sharing

[English](#english) | [فارسی](#فارسی)

---

## English

Advanced GUI chat application powered by Groq AI, featuring a sleek Black & Orange theme.

### Features
- **Dynamic Model Fetching**: Automatically retrieves available models directly from Groq API.
- **Vision Support (Llama)**: Upload images and chat about their content.
- **Chat Memory**: Optional context memory (sends last 3 message pairs).
- **System Prompt**: Custom instructions for the AI model.
- **Dark Mode**: Professional Groq-branded UI.

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python groq_gui.py
   ```

### Build EXE
To create a standalone executable:
```bash
pyinstaller --onefile --noconsole --icon=favicon.ico --name "groq_gui" groq_gui.py
```

---

## فارسی

برنامه چت گرافیکی پیشرفته با استفاده از هوش مصنوعی Groq، با طراحی اختصاصی مشکی و نارنجی.

### قابلیت‌ها
- **دریافت خودکار مدل‌ها**: دریافت لیست مدل‌های فعال مستقیماً از API اختصاصی Groq.
- **پشتیبانی از تصویر (Vision)**: قابلیت آپلود تصویر و پرسش درباره محتوای آن در مدل‌های Llama.
- **حافظه چت**: امکان ارسال تاریخچه (۳ جفت پیام آخر) برای حفظ سیاق گفتگو.
- **دستورالعمل سیستمی (System Prompt)**: تعیین رفتار و نقش هوش مصنوعی.
- **تم اختصاصی**: رابط کاربری حرفه‌ای هماهنگ با برند Groq.

### نصب و اجرا
۱. نصب نیازمندی‌ها:
   ```bash
   pip install -r requirements.txt
   ```
۲. اجرای برنامه:
   ```bash
   python groq_gui.py
   ```

### ساخت فایل EXE
برای ساخت فایل اجرایی تک‌فایله:
```bash
pyinstaller --onefile --noconsole --icon=favicon.ico --name "groq_gui" groq_gui.py
```
