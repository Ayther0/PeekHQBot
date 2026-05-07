import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import init_db, get_user, add_user, update_credits, set_language, get_all_users

logging.basicConfig(level=logging.INFO)

TOKEN = "8547390643:AAE7r0W8DsDwVzr39KjIvM0bm6d5LhTFHSM"
CHANNEL = "@iPeekHQ"
ADMIN_ID = 8601067589

TEXTS = {
    'ar': {
        'welcome': "👁️ أهلاً في PeekHQ\n\nالبوت الأقوى لتحليل حسابات Instagram وTikTok\n\n🔍 اكتشف من يتابع من\n👻 شاهد القصص بشكل مجهول\n📊 تحليل كامل للحسابات\n\nرصيدك: {credits} محاولة مجانية",
        'choose_lang': "اختر لغتك:",
        'subscribe': "⚠️ لازم تشترك بالقناة أول:\n\n👉 @iPeekHQ\n\nبعد الاشتراك اضغط تحقق ✅",
        'not_subscribed': "❌ ما اشتركت بعد! اشترك وبعدين اضغط تحقق",
        'send_username': "أرسل يوزرنيم الحساب أو رابطه:",
        'choose_platform': "اختر المنصة:",
        'no_credits': "❌ انتهى رصيدك!\n\nاختر طريقة لإعادة الشحن:",
        'watch_ad': "🎬 شاهد إعلان (+3 محاولات)",
        'pay_stars': "⭐ ادفع بالنجوم (50 نجمة = لامحدود)",
        'referral': "👥 شارك رابطك (+2 لكل شخص)",
    },
    'en': {
        'welcome': "👁️ Welcome to PeekHQ\n\nThe most powerful Instagram & TikTok analyzer\n\n🔍 Discover who follows who\n👻 View stories anonymously\n📊 Full account analysis\n\nYour credits: {credits} free attempts",
        'choose_lang': "Choose your language:",
        'subscribe': "⚠️ You must join our channel first:\n\n👉 @iPeekHQ\n\nAfter joining press Verify ✅",
        'not_subscribed': "❌ Not subscribed yet! Join then press Verify",
        'send_username': "Send the account username or link:",
        'choose_platform': "Choose platform:",
        'no_credits': "❌ No credits left!\n\nChoose how to recharge:",
        'watch_ad': "🎬 Watch ad (+3 attempts)",
        'pay_stars': "⭐ Pay with Stars (50 stars = unlimited)",
        'referral': "👥 Share your link (+2 per person)",
    }
}

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    
    referred_by = None
    if context.args:
        try:
            referred_by = int(context.args[0])
            if referred_by == user_id:
                referred_by = None
        except:
            pass
    
    add_user(user_id, username, referred_by)
    user = get_user(user_id)
    lang = user[2] if user else 'ar'
    
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text(
        TEXTS[lang]['choose_lang'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()
    
    user = get_user(user_id)
    lang = user[2] if user else 'ar'
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        set_language(user_id, lang)
        user = get_user(user_id)
        
        keyboard = [
            [InlineKeyboardButton("✅ تحقق | Verify", callback_data="check_sub")]
        ]
        await query.edit_message_text(
            TEXTS[lang]['subscribe'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "check_sub":
        subscribed = await check_subscription(user_id, context.bot)
        if subscribed:
            user = get_user(user_id)
            credits = user[3]
            keyboard = [
                [InlineKeyboardButton("📸 Instagram", callback_data="platform_ig"),
                 InlineKeyboardButton("🎵 TikTok", callback_data="platform_tt")]
            ]
            await query.edit_message_text(
                TEXTS[lang]['welcome'].format(credits=credits),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.answer(TEXTS[lang]['not_subscribed'], show_alert=True)
    
    elif data.startswith("platform_"):
        if user[3] <= 0:
            ref_link = f"https://t.me/PeekHQBot?start={user_id}"
            keyboard = [
                [InlineKeyboardButton(TEXTS[lang]['watch_ad'], url="https://linkvertise.com")],
                [InlineKeyboardButton(TEXTS[lang]['pay_stars'], callback_data="pay_stars")],
                [InlineKeyboardButton(TEXTS[lang]['referral'], switch_inline_query=ref_link)]
            ]
            await query.edit_message_text(
                TEXTS[lang]['no_credits'],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        platform = data.split("_")[1]
        context.user_data['platform'] = platform
        await query.edit_message_text(TEXTS[lang]['send_username'])

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("أرسل /start أولاً")
        return
    
    lang = user[2]
    platform = context.user_data.get('platform')
    
    if not platform:
        keyboard = [
            [InlineKeyboardButton("📸 Instagram", callback_data="platform_ig"),
             InlineKeyboardButton("🎵 TikTok", callback_data="platform_tt")]
        ]
        await update.message.reply_text(
            TEXTS[lang]['choose_platform'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    username = update.message.text.strip().replace("@", "").replace("https://www.instagram.com/", "").replace("https://www.tiktok.com/@", "").strip("/")
    
    update_credits(user_id, -1)
    
    await update.message.reply_text(f"🔍 جاري تحليل @{username}...")
    
    # هنا نضيف الأدوات لاحقاً
    await update.message.reply_text(f"✅ تم استلام: @{username}\n🚧 الأدوات قيد البناء...")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("اكتب الرسالة بعد /broadcast")
        return
    
    message = " ".join(context.args)
    users = get_all_users()
    sent = 0
    for user in users:
        try:
            await context.bot.send_message(user[0], message)
            sent += 1
        except:
            pass
    await update.message.reply_text(f"✅ تم الإرسال لـ {sent} مستخدم")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.run_polling()

if __name__ == "__main__":
    main()
