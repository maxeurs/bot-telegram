
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
 
# Un seul état intermédiaire
WAITING_BUTTON, WAITING_PROFILES = range(2)
 
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
 
MSG_WELCOME = """💼 *TON JOB*
 
Tu dois contacter des influenceurs sur TikTok et Instagram 📱
 
Si tu réussis le test, tu auras accès à notre CRM et tu pourras commencer à gagner de l'argent 💰
 
*Ta mission :* trouver des créateurs qui ont MINIMUM 30 000 vues par vidéo en moyenne.
 
💰 *COMBIEN TU PEUX GAGNER ?*
━━━━━━━━━━━━━━━━━━━━
🏦 *100$ fixe / mois*
Garanti dès que tu passes le test et tu bosses sérieusement
 
📲 *+ 3$ par contact ramené*
Chaque numéro WhatsApp ou Telegram d'influenceur = +3$
━━━━━━━━━━━━━━━━━━━━
📊 *Exemple concret (1 mois) :*
10 contacts/jour x 30 jours = 300 contacts
300 x 3$ = 900$
+ le fixe de 100$
= *1 000$ ce mois-là*
━━━━━━━━━━━━━━━━━━━━
Paiement tous les 3 jours — pas d'attente de fin de mois 🔥
 
Tu devras contacter environ *150 influenceurs par jour.*
On préfère la *QUALITÉ* à la quantité — mieux vaut 50 bons profils que 150 mauvais.
 
Appuie sur le bouton pour commencer le test 👇"""
 
MSG_TEST = """🧪 *LE TEST*
 
Tu vas m'envoyer *5 profils TikTok.*
 
🇫🇷 Marché cible : *FRANCE* 🇫🇷
 
✅ *UN BON PROFIL C'EST :*
- Minimum 40 000 vues en moyenne
- Pas trop connu (PAS de Squeezie, Inoxtag, etc.)
- A posté dans les *7 derniers jours*
- PAS une entreprise ou une marque
- PAS de contenu religieux
- PAS un compte de repost
- Doit viser le marché français
- Pas d'influenceurs d'Afrique — personnes basées en France uniquement
 
📌 *4 EXEMPLES* (tu ne peux PAS les utiliser) :
1. https://www.tiktok.com/@drivewitharthur
2. https://www.tiktok.com/@moses_carss
3. https://www.tiktok.com/@gueuledange_off
4. https://www.tiktok.com/@capi_cs
 
⚠️ Tu as droit à *1 erreur MAXIMUM !*
 
Format : https://www.tiktok.com/@username
 
💪 Envoie tes 5 profils maintenant :"""
 
MSG_FORBIDDEN = "🚫 Ce profil fait partie des exemples fournis, tu ne peux pas l'utiliser !"
MSG_INVALID_URL = "❌ Ce n'est pas une URL TikTok valide.\n\nFormat attendu : https://www.tiktok.com/@username"
MSG_DUPLICATE = "⚠️ Tu as déjà envoyé ce profil. Envoie-en un autre."
MSG_SUCCESS = """🎉 *FÉLICITATIONS !*
 
Tu as passé le test avec succès ! ✅
 
Notre équipe va vérifier tes profils et te recontacte très prochainement. 🚀
 
Bienvenue dans l'équipe ! 💪"""
 
MSG_FAILED = """❌ *TEST ÉCHOUÉ*
 
Tu as dépassé le nombre d'erreurs autorisées (1 maximum).
 
Tape /start pour recommencer."""
 
MSG_PROGRESS = "📋 Profils reçus : {count}/5\n✅ Valides : {valid}\n⚠️ Erreurs : {errors}/1"
 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["profiles"] = []
    context.user_data["errors"] = 0
    context.user_data["valid_count"] = 0
    keyboard = [["Commencer le test"]]
    await update.message.reply_text(
        MSG_WELCOME,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return WAITING_BUTTON
 
 
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
 
 
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_test),
            ],
            WAITING_PROFILES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_profiles),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    logger.info("Bot démarré...")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()
