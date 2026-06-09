import logging
import re
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
 
BOT_TOKEN = os.environ.get("BOT_TOKEN")
 
FORBIDDEN_PROFILES = ["drivewitharthur", "moses_carss", "gueuledange_off", "capi_cs"]
TIKTOK_REGEX = re.compile(r"https?://(www\.)?tiktok\.com/@[\w._-]+", re.IGNORECASE)
WAITING_START, WAITING_PROFILES = range(2)
 
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
 
BTN_PRET = "Je suis pret, continuer"
BTN_TEST = "Commencer le test"
 
MSG_WELCOME = """💼 *TON JOB*
 
Tu dois contacter des influenceurs sur TikTok et Instagram 📱
 
🛠️ Si tu réussis le test, tu auras accès à notre CRM et tu pourras commencer à gagner de l'argent 💰
 
🎯 *Ta mission :* trouver des créateurs qui ont MINIMUM 30 000 vues par vidéo en moyenne.
 
💰 *COMBIEN TU PEUX GAGNER ?*
━━━━━━━━━━━━━━━━━━━━
🏦 *100$ fixe / mois*
Garanti dès que tu passes le test et tu bosses sérieusement
 
📲 *+ 3$ par contact ramené*
Chaque numéro WhatsApp ou Telegram d'influenceur = +3$
━━━━━━━━━━━━━━━━━━━━
📊 *Exemple concret (1 mois) :*
➡️ 10 contacts/jour x 30 jours = 300 contacts
➡️ 300 x 3$ = 900$
➡️ + le fixe de 100$
🤑 = *1 000$ ce mois-là*
━━━━━━━━━━━━━━━━━━━━
⏱️ Paiement tous les 3 jours — pas d'attente de fin de mois 🔥
 
Tu es prêt à continuer ?"""
 
MSG_OBJECTIVE = """📬 *TON OBJECTIF*
 
Tu devras contacter environ *150 influenceurs par jour.*
 
⚠️ On préfère la *QUALITÉ* à la quantité !
Mieux vaut 50 bons profils que 150 mauvais.
 
Appuie sur *Commencer le test* quand tu es prêt !"""
 
MSG_TEST = """🧪 *LE TEST*
 
Tu vas m'envoyer *5 profils TikTok* via ce bot.
 
🇫🇷 Marché cible : *FRANCE* 🇫🇷
 
✅ *UN BON PROFIL C'EST :*
📊 Minimum 40 000 vues en moyenne
👤 Pas trop connu (PAS de Squeezie, Inoxtag, etc.)
📅 A posté dans les *7 derniers jours*
🚫 PAS une entreprise ou une marque
🚫 PAS de contenu religieux
🚫 PAS un compte de repost
🇫🇷 Doit viser le marché français
🚫 Pas d'influenceurs d'Afrique — personnes basées en France uniquement
 
📌 *4 EXEMPLES de bons profils* (tu ne peux PAS les utiliser) :
1️⃣ https://www.tiktok.com/@drivewitharthur
2️⃣ https://www.tiktok.com/@moses_carss
3️⃣ https://www.tiktok.com/@gueuledange_off
4️⃣ https://www.tiktok.com/@capi_cs
 
⚠️ Tu as droit à *1 erreur MAXIMUM !*
 
✏️ Format : https://www.tiktok.com/@username
 
💪 Envoie tes 5 profils (un par un ou tous d'un coup) :"""
 
MSG_FORBIDDEN = "🚫 Ce profil fait partie des exemples fournis, tu ne peux pas l'utiliser !"
MSG_INVALID_URL = "❌ Ce n'est pas une URL TikTok valide.\n\nFormat attendu : https://www.tiktok.com/@username"
MSG_DUPLICATE = "⚠️ Tu as déjà envoyé ce profil. Envoie-en un autre."
MSG_SUCCESS = """🎉 *FÉLICITATIONS !*
 
Tu as passé le test avec succès ! ✅
 
Notre équipe va vérifier tes profils et te recontacte très prochainement pour la suite. 🚀
 
Bienvenue dans l'équipe ! 💪"""
 
MSG_FAILED = """❌ *TEST ÉCHOUÉ*
 
Tu as dépassé le nombre d'erreurs autorisées (1 maximum).
 
Tu peux recommencer depuis le début avec /start."""
 
MSG_PROGRESS = "📋 Profils reçus : {count}/5\n✅ Valides : {valid}\n⚠️ Erreurs : {errors}/1"
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["profiles"] = []
    context.user_data["errors"] = 0
    context.user_data["valid_count"] = 0
    keyboard = [[BTN_PRET]]
    await update.message.reply_text(
        MSG_WELCOME,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return WAITING_START
 
 
async def show_objective(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[BTN_TEST]]
    await update.message.reply_text(
        MSG_OBJECTIVE,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return WAITING_START
 
 
async def show_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MSG_TEST,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return WAITING_PROFILES
 
 
async def receive_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    urls = TIKTOK_REGEX.findall(text)
 
    if not urls:
        context.user_data["errors"] = context.user_data.get("errors", 0) + 1
        if context.user_data["errors"] > 1:
            await update.message.reply_text(MSG_FAILED, parse_mode="Markdown")
            return ConversationHandler.END
        await update.message.reply_text(MSG_INVALID_URL)
        await send_progress(update, context)
        return WAITING_PROFILES
 
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
                await update.message.reply_text(MSG_FAILED, parse_mode="Markdown")
                return ConversationHandler.END
            await update.message.reply_text(MSG_FORBIDDEN)
            continue
 
        if url in profiles:
            await update.message.reply_text(MSG_DUPLICATE)
            continue
 
        profiles.append(url)
        valid_count += 1
        context.user_data["profiles"] = profiles
        context.user_data["valid_count"] = valid_count
 
        await update.message.reply_text(f"✅ Profil {valid_count}/5 enregistré !")
 
        if valid_count >= 5:
            user = update.effective_user
            logger.info(f"NOUVEAU VA | @{user.username} ({user.id}) | Profils: {profiles}")
            await update.message.reply_text(MSG_SUCCESS, parse_mode="Markdown")
            return ConversationHandler.END
 
    if context.user_data.get("valid_count", 0) < 5:
        await send_progress(update, context)
 
    return WAITING_PROFILES
 
 
async def send_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid = context.user_data.get("valid_count", 0)
    errors = context.user_data.get("errors", 0)
    await update.message.reply_text(MSG_PROGRESS.format(count=valid+errors, valid=valid, errors=errors))
 
 
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session annulée. Tape /start pour recommencer.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
 
 
async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 Tape /start pour commencer le test de recrutement.")
 
 
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_START: [
                MessageHandler(filters.Text(BTN_PRET), show_objective),
                MessageHandler(filters.Text(BTN_TEST), show_test),
            ],
            WAITING_PROFILES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_profiles),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    logger.info("Bot démarré...")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
