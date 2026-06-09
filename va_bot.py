import logging
import re
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = "givrelin"
 
FORBIDDEN_PROFILES = ["drivewitharthur", "moses_carss", "gueuledange_off", "capi_cs"]
TIKTOK_REGEX = re.compile(r"https?://(www\.)?tiktok\.com/@[\w._-]+", re.IGNORECASE)
 
S1, S2, S3, PROFILS = range(4)
 
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
 
# ── MESSAGES ────────────────────────────────────────────────────────────────
 
MSG1 = (
    "💼 TON JOB\n\n"
    "Tu dois contacter des influenceurs sur TikTok et Instagram 📱\n\n"
    "🛠️ Si tu réussis le test, tu auras accès à notre CRM (l'outil qui t'aide à bosser) et tu pourras commencer à gagner de l'argent 💰\n\n"
    "🎯 Ta mission : trouver des créateurs qui ont MINIMUM 30 000 vues par vidéo en moyenne.\n\n"
    "💰 COMBIEN TU PEUX GAGNER ?\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "🏦 100$ fixe / mois\n"
    "Garanti dès que tu passes le test et tu bosses sérieusement\n\n"
    "📲 + 3$ par contact ramené\n"
    "Chaque numéro WhatsApp ou Telegram d'influenceur que tu trouves = +3$\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "📊 Exemple concret (1 mois) :\n"
    "➡️ 10 contacts/jour x 30 jours = 300 contacts\n"
    "➡️ 300 x 3$ = 900$\n"
    "➡️ + le fixe de 100$\n"
    "🤑 = 1 000$ ce mois-là\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "⏱️ Paiement tous les 3 jours — pas d'attente de fin de mois 🔥\n\n"
    "C'est toi qui décides de ton niveau. 🚀"
)
 
MSG2 = (
    "📬 TON OBJECTIF\n\n"
    "Tu devras contacter environ 150 influenceurs par jour.\n\n"
    "⚠️ ATTENTION : on préfère la QUALITÉ à la quantité !\n"
    "Mieux vaut 50 bons profils que 150 mauvais."
)
 
MSG3 = (
    "🧪 LE TEST\n\n"
    "Maintenant on va voir si tu as bien compris 🧠\n"
    "Tu vas m'envoyer 5 profils TikTok via ce bot.\n\n"
    "🇫🇷 Marché cible : FRANCE 🇫🇷\n\n"
    "✅ UN BON PROFIL C'EST :\n"
    "📊 Minimum 40 000 vues en moyenne\n"
    "👤 Pas trop connu (PAS de Squeezie, Inoxtag, etc.)\n"
    "📅 A posté dans les 7 derniers jours\n"
    "🚫 PAS une entreprise ou une marque (style McDonald's)\n"
    "🚫 PAS de contenu religieux\n"
    "🚫 PAS un compte de repost (on veut des VRAIS créateurs originaux)\n"
    "🇫🇷 Doit viser le marché français\n\n"
    "📌 Règles supplémentaires :\n"
    "- Pas d'influenceurs d'Afrique, nous voulons des personnes basées en France 🇫🇷\n"
    "- Pas de grosse personnalité connue ou certifiée 🙅‍♂️"
)
 
MSG4 = (
    "📌 VOICI 4 EXEMPLES DE BONS PROFILS :\n\n"
    "1️⃣ https://www.tiktok.com/@drivewitharthur\n"
    "2️⃣ https://www.tiktok.com/@moses_carss\n"
    "3️⃣ https://www.tiktok.com/@gueuledange_off\n"
    "4️⃣ https://www.tiktok.com/@capi_cs\n\n"
    "⚠️ IMPORTANT : Tu ne peux PAS utiliser ces profils dans le test ! Trouves-en d'autres 😉\n\n"
    "💪 A TOI DE JOUER !\n"
    "Envoie-moi tes 5 profils TikTok.\n"
    "✏️ Format : https://www.tiktok.com/@username\n\n"
    "⚠️ Tu as droit à 1 erreur MAXIMUM !\n"
    "Tu peux les envoyer un par un ou tous d'un coup."
)
 
BTN1 = "Continuer ➡️"
BTN2 = "Voir le test ➡️"
BTN3 = "Voir les exemples ➡️"
BTN4 = "Je suis pret, envoyer mes profils ➡️"
 
 
# ── HANDLERS ────────────────────────────────────────────────────────────────
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["profiles"] = []
    context.user_data["errors"] = 0
    context.user_data["valid_count"] = 0
    kb = [[BTN1]]
    await update.message.reply_text(
        MSG1,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    )
    return S1
 
 
async def step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[BTN2]]
    await update.message.reply_text(
        MSG2,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    )
    return S2
 
 
async def step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[BTN3]]
    await update.message.reply_text(
        MSG3,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    )
    return S3
 
 
async def step4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[BTN4]]
    await update.message.reply_text(
        MSG4,
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    )
    return PROFILS
 
 
async def receive_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
 
    # Si le VA appuie sur le bouton "Je suis pret" au lieu d'envoyer un profil
    if text == BTN4:
        await update.message.reply_text(
            "Envoie tes profils TikTok maintenant 👇\nFormat : https://www.tiktok.com/@username",
            reply_markup=ReplyKeyboardRemove()
        )
        return PROFILS
 
    urls = TIKTOK_REGEX.findall(text)
 
    if not urls:
        context.user_data["errors"] = context.user_data.get("errors", 0) + 1
        if context.user_data["errors"] > 1:
            await notify_admin(context, update.effective_user, context.user_data.get("profiles", []), "echoue")
            await update.message.reply_text(
                "❌ TEST ECHOUE\n\nTu as depasse le nombre d'erreurs autorisees (1 maximum).\n\nTape /start pour recommencer.",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
        await update.message.reply_text(
            "❌ Ce n'est pas une URL TikTok valide.\n\nFormat attendu : https://www.tiktok.com/@username",
            reply_markup=ReplyKeyboardRemove()
        )
        await send_progress(update, context)
        return PROFILS
 
    for raw_url in urls:
        url = raw_url.lower().rstrip("/")
        username = url.split("/@")[-1].lower()
        profiles = context.user_data.get("profiles", [])
        errors = context.user_data.get("errors", 0)
        valid_count = context.user_data.get("valid_count", 0)
 
        if username in FORBIDDEN_PROFILES:
            errors += 1
            context.user_data["errors"] = errors
            if errors > 1:
                await notify_admin(context, update.effective_user, profiles, "echoue")
                await update.message.reply_text(
                    "❌ TEST ECHOUE\n\nTu as utilise un profil exemple et depasse la limite d'erreurs.\n\nTape /start pour recommencer.",
                    reply_markup=ReplyKeyboardRemove()
                )
                return ConversationHandler.END
            await update.message.reply_text("🚫 Ce profil fait partie des exemples fournis, tu ne peux pas l'utiliser !")
            await send_progress(update, context)
            continue
 
        if url in profiles:
            await update.message.reply_text("⚠️ Tu as deja envoye ce profil. Envoie-en un autre.")
            continue
 
        profiles.append(url)
        valid_count += 1
        context.user_data["profiles"] = profiles
        context.user_data["valid_count"] = valid_count
 
        await update.message.reply_text(f"✅ Profil {valid_count}/5 enregistre !")
 
        if valid_count >= 5:
            await notify_admin(context, update.effective_user, profiles, "reussi")
            await update.message.reply_text(
                "🎉 FELICITATIONS !\n\nTu as passe le test avec succes ! ✅\n\nNotre equipe va verifier tes profils et te recontacte tres prochainement. 🚀\n\nBienvenue dans l'equipe ! 💪",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
 
    if context.user_data.get("valid_count", 0) < 5:
        await send_progress(update, context)
 
    return PROFILS
 
 
async def send_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid = context.user_data.get("valid_count", 0)
    errors = context.user_data.get("errors", 0)
    await update.message.reply_text(
        f"📋 Profils recus : {valid + errors}/5\n✅ Valides : {valid}\n⚠️ Erreurs : {errors}/1"
    )
 
 
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user, profiles, status):
    try:
        profils_text = "\n".join([f"• {p}" for p in profiles]) if profiles else "Aucun profil soumis"
        emoji = "✅" if status == "reussi" else "❌"
        msg = (
            f"{emoji} VA {status.upper()}\n\n"
            f"👤 @{user.username} ({user.first_name})\n"
            f"🆔 ID Telegram : {user.id}\n\n"
            f"📋 Profils soumis :\n{profils_text}"
        )
        await context.bot.send_message(chat_id=f"@{ADMIN_USERNAME}", text=msg)
    except Exception as e:
        logger.error(f"Erreur notification admin : {e}")
 
 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session annulee. Tape /start pour recommencer.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
 
 
# ── MAIN ────────────────────────────────────────────────────────────────────
 
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            S1: [MessageHandler(filters.TEXT & ~filters.COMMAND, step2)],
            S2: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3)],
            S3: [MessageHandler(filters.TEXT & ~filters.COMMAND, step4)],
            PROFILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_profiles)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    logger.info("Bot demarre...")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
 
