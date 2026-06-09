import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = "givrelin"
 
S1, S2, S3, PROFILS = range(4)
 
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
 
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
    "💪 À TOI DE JOUER !\n"
    "Envoie-moi tes 5 profils TikTok.\n"
    "✏️ Format : https://www.tiktok.com/@username\n\n"
    "Tu peux les envoyer un par un ou tous d'un coup."
)
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["profiles"] = []
    await update.message.reply_text(
        MSG1,
        reply_markup=ReplyKeyboardMarkup([["Continuer ➡️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return S1
 
async def step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MSG2,
        reply_markup=ReplyKeyboardMarkup([["Voir le test ➡️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return S2
 
async def step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MSG3,
        reply_markup=ReplyKeyboardMarkup([["Voir les exemples ➡️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return S3
 
async def step4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MSG4,
        reply_markup=ReplyKeyboardRemove()
    )
    return PROFILS
 
 
async def receive_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    profiles = context.user_data.get("profiles", [])
 
    profiles.append(text)
    context.user_data["profiles"] = profiles
    count = len(profiles)
 
    await update.message.reply_text(f"✅ Profil {count}/5 reçu !")
 
    if count >= 5:
        user = update.effective_user
        await notify_admin(context, user, profiles)
        await update.message.reply_text(
            "🎉 FÉLICITATIONS !\n\nTu as envoyé tes 5 profils ! ✅\n\nNotre équipe va les vérifier et te recontacte très prochainement. 🚀\n\nBienvenue dans l'équipe ! 💪",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
 
    return PROFILS
 
 
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, user, profiles):
    try:
        profils_text = "\n".join([f"{i+1}. {p}" for i, p in enumerate(profiles)])
        username = f"@{user.username}" if user.username else user.first_name
        msg = (
            f"🆕 NOUVEAU VA — TEST COMPLÉTÉ\n\n"
            f"👤 {username} ({user.first_name})\n"
            f"🆔 ID : {user.id}\n\n"
            f"📋 Profils soumis :\n{profils_text}"
        )
        await context.bot.send_message(chat_id=f"@{ADMIN_USERNAME}", text=msg)
    except Exception as e:
        logger.error(f"Erreur notification admin : {e}")
 
 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session annulée. Tape /start pour recommencer.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
 
 
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
 
