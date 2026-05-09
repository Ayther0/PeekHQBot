import logging
import random
from datetime import datetime, timedelta
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import *

logging.basicConfig(level=logging.INFO)

TOKEN = "8673666605:AAGitSny8hFxHehQX4K2lVR-dKSCUue-KuI"
ADMIN_ID = 8601067589

# ═══════════════════════════
# Web Server
# ═══════════════════════════

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'StudyClub Bot is running!')
    def log_message(self, format, *args):
        pass

Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), Handler).serve_forever(), daemon=True).start()

# ═══════════════════════════
# الترجمات
# ═══════════════════════════

TEXTS = {
    'ar': {
        'choose_lang': "أهلاً! 👋\n\nاختر لغتك:",
        'charter': """🏛️ *أهلاً بك في نادي الدراسة*

"هنا لا يُطلب منك أن تكون كاملًا، بل أن تتوه قليلًا حتى تدرك أن الفهم لا يأتي دفعة واحدة، بل يُولد من الفوضى التي تعيشها وأنت تحاول أن تصبح شيئًا مختلفًا."

*قواعد النادي:*

1️⃣ عند دخولك للنادي، انتزع مشاكلك العاطفية والنفسية؛ فهي لا تنفعك هنا، ومستقبلك أهم من أن يضيع في زحام مشاعرك.

2️⃣ كل نقطة تجمعها في هذا البوت هي خطوة تقربك من حلمك؛ عامل نقاطك كأنها رصيدك في طريقك نحو السيادة.

3️⃣ إذا كان هذا يومك الأول في النادي، فعليك أن تبدأ الآن.. وبصمت.""",
        'agree_btn': "أوافق على ميثاق النادي ✅",
        'ask_name': "ما اسمك؟ ✍️",
        'ask_specialty': "ما تخصصك أو حلمك؟ 🎯",
        'welcome_done': "مرحباً {name}! 🏛️\n\nأنت الآن عضو في نادي الدراسة.\nرتبتك الحالية: {rank}\nنقاطك: {points}",
        'main_menu': "🏛️ *نادي الدراسة*\n\n👤 {name} | {rank}\n💰 النقاط: {points}",
        'solo_session': "🧘‍♂️ *السشن المنفرد*\n\nاختر نظام دراستك اليومي:",
        'random_session': "👥 *السشن العشوائي*\n\nستدرس مع 9 مكافحين من حول العالم!\n\nاختر مدة دراستك:",
        'challenge_friend': "⚔️ *تحدي صديق*\n\nأرسل معرف التحدي الخاص بك لصديقك:\n\n🆔 معرفك: `{id}`\n\nأو أدخل معرف صديقك للتحدي:",
        'black_market': "🕶️ *السوق السوداء*\n\n💰 رصيدك: {points} نقطة\n\nاختر ما تريد شراءه:",
        'guide': "📖 *دليل النادي*",
        'session_started': "📚 *بدأ السشن!*\n\n⏰ البداية: {start}\n🏁 النهاية: {end}\n\nالحمدلله دائماً 🤍",
        'break_time': "☕ *وقت الاستراحة!*\n\n⏱️ {minutes} دقيقة\n\nأستغفر الله 🤍",
        'session_done': "🎯 *انتهى السشن!*\n\n✅ أكملت {hours} ساعة\n💰 ربحت {points} نقطة\n\nبالتوفيق 🤍",
        'withdrew': "✅ تم الانسحاب من السشن\n💰 ربحت {points} نقطة على ما أكملته",
        'no_session': "❌ ما عندك سشن نشط",
        'tasks_ask': "📝 هل تريد إضافة مهام لسشنك؟",
        'tasks_add': "أرسل مهامك الآن (كل مهمة في رسالة منفصلة)\nعند الانتهاء اكتب: *تم*",
        'task_added': "✅ تمت إضافة المهمة",
        'tasks_done': "✅ تم حفظ المهام! بالتوفيق 🤍",
        'task_complete': "✅ ممتاز! اكتمل: {task}",
        'all_tasks_done': "🎉 أكملت كل المهام! +2 نقطة إضافية!",
        'fajr_msg': "🌅 صباح الخير {name}!\n\nيوم جديد، فرصة جديدة.\nاستعن بالله ولا تعجز 🤍",
        'weekly_msg': "💭 {name}، تذكر..\n\nمشاكلك العاطفية لن تحل مستقبلك.\nركز على هدفك — النادي ينتظرك. 🏛️",
        'session_msg': "✨ تذكر لماذا بدأت..\nالقمة تنتظرك. 🏛️",
        'bleed_warning': "⚠️ {name}! بقي 4 ساعات ويبدأ رصيدك بالنزيف!\nأنقذ نفسك بسشن دراسي الآن 📚",
        'rank_up': "🎉 تهانينا {name}! ترقيت إلى رتبة *{rank}*!\n+5 نقاط مكافأة! 🎁",
    },
    'en': {
        'choose_lang': "Hello! 👋\n\nChoose your language:",
        'charter': """🏛️ *Welcome to Study Club*

"You are not required to be perfect here. You are allowed to be lost for a while — until you realize that understanding doesn't come all at once, but is born from the chaos you live through as you try to become something different."

*Club Rules:*

1️⃣ When you enter the club, leave your emotional problems at the door. They won't help you here, and your future is too important to be lost in the noise of your feelings.

2️⃣ Every point you earn in this bot is a step closer to your dream. Treat your points like your currency on the road to mastery.

3️⃣ If this is your first day in the club, you must start now... in silence.""",
        'agree_btn': "I agree to the Club Charter ✅",
        'ask_name': "What's your name? ✍️",
        'ask_specialty': "What's your specialty or dream? 🎯",
        'welcome_done': "Welcome {name}! 🏛️\n\nYou are now a member of Study Club.\nRank: {rank}\nPoints: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 Points: {points}",
        'solo_session': "🧘‍♂️ *Solo Session*\n\nChoose your daily study plan:",
        'random_session': "👥 *Random Session*\n\nYou'll study with 9 fighters from around the world!\n\nChoose duration:",
        'challenge_friend': "⚔️ *Friend Challenge*\n\nSend your challenge ID to your friend:\n\n🆔 Your ID: `{id}`\n\nOr enter your friend's ID to challenge them:",
        'black_market': "🕶️ *Black Market*\n\n💰 Balance: {points} points\n\nChoose what to buy:",
        'guide': "📖 *Club Guide*",
        'session_started': "📚 *Session Started!*\n\n⏰ Start: {start}\n🏁 End: {end}\n\nAlhamdulillah 🤍",
        'break_time': "☕ *Break Time!*\n\n⏱️ {minutes} minutes\n\nAstaghfirullah 🤍",
        'session_done': "🎯 *Session Complete!*\n\n✅ Completed {hours} hours\n💰 Earned {points} points\n\nGood luck 🤍",
        'withdrew': "✅ Withdrew from session\n💰 Earned {points} points for what you completed",
        'no_session': "❌ No active session",
        'tasks_ask': "📝 Do you want to add tasks to your session?",
        'tasks_add': "Send your tasks now (one task per message)\nWhen done, type: *done*",
        'task_added': "✅ Task added",
        'tasks_done': "✅ Tasks saved! Good luck 🤍",
        'task_complete': "✅ Completed: {task}",
        'all_tasks_done': "🎉 All tasks completed! +2 bonus points!",
        'fajr_msg': "🌅 Good morning {name}!\n\nNew day, new opportunity.\nSeek help from Allah and don't be lazy 🤍",
        'weekly_msg': "💭 {name}, remember..\n\nYour emotional problems won't solve your future.\nFocus on your goal — the club awaits. 🏛️",
        'session_msg': "✨ Remember why you started..\nThe top awaits you. 🏛️",
        'bleed_warning': "⚠️ {name}! 4 hours left before your points start bleeding!\nSave yourself with a study session now 📚",
        'rank_up': "🎉 Congratulations {name}! You've been promoted to *{rank}*!\n+5 bonus points! 🎁",
    },
    'ru': {
        'choose_lang': "Привет! 👋\n\nВыберите язык:",
        'charter': "🏛️ *Добро пожаловать в Study Club*\n\nПравила клуба:\n\n1️⃣ Оставьте проблемы за дверью.\n2️⃣ Каждое очко приближает вас к мечте.\n3️⃣ Начните сейчас... в тишине.",
        'agree_btn': "Я согласен с уставом ✅",
        'ask_name': "Как вас зовут? ✍️",
        'ask_specialty': "Ваша специальность или мечта? 🎯",
        'welcome_done': "Добро пожаловать {name}! 🏛️\n\nРанг: {rank}\nОчки: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 Очки: {points}",
        'solo_session': "🧘‍♂️ *Одиночная сессия*\n\nВыберите план:",
        'random_session': "👥 *Случайная сессия*\n\nВы будете учиться с 9 бойцами!\n\nВыберите продолжительность:",
        'challenge_friend': "⚔️ *Вызов другу*\n\n🆔 Ваш ID: `{id}`\n\nИли введите ID друга:",
        'black_market': "🕶️ *Чёрный рынок*\n\n💰 Баланс: {points} очков",
        'guide': "📖 *Руководство клуба*",
        'session_started': "📚 *Сессия началась!*\n\n⏰ Начало: {start}\n🏁 Конец: {end}",
        'break_time': "☕ *Перерыв!*\n\n⏱️ {minutes} минут",
        'session_done': "🎯 *Сессия завершена!*\n\n✅ {hours} часов\n💰 +{points} очков",
        'withdrew': "✅ Вышли из сессии\n💰 +{points} очков",
        'no_session': "❌ Нет активной сессии",
        'tasks_ask': "📝 Добавить задачи?",
        'tasks_add': "Отправьте задачи (по одной)\nКогда закончите, напишите: *done*",
        'task_added': "✅ Задача добавлена",
        'tasks_done': "✅ Задачи сохранены!",
        'task_complete': "✅ Выполнено: {task}",
        'all_tasks_done': "🎉 Все задачи выполнены! +2 очка!",
        'fajr_msg': "🌅 Доброе утро {name}!\n\nНовый день, новая возможность 🤍",
        'weekly_msg': "💭 {name}, помните..\n\nФокусируйтесь на цели 🏛️",
        'session_msg': "✨ Помните, зачем начали..\nВершина ждёт вас. 🏛️",
        'bleed_warning': "⚠️ {name}! Осталось 4 часа до потери очков!\nНачните сессию сейчас 📚",
        'rank_up': "🎉 Поздравляем {name}! Новый ранг: *{rank}*!\n+5 очков! 🎁",
    },
    'tr': {
        'choose_lang': "Merhaba! 👋\n\nDilini seç:",
        'charter': "🏛️ *Study Club'a Hoş Geldiniz*\n\nKulüp Kuralları:\n\n1️⃣ Duygusal sorunlarını kapıda bırak.\n2️⃣ Her puan seni hayaline yaklaştırır.\n3️⃣ Şimdi başla... sessizce.",
        'agree_btn': "Tüzüğü kabul ediyorum ✅",
        'ask_name': "Adın ne? ✍️",
        'ask_specialty': "Uzmanlık alanın veya hayalin? 🎯",
        'welcome_done': "Hoş geldin {name}! 🏛️\n\nRütbe: {rank}\nPuan: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 Puan: {points}",
        'solo_session': "🧘‍♂️ *Bireysel Seans*\n\nGünlük planını seç:",
        'random_session': "👥 *Rastgele Seans*\n\n9 savaşçıyla çalışacaksın!\n\nSüreyi seç:",
        'challenge_friend': "⚔️ *Arkadaş Meydan Okuması*\n\n🆔 ID'n: `{id}`\n\nYa da arkadaşının ID'sini gir:",
        'black_market': "🕶️ *Kara Pazar*\n\n💰 Bakiye: {points} puan",
        'guide': "📖 *Kulüp Rehberi*",
        'session_started': "📚 *Seans Başladı!*\n\n⏰ Başlangıç: {start}\n🏁 Bitiş: {end}",
        'break_time': "☕ *Mola!*\n\n⏱️ {minutes} dakika",
        'session_done': "🎯 *Seans Tamamlandı!*\n\n✅ {hours} saat\n💰 +{points} puan",
        'withdrew': "✅ Seanstan çıkıldı\n💰 +{points} puan",
        'no_session': "❌ Aktif seans yok",
        'tasks_ask': "📝 Görev eklemek ister misin?",
        'tasks_add': "Görevleri gönder (her biri ayrı mesajda)\nBitince yaz: *done*",
        'task_added': "✅ Görev eklendi",
        'tasks_done': "✅ Görevler kaydedildi!",
        'task_complete': "✅ Tamamlandı: {task}",
        'all_tasks_done': "🎉 Tüm görevler tamamlandı! +2 puan!",
        'fajr_msg': "🌅 Günaydın {name}!\n\nYeni gün, yeni fırsat 🤍",
        'weekly_msg': "💭 {name}, hatırla..\n\nHedefine odaklan 🏛️",
        'session_msg': "✨ Neden başladığını hatırla..\nZirve seni bekliyor. 🏛️",
        'bleed_warning': "⚠️ {name}! Puan kaybına 4 saat kaldı!\nŞimdi çalış 📚",
        'rank_up': "🎉 Tebrikler {name}! Yeni rütbe: *{rank}*!\n+5 puan! 🎁",
    },
    'fa': {
        'choose_lang': "سلام! 👋\n\nزبان خود را انتخاب کنید:",
        'charter': "🏛️ *به Study Club خوش آمدید*\n\nقوانین:\n\n1️⃣ مشکلات احساسی را کنار بگذارید.\n2️⃣ هر امتیاز شما را به رویایتان نزدیک می‌کند.\n3️⃣ همین الان شروع کنید... در سکوت.",
        'agree_btn': "با منشور موافقم ✅",
        'ask_name': "اسمت چیه؟ ✍️",
        'ask_specialty': "تخصص یا رویایت چیست؟ 🎯",
        'welcome_done': "خوش آمدی {name}! 🏛️\n\nرتبه: {rank}\nامتیاز: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 امتیاز: {points}",
        'solo_session': "🧘‍♂️ *سشن انفرادی*\n\nبرنامه روزانه‌ات را انتخاب کن:",
        'random_session': "👥 *سشن تصادفی*\n\nبا ۹ نفر دیگر مطالعه می‌کنی!\n\nمدت را انتخاب کن:",
        'challenge_friend': "⚔️ *چالش دوست*\n\n🆔 شناسه شما: `{id}`\n\nیا شناسه دوستت را وارد کن:",
        'black_market': "🕶️ *بازار سیاه*\n\n💰 موجودی: {points} امتیاز",
        'guide': "📖 *راهنمای باشگاه*",
        'session_started': "📚 *سشن شروع شد!*\n\n⏰ شروع: {start}\n🏁 پایان: {end}",
        'break_time': "☕ *استراحت!*\n\n⏱️ {minutes} دقیقه",
        'session_done': "🎯 *سشن تمام شد!*\n\n✅ {hours} ساعت\n💰 +{points} امتیاز",
        'withdrew': "✅ از سشن خارج شدید\n💰 +{points} امتیاز",
        'no_session': "❌ سشن فعالی وجود ندارد",
        'tasks_ask': "📝 می‌خواهی وظایف اضافه کنی؟",
        'tasks_add': "وظایفت را بفرست\nوقتی تمام شد بنویس: *done*",
        'task_added': "✅ وظیفه اضافه شد",
        'tasks_done': "✅ وظایف ذخیره شد!",
        'task_complete': "✅ انجام شد: {task}",
        'all_tasks_done': "🎉 همه وظایف انجام شد! +2 امتیاز!",
        'fajr_msg': "🌅 صبح بخیر {name}!\n\nروز جدید، فرصت جدید 🤍",
        'weekly_msg': "💭 {name}، یادت باشد..\n\nبر هدفت تمرکز کن 🏛️",
        'session_msg': "✨ یادت باشه چرا شروع کردی..\nقله منتظرته. 🏛️",
        'bleed_warning': "⚠️ {name}! ۴ ساعت تا کسر امتیاز!\nالان مطالعه کن 📚",
        'rank_up': "🎉 تبریک {name}! رتبه جدید: *{rank}*!\n+5 امتیاز! 🎁",
    },
    'hi': {
        'choose_lang': "नमस्ते! 👋\n\nअपनी भाषा चुनें:",
        'charter': "🏛️ *Study Club में आपका स्वागत है*\n\nनियम:\n\n1️⃣ भावनात्मक समस्याएं दरवाजे पर छोड़ें।\n2️⃣ हर पॉइंट आपको सपने के करीब लाता है।\n3️⃣ अभी शुरू करें... चुपचाप।",
        'agree_btn': "मैं चार्टर से सहमत हूं ✅",
        'ask_name': "आपका नाम क्या है? ✍️",
        'ask_specialty': "आपकी विशेषता या सपना? 🎯",
        'welcome_done': "स्वागत है {name}! 🏛️\n\nरैंक: {rank}\nपॉइंट्स: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 पॉइंट्स: {points}",
        'solo_session': "🧘‍♂️ *एकल सत्र*\n\nअपनी योजना चुनें:",
        'random_session': "👥 *रैंडम सत्र*\n\n9 लड़ाकों के साथ पढ़ेंगे!\n\nअवधि चुनें:",
        'challenge_friend': "⚔️ *दोस्त चुनौती*\n\n🆔 आपकी ID: `{id}`\n\nया दोस्त की ID दर्ज करें:",
        'black_market': "🕶️ *ब्लैक मार्केट*\n\n💰 बैलेंस: {points} पॉइंट्स",
        'guide': "📖 *क्लब गाइड*",
        'session_started': "📚 *सत्र शुरू!*\n\n⏰ शुरू: {start}\n🏁 समाप्त: {end}",
        'break_time': "☕ *ब्रेक!*\n\n⏱️ {minutes} मिनट",
        'session_done': "🎯 *सत्र पूर्ण!*\n\n✅ {hours} घंटे\n💰 +{points} पॉइंट्स",
        'withdrew': "✅ सत्र से बाहर\n💰 +{points} पॉइंट्स",
        'no_session': "❌ कोई सक्रिय सत्र नहीं",
        'tasks_ask': "📝 कार्य जोड़ना चाहते हैं?",
        'tasks_add': "अपने कार्य भेजें\nजब हो जाए लिखें: *done*",
        'task_added': "✅ कार्य जोड़ा गया",
        'tasks_done': "✅ कार्य सहेजे गए!",
        'task_complete': "✅ पूर्ण: {task}",
        'all_tasks_done': "🎉 सभी कार्य पूर्ण! +2 पॉइंट्स!",
        'fajr_msg': "🌅 सुप्रभात {name}!\n\nनया दिन, नया अवसर 🤍",
        'weekly_msg': "💭 {name}, याद रखें..\n\nअपने लक्ष्य पर ध्यान दें 🏛️",
        'session_msg': "✨ याद करें क्यों शुरू किया..\nशिखर आपका इंतजार कर रहा है। 🏛️",
        'bleed_warning': "⚠️ {name}! 4 घंटे बाकी!\nअभी पढ़ें 📚",
        'rank_up': "🎉 बधाई {name}! नई रैंक: *{rank}*!\n+5 पॉइंट्स! 🎁",
    },
    'uz': {
        'choose_lang': "Salom! 👋\n\nTilni tanlang:",
        'charter': "🏛️ *Study Club'ga xush kelibsiz*\n\nQoidalar:\n\n1️⃣ Hissiy muammolaringizni eshik oldida qoldiring.\n2️⃣ Har bir ball sizni orzuingizga yaqinlashtiradi.\n3️⃣ Hoziroq boshlang... jimgina.",
        'agree_btn': "Nizomga roziman ✅",
        'ask_name': "Ismingiz nima? ✍️",
        'ask_specialty': "Mutaxassislik yoki orzuingiz? 🎯",
        'welcome_done': "Xush kelibsiz {name}! 🏛️\n\nDaraja: {rank}\nBallar: {points}",
        'main_menu': "🏛️ *Study Club*\n\n👤 {name} | {rank}\n💰 Ballar: {points}",
        'solo_session': "🧘‍♂️ *Yakka sessiya*\n\nKunlik rejangizni tanlang:",
        'random_session': "👥 *Tasodifiy sessiya*\n\n9 kurashchi bilan o'qiysiz!\n\nMuddat tanlang:",
        'challenge_friend': "⚔️ *Do'stga chaqiruv*\n\n🆔 Sizning ID: `{id}`\n\nYoki do'stingiz ID'sini kiriting:",
        'black_market': "🕶️ *Qora bozor*\n\n💰 Balans: {points} ball",
        'guide': "📖 *Klub qo'llanmasi*",
        'session_started': "📚 *Sessiya boshlandi!*\n\n⏰ Boshlanish: {start}\n🏁 Tugash: {end}",
        'break_time': "☕ *Dam olish!*\n\n⏱️ {minutes} daqiqa",
        'session_done': "🎯 *Sessiya tugadi!*\n\n✅ {hours} soat\n💰 +{points} ball",
        'withdrew': "✅ Sessiyadan chiqildi\n💰 +{points} ball",
        'no_session': "❌ Faol sessiya yo'q",
        'tasks_ask': "📝 Vazifalar qo'shmoqchimisiz?",
        'tasks_add': "Vazifalarni yuboring\nTugagach yozing: *done*",
        'task_added': "✅ Vazifa qo'shildi",
        'tasks_done': "✅ Vazifalar saqlandi!",
        'task_complete': "✅ Bajarildi: {task}",
        'all_tasks_done': "🎉 Barcha vazifalar bajarildi! +2 ball!",
        'fajr_msg': "🌅 Xayrli tong {name}!\n\nYangi kun, yangi imkoniyat 🤍",
        'weekly_msg': "💭 {name}, esla..\n\nMaqsadingga e'tibor qaratgin 🏛️",
        'session_msg': "✨ Nega boshlaganingni esla..\nCho'qqi seni kutmoqda. 🏛️",
        'bleed_warning': "⚠️ {name}! 4 soat qoldi!\nHozir o'qi 📚",
        'rank_up': "🎉 Tabriklar {name}! Yangi daraja: *{rank}*!\n+5 ball! 🎁",
    },
}

# ═══════════════════════════
# بيانات وهمية للسشن العشوائي
# ═══════════════════════════

FAKE_USERS = [
    {"name": "أحمد", "country": "🇮🇶 العراق", "specialty": "طالب صيدلة"},
    {"name": "علي", "country": "🇸🇦 السعودية", "specialty": "طالب هندسة"},
    {"name": "سارة", "country": "🇪🇬 مصر", "specialty": "طالبة طب"},
    {"name": "Max", "country": "🇺🇸 USA", "specialty": "Engineering student"},
    {"name": "Yuki", "country": "🇯🇵 Japan", "specialty": "Medicine student"},
    {"name": "Omar", "country": "🇦🇪 UAE", "specialty": "Law student"},
    {"name": "Lena", "country": "🇷🇺 Russia", "specialty": "Physics student"},
    {"name": "Fatima", "country": "🇲🇦 Morocco", "specialty": "طالبة رياضيات"},
    {"name": "Carlos", "country": "🇧🇷 Brazil", "specialty": "Computer Science"},
]

SESSION_MSGS = [
    "✨ تذكر لماذا بدأت.. القمة تنتظرك. 🏛️",
    "💪 أنت أقوى مما تظن. استمر!",
    "🎯 كل دقيقة الآن تصنع فارقاً في مستقبلك.",
    "🌟 النجاح ليس حظاً، بل ساعات من العمل الصامت.",
    "🔥 لا تتوقف. الآخرون يستريحون — وأنت تتقدم.",
]

def get_lang(user):
    return user[6] if user and user[6] in TEXTS else 'ar'

def get_text(user, key, **kwargs):
    lang = get_lang(user)
    text = TEXTS[lang].get(key, TEXTS['ar'].get(key, ''))
    return text.format(**kwargs) if kwargs else text

def main_keyboard(lang='ar'):
    buttons = [
        [InlineKeyboardButton("🧘‍♂️ سشن منفرد" if lang == 'ar' else "🧘‍♂️ Solo Session", callback_data="menu_solo"),
         InlineKeyboardButton("👥 سشن عشوائي" if lang == 'ar' else "👥 Random Session", callback_data="menu_random")],
        [InlineKeyboardButton("⚔️ تحدي صديق" if lang == 'ar' else "⚔️ Challenge Friend", callback_data="menu_challenge"),
         InlineKeyboardButton("👥 تحدي جماعي" if lang == 'ar' else "👥 Group Challenge", callback_data="menu_group")],
        [InlineKeyboardButton("🕶️ السوق السوداء" if lang == 'ar' else "🕶️ Black Market", callback_data="menu_market"),
         InlineKeyboardButton("📖 دليل النادي" if lang == 'ar' else "📖 Club Guide", callback_data="menu_guide")],
    ]
    return InlineKeyboardMarkup(buttons)

def back_keyboard(lang='ar'):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="go_home")]])

# ═══════════════════════════
# Handlers
# ═══════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tg_username = update.effective_user.username or ""
    user = get_user(user_id)

    if not user:
        add_user(user_id, tg_username)
        user = get_user(user_id)

    lang = get_lang(user)

    if not user[9]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇮🇶 العربية", callback_data="lang_ar"),
             InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
            [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
             InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi")],
            [InlineKeyboardButton("🇺🇿 Uzbek", callback_data="lang_uz")],
        ])
        await update.message.reply_text(TEXTS[lang]['choose_lang'], reply_markup=keyboard)
    else:
        rank = get_rank(user[7])
        await update.message.reply_text(
            get_text(user, 'main_menu', name=user[2], rank=rank, points=user[6]),
            reply_markup=main_keyboard(lang),
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()

    user = get_user(user_id)
    lang = get_lang(user)

    if data.startswith("lang_"):
        chosen_lang = data.split("_")[1]
        update_user(user_id, language=chosen_lang)
        user = get_user(user_id)

        await query.edit_message_text(
            TEXTS[chosen_lang]['charter'],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(TEXTS[chosen_lang]['agree_btn'], callback_data="agree_charter")
            ]]),
            parse_mode='Markdown'
        )

    elif data == "agree_charter":
        context.user_data['step'] = 'ask_name'
        await query.edit_message_text(get_text(user, 'ask_name'))

    elif data == "go_home":
        user = get_user(user_id)
        lang = get_lang(user)
        rank = get_rank(user[7])
        await query.edit_message_text(
            get_text(user, 'main_menu', name=user[2], rank=rank, points=user[6]),
            reply_markup=main_keyboard(lang),
            parse_mode='Markdown'
        )

    elif data == "menu_solo":
        desc = "🧘‍♂️ *السشن المنفرد*\n\nادرس بمفردك بالنظام الذي تختاره.\nكل ساعة = نقطة واحدة.\n\n" if lang == 'ar' else "🧘‍♂️ *Solo Session*\n\nStudy alone with your chosen system.\n1 hour = 1 point.\n\n"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("50د دراسة | 10د استراحة 🕐", callback_data="solo_50_10")],
            [InlineKeyboardButton("2س دراسة | 10د استراحة 🕑", callback_data="solo_120_10")],
            [InlineKeyboardButton("3س دراسة | 10د استراحة 🕒", callback_data="solo_180_10")],
            [InlineKeyboardButton("⚙️ مخصص", callback_data="solo_custom")],
            [InlineKeyboardButton("🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="go_home")]
        ])
        await query.edit_message_text(desc, reply_markup=keyboard, parse_mode='Markdown')

    elif data.startswith("solo_"):
        parts = data.split("_")
        if parts[1] == "custom":
            context.user_data['step'] = 'custom_session'
            await query.edit_message_text("⚙️ أرسل مدة الدراسة بالدقائق (مثال: 90):")
            return

        study_mins = int(parts[1])
        break_mins = int(parts[2])
        context.user_data['session_type'] = 'solo'
        context.user_data['study_mins'] = study_mins
        context.user_data['break_mins'] = break_mins

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 نعم، أضف مهام" if lang == 'ar' else "📝 Yes, add tasks", callback_data="add_tasks")],
            [InlineKeyboardButton("🚀 ابدأ مباشرة" if lang == 'ar' else "🚀 Start directly", callback_data="start_session")],
        ])
        await query.edit_message_text(get_text(user, 'tasks_ask'), reply_markup=keyboard)

    elif data == "add_tasks":
        context.user_data['step'] = 'adding_tasks'
        context.user_data['tasks'] = []
        await query.edit_message_text(get_text(user, 'tasks_add'), parse_mode='Markdown')

    elif data == "start_session":
        study_mins = context.user_data.get('study_mins', 50)
        break_mins = context.user_data.get('break_mins', 10)
        now = datetime.now()
        end = now + timedelta(minutes=study_mins)
        session_id = start_session(user_id, study_mins / 60)
        context.user_data['session_id'] = session_id
        context.user_data['session_end'] = end
        context.user_data['break_mins'] = break_mins

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🚪 انسحاب" if lang == 'ar' else "🚪 Withdraw", callback_data="withdraw_session")
        ]])
        await query.edit_message_text(
            get_text(user, 'session_started',
                     start=now.strftime("%I:%M %p"),
                     end=end.strftime("%I:%M %p")),
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

        context.application.job_queue.run_once(
            session_break_callback,
            study_mins * 60,
            data={'user_id': user_id, 'break_mins': break_mins, 'session_id': session_id},
            name=f"break_{user_id}"
        )

    elif data == "withdraw_session":
        session = get_active_session(user_id)
        if session:
            started = datetime.fromisoformat(str(session[2]))
            elapsed = (datetime.now() - started).total_seconds() / 3600
            points = max(0, int(elapsed))
            end_session(session[0], points)
            if points > 0:
                add_points(user_id, points)
            await query.edit_message_text(
                get_text(user, 'withdrew', points=points),
                reply_markup=back_keyboard(lang),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(get_text(user, 'no_session'))

    elif data == "menu_random":
        fake_list = "\n".join([f"{i+1}. {u['name']} ({u['country']}) — {u['specialty']}" for i, u in enumerate(FAKE_USERS)])
        user_entry = f"10. {user[2]} ({update.effective_user.first_name}) — {user[3]}"
        msg = f"👥 *المشاركون في السشن:*\n\n{fake_list}\n{user_entry}\n\n"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("50د دراسة 🕐", callback_data="solo_50_10")],
            [InlineKeyboardButton("2س دراسة 🕑", callback_data="solo_120_10")],
            [InlineKeyboardButton("3س دراسة 🕒", callback_data="solo_180_10")],
            [InlineKeyboardButton("🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="go_home")]
        ])
        await query.edit_message_text(msg + get_text(user, 'random_session'), reply_markup=keyboard, parse_mode='Markdown')

    elif data == "menu_challenge":
        await query.edit_message_text(
            get_text(user, 'challenge_friend', id=user_id),
            reply_markup=back_keyboard(lang),
            parse_mode='Markdown'
        )
        context.user_data['step'] = 'challenge_input'

    elif data == "menu_group":
        group_code = f"GRP{user_id % 9999:04d}"
        msg = f"👥 *التحدي الجماعي*\n\nكودك: `{group_code}`\n\nأرسل هذا الكود لأصدقائك ليدخلوا معك!\nمدة التحدي: 24 ساعة\n\nأو أدخل كود صديقك:"
        await query.edit_message_text(msg, reply_markup=back_keyboard(lang), parse_mode='Markdown')
        context.user_data['step'] = 'group_input'

    elif data == "menu_market":
        points = user[6]
        msg = get_text(user, 'black_market', points=points) + "\n\n"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 غرفة الـ 1% — 150 نقطة", callback_data="buy_elite")],
            [InlineKeyboardButton("🛡️ إجازة يومية — 5 نقاط", callback_data="buy_daily")],
            [InlineKeyboardButton("✈️ إجازة أسبوعية — 15 نقطة", callback_data="buy_weekly")],
            [InlineKeyboardButton("🆔 تغيير الهوية — 3 نقاط", callback_data="buy_identity")],
            [InlineKeyboardButton("🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="go_home")]
        ])
        await query.edit_message_text(msg, reply_markup=keyboard, parse_mode='Markdown')

    elif data.startswith("buy_"):
        item = data.split("_")[1]
        costs = {'elite': 150, 'daily': 5, 'weekly': 15, 'identity': 3}
        cost = costs.get(item, 0)
        points = user[6]

        if points < cost:
            await query.answer(f"❌ ما عندك نقاط كافية! تحتاج {cost} نقطة", show_alert=True)
            return

        deduct_points(user_id, cost)

        if item == 'identity':
            context.user_data['step'] = 'change_name'
            await query.edit_message_text("🆔 أرسل اسمك الجديد:")
        else:
            expires = datetime.now() + timedelta(days=7 if item == 'weekly' else 1 if item == 'daily' else 3)
            conn = __import__('sqlite3').connect('studyclub.db')
            c = conn.cursor()
            c.execute('INSERT INTO purchases (user_id, item, cost, expires_at) VALUES (?, ?, ?, ?)',
                      (user_id, item, cost, expires))
            conn.commit()
            conn.close()
            await query.edit_message_text(f"✅ تم الشراء بنجاح!", reply_markup=back_keyboard(lang))

    elif data == "menu_guide":
        guide_text = """📖 *دليل النادي*

💰 *نظام النقاط:*
• كل ساعة دراسة = 1 نقطة
• إكمال كل المهام = +2 نقطة
• ترقية الرتبة = +5 نقاط

📉 *النزيف:*
• 24 ساعة بدون دراسة = -2 نقطة
• أسبوع كامل = -10 نقاط

🏆 *الرتب:*
• برونزي 🥉 (0)
• فضي 🥈 (30)
• ذهبي 🥇 (100)
• بلاتيني 🔥 (250)
• ماسي 💎 (500)
• العرّاب 👑 (1000)"""
        await query.edit_message_text(guide_text, reply_markup=back_keyboard(lang), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("أرسل /start أولاً")
        return

    lang = get_lang(user)
    text = update.message.text.strip()
    step = context.user_data.get('step')

    if step == 'ask_name':
        update_user(user_id, name=text)
        context.user_data['step'] = 'ask_specialty'
        await update.message.reply_text(get_text(user, 'ask_specialty'))

    elif step == 'ask_specialty':
        update_user(user_id, specialty=text, charter_done=1)
        context.user_data['step'] = None
        user = get_user(user_id)
        rank = get_rank(user[7])
        await update.message.reply_text(
            get_text(user, 'welcome_done', name=user[2], rank=rank, points=user[6]),
            parse_mode='Markdown'
        )
        await update.message.reply_text(
            get_text(user, 'main_menu', name=user[2], rank=rank, points=user[6]),
            reply_markup=main_keyboard(lang),
            parse_mode='Markdown'
        )

    elif step == 'adding_tasks':
        if text.lower() in ['تم', 'done']:
            context.user_data['step'] = None
            await update.message.reply_text(get_text(user, 'tasks_done'), parse_mode='Markdown')
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🚀 ابدأ السشن" if lang == 'ar' else "🚀 Start Session", callback_data="start_session")
            ]])
            await update.message.reply_text("جاهز؟", reply_markup=keyboard)
        else:
            tasks = context.user_data.get('tasks', [])
            tasks.append(text)
            context.user_data['tasks'] = tasks
            await update.message.reply_text(get_text(user, 'task_added'))

    elif step == 'change_name':
        update_user(user_id, name=text)
        context.user_data['step'] = None
        await update.message.reply_text(f"✅ تم تغيير اسمك إلى: {text}")

    elif step == 'challenge_input':
        try:
            target_id = int(text)
            target = get_user(target_id)
            if target:
                await update.message.reply_text(f"✅ تم إرسال التحدي لـ {target[2]}!")
                await context.bot.send_message(
                    target_id,
                    f"⚔️ {user[2]} يتحداك في نادي الدراسة!\n\nموافق أم رفض؟",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ موافق", callback_data=f"accept_{user_id}"),
                         InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")]
                    ])
                )
            else:
                await update.message.reply_text("❌ المستخدم غير موجود")
        except:
            await update.message.reply_text("❌ أرسل ID صحيح")
        context.user_data['step'] = None

    elif step == 'custom_session':
        try:
            mins = int(text)
            if 10 <= mins <= 480:
                context.user_data['study_mins'] = mins
                context.user_data['break_mins'] = 10
                context.user_data['step'] = None
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 أضف مهام", callback_data="add_tasks")],
                    [InlineKeyboardButton("🚀 ابدأ مباشرة", callback_data="start_session")],
                ])
                await update.message.reply_text(get_text(user, 'tasks_ask'), reply_markup=keyboard)
            else:
                await update.message.reply_text("❌ أرسل رقم بين 10 و 480 دقيقة")
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح")

    else:
        rank = get_rank(user[7])
        await update.message.reply_text(
            get_text(user, 'main_menu', name=user[2] or 'مستخدم', rank=rank, points=user[6]),
            reply_markup=main_keyboard(lang),
            parse_mode='Markdown'
        )

async def session_break_callback(context):
    job_data = context.job.data
    user_id = job_data['user_id']
    break_mins = job_data['break_mins']
    session_id = job_data['session_id']
    user = get_user(user_id)
    lang = get_lang(user)

    await context.bot.send_message(
        user_id,
        get_text(user, 'break_time', minutes=break_mins),
        parse_mode='Markdown'
    )

    context.application.job_queue.run_once(
        session_end_callback,
        break_mins * 60,
        data={'user_id': user_id, 'session_id': session_id},
        name=f"end_{user_id}"
    )

async def session_end_callback(context):
    job_data = context.job.data
    user_id = job_data['user_id']
    session_id = job_data['session_id']
    user = get_user(user_id)

    session = get_active_session(user_id)
    if session:
        started = datetime.fromisoformat(str(session[2]))
        elapsed = (datetime.now() - started).total_seconds() / 3600
        points = max(1, int(elapsed))
        end_session(session_id, points)
        add_points(user_id, points)

        old_rank = get_rank(user[7])
        user = get_user(user_id)
        new_rank = get_rank(user[7])

        await context.bot.send_message(
            user_id,
            get_text(user, 'session_done', hours=round(elapsed, 1), points=points),
            parse_mode='Markdown'
        )

        if old_rank != new_rank:
            add_points(user_id, 5)
            await context.bot.send_message(
                user_id,
                get_text(user, 'rank_up', name=user[2], rank=new_rank),
                parse_mode='Markdown'
            )

async def fajr_notification(context):
    users = get_all_users()
    for u in users:
        try:
            user = get_user(u[0])
            if user and user[2]:
                await context.bot.send_message(
                    u[0],
                    get_text(user, 'fajr_msg', name=user[2]),
                    parse_mode='Markdown'
                )
        except:
            pass

async def bleed_check(context):
    conn = __import__('sqlite3').connect('studyclub.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE charter_done = 1')
    users = c.fetchall()
    conn.close()

    for user in users:
        user_id = user[0]
        last_study = user[8]
        if last_study:
            last = datetime.fromisoformat(str(last_study))
            diff = (datetime.now() - last).total_seconds() / 3600
            if diff >= 20:
                try:
                    await context.bot.send_message(
                        user_id,
                        get_text(user, 'bleed_warning', name=user[2]),
                        parse_mode='Markdown'
                    )
                except:
                    pass
            if diff >= 24 and not has_active_protection(user_id):
                deduct_points(user_id, 2)

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(fajr_notification, 'cron', hour=6, minute=0, args=[app])
    scheduler.add_job(bleed_check, 'interval', hours=4, args=[app])
    scheduler.start()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ StudyClub Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
