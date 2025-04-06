import os
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from yt_dlp import YoutubeDL
import logging
import time

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Remplace par ton token et l'ID de ton canal
TOKEN = "7399969013:AAGjK8ztQWTExbJnlJvUIy-yy4CSpaB5ui0"
ADMIN_ID = 5381954794  # Ton ID Telegram
CHANNEL_ID = "@Edufr1"  # Ton canal Telegram

# Dossier temporaire pour les fichiers téléchargés
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Dictionnaire pour les traductions
LANGUAGES = {
    "fr": {
        "welcome": "👋 Bienvenue sur EduVideoDownloaderBot !\nJe suis ici pour t'aider à télécharger des vidéos et de la musique depuis YouTube, Instagram, TikTok et plus encore, rapidement et facilement.",
        "send_link": "✅ Envoie un lien YouTube, Instagram, TikTok ou autre pour télécharger.",
        "help_text": "📖 **Aide pour EduVideoDownloaderBot**\n\n1. Envoie un lien YouTube, Instagram, TikTok ou autre.\n2. Choisis la qualité : Vidéo (Standard 720p, HD 1080p, 4K si disponible) ou Musique (MP3).\n\nCommandes disponibles :\n/start - Afficher ce message\n/help - Afficher cette aide\n/stats - Voir les statistiques (admin uniquement)",
        "choose_format": "⬇️ Choisis une option :",
        "downloading": "⏳ Téléchargement en cours : {format_type} ({quality})...",
        "video_caption": "Voici votre vidéo !",
        "audio_caption": "Voici votre audio !",
        "invalid_link": "❌ Veuillez envoyer un lien valide (YouTube, Instagram, TikTok, etc.).",
        "no_url": "❌ Erreur : aucune URL trouvée. Veuillez renvoyer le lien.",
        "invalid_action": "❌ Action non reconnue.",
        "invalid_data": "❌ Erreur : format de données invalide.",
        "download_error": "❌ Une erreur s'est produite lors du téléchargement. Veuillez réessayer.",
        "format_error": "❌ Une erreur s'est produite lors de la récupération des informations.",
        "stats_text": "📊 **Statistiques**\n\nTotal des téléchargements : {total_downloads}",
        "not_authorized": "🚫 Vous n'êtes pas autorisé à utiliser cette commande.",
        "network_error": "⚠️ Problème de connexion. Veuillez réessayer plus tard.",
        "value_error": "⚠️ Une erreur s'est produite. Veuillez réessayer.",
        "unexpected_error": "⚠️ Une erreur inattendue s'est produite.",
        "not_subscribed": "🚫 Vous devez être abonné à notre canal pour utiliser ce bot.\nRejoignez ici : {channel_link}",
    },
    "en": {
        "welcome": "👋 Welcome to EduVideoDownloaderBot!\nI'm here to help you download videos and music from YouTube, Instagram, TikTok, and more, quickly and easily.",
        "send_link": "✅ Send a YouTube, Instagram, TikTok, or other link to download.",
        "help_text": "📖 **Help for EduVideoDownloaderBot**\n\n1. Send a YouTube, Instagram, TikTok, or other link.\n2. Choose the quality: Video (Standard 720p, HD 1080p, 4K if available) or Music (MP3).\n\nAvailable commands:\n/start - Show this message\n/help - Show this help\n/stats - View statistics (admin only)",
        "choose_format": "⬇️ Choose an option:",
        "downloading": "⏳ Downloading: {format_type} ({quality})...",
        "video_caption": "Here is your video!",
        "audio_caption": "Here is your audio!",
        "invalid_link": "❌ Please send a valid link (YouTube, Instagram, TikTok, etc.).",
        "no_url": "❌ Error: No URL found. Please resend the link.",
        "invalid_action": "❌ Unrecognized action.",
        "invalid_data": "❌ Error: Invalid data format.",
        "download_error": "❌ An error occurred while downloading. Please try again.",
        "format_error": "❌ An error occurred while retrieving information.",
        "stats_text": "📊 **Statistics**\n\nTotal downloads: {total_downloads}",
        "not_authorized": "🚫 You are not authorized to use this command.",
        "network_error": "⚠️ Connection issue. Please try again later.",
        "value_error": "⚠️ An error occurred. Please try again.",
        "unexpected_error": "⚠️ An unexpected error occurred.",
        "not_subscribed": "🚫 You must be subscribed to our channel to use this bot.\nJoin here: {channel_link}",
    },
    "es": {
        "welcome": "👋 ¡Bienvenido a EduVideoDownloaderBot!\nEstoy aquí para ayudarte a descargar videos y música de YouTube, Instagram, TikTok y más, de manera rápida y fácil.",
        "send_link": "✅ ¡Envía un enlace de YouTube, Instagram, TikTok u otro para descargar!",
        "help_text": "📖 **Ayuda para EduVideoDownloaderBot**\n\n1. Envía un enlace de YouTube, Instagram, TikTok u otro.\n2. Elige la calidad: Video (Estándar 720p, HD 1080p, 4K si disponible) o Música (MP3).\n\nComandos disponibles:\n/start - Mostrar este mensaje\n/help - Mostrar esta ayuda\n/stats - Ver estadísticas (solo admin)",
        "choose_format": "⬇️ Elige una opción:",
        "downloading": "⏳ Descargando: {format_type} ({quality})...",
        "video_caption": "¡Aquí está tu video!",
        "audio_caption": "¡Aquí está tu audio!",
        "invalid_link": "❌ Por favor, envía un enlace válido (YouTube, Instagram, TikTok, etc.).",
        "no_url": "❌ Error: No se encontró ninguna URL. Por favor, vuelve a enviar el enlace.",
        "invalid_action": "❌ Acción no reconocida.",
        "invalid_data": "❌ Error: Formato de datos inválido.",
        "download_error": "❌ Ocurrió un error durante la descarga. Por favor, intenta de nuevo.",
        "format_error": "❌ Ocurrió un error al recuperar la información.",
        "stats_text": "📊 **Estadísticas**\n\nTotal de descargas: {total_downloads}",
        "not_authorized": "🚫 No estás autorizado para usar este comando.",
        "network_error": "⚠️ Problema de conexión. Por favor, intenta de nuevo más tarde.",
        "value_error": "⚠️ Ocurrió un error. Por favor, intenta de nuevo.",
        "unexpected_error": "⚠️ Ocurrió un error inesperado.",
        "not_subscribed": "🚫 Debes estar suscrito a nuestro canal para usar este bot.\nÚnete aquí: {channel_link}",
    }
}

# Fonction pour obtenir le texte traduit selon la langue de l'utilisateur
def get_text(key, update, context, **kwargs):
    lang = update.effective_user.language_code if update.effective_user else "fr"
    if lang.startswith("fr"):
        lang = "fr"
    elif lang.startswith("es"):
        lang = "es"
    else:
        lang = "en"
    context.user_data["language"] = lang
    text = LANGUAGES[lang].get(key, LANGUAGES["fr"][key])
    return text.format(**kwargs) if kwargs else text

# Fonction pour vérifier l'abonnement au canal
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except telegram.error.TelegramError as e:
        logger.error(f"Erreur lors de la vérification de l'abonnement : {e}")
        await update.message.reply_text(get_text("unexpected_error", update, context))
        return False

# Commande /start avec message de bienvenue
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Commande /start reçue")
    is_subscribed = await check_subscription(update, context)
    if not is_subscribed:
        channel_link = f"https://t.me/{CHANNEL_ID.lstrip('@')}"
        await update.message.reply_text(get_text("not_subscribed", update, context, channel_link=channel_link))
        return
    await update.message.reply_text(get_text("welcome", update, context))
    await update.message.reply_text(get_text("send_link", update, context))

# Commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        return
    await update.message.reply_text(get_text("help_text", update, context))

# Commande /stats (admin uniquement)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text(get_text("not_authorized", update, context))
        return
    total_downloads = context.bot_data.get("total_downloads", 0)
    await update.message.reply_text(get_text("stats_text", update, context, total_downloads=total_downloads))

# Gestion des liens envoyés
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        return
    url = update.message.text
    logger.info(f"Message reçu, vérification du lien... URL : {url}")
    if not ("youtube.com" in url or "youtu.be" in url or "instagram.com" in url or "tiktok.com" in url):
        await update.message.reply_text(get_text("invalid_link", update, context))
        return
    context.user_data["url"] = url
    keyboard = [
        [InlineKeyboardButton("🎥 Vidéo (Standard 720p)", callback_data="download_video_standard")],
        [InlineKeyboardButton("🎥 Vidéo (HD 1080p)", callback_data="download_video_hd")],
        [InlineKeyboardButton("🎥 Vidéo (4K)", callback_data="download_video_4k")],
        [InlineKeyboardButton("🎵 Musique (MP3)", callback_data="download_audio_mp3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("choose_format", update, context), reply_markup=reply_markup)

# Gestion des clics sur les boutons
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    logger.info(f"Callback data reçu : {data}")
    if not data.startswith("download_"):
        await query.message.reply_text(get_text("invalid_action", update, context))
        return
    parts = data.split("_")
    if len(parts) < 3:
        logger.error(f"Erreur : callback_data mal formé : {data}")
        await query.message.reply_text(get_text("invalid_data", update, context))
        return
    _, format_type, quality = parts
    file_format = "mp4" if format_type == "video" else "mp3"
    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text(get_text("no_url", update, context))
        return
    await query.message.reply_text(
        get_text("downloading", update, context, format_type=format_type.capitalize(), quality=quality.upper())
    )
    await download_and_send(url, format_type, file_format, quality, query.message, update, context)

# Fonction pour télécharger et envoyer le fichier
async def download_and_send(url: str, format_type: str, file_format: str, quality: str, message, update: Update, context: ContextTypes.DEFAULT_TYPE):
    ydl_opts = {
        "outtmpl": f"{TEMP_DIR}/%(title)s.%(ext)s",
        "format": (
            "bestvideo[height<=2160]+bestaudio/best" if quality == "4k" else
            "bestvideo[height<=1080]+bestaudio/best" if quality == "hd" else
            "bestvideo[height<=720]+bestaudio/best" if format_type == "video" else
            "bestaudio"
        ),
        "merge_output_format": file_format,
        "quiet": True,
        "no_warnings": True,
        "no_playlist": True,
        "retries": 10,
        "retry_sleep": 5,
        "no_check_certificate": True,
        "format_sort": ["res", "vcodec:h264"],
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).rsplit(".", 1)[0] + f".{file_format}"
            if os.path.exists(file_path):
                if format_type == "video":
                    await message.reply_video(video=open(file_path, "rb"), caption=get_text("video_caption", update, context))
                else:
                    await message.reply_audio(audio=open(file_path, "rb"), caption=get_text("audio_caption", update, context))
                context.bot_data["total_downloads"] = context.bot_data.get("total_downloads", 0) + 1
                os.remove(file_path)
            else:
                await message.reply_text(get_text("download_error", update, context))
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement : {e}")
        await message.reply_text(get_text("download_error", update, context))

# Gestionnaire d'erreurs global
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, telegram.error.NetworkError):
        logger.error(f"Erreur réseau : {context.error}. Tentative de reconnexion...")
        if update and update.message:
            await update.message.reply_text(get_text("network_error", update, context))
    elif isinstance(context.error, ValueError):
        logger.error(f"Erreur de valeur : {context.error}")
        if update and update.message:
            await update.message.reply_text(get_text("value_error", update, context))
    else:
        logger.error(f"Erreur inattendue : {context.error}")
        if update and update.message:
            await update.message.reply_text(get_text("unexpected_error", update, context))

# Fonction principale avec reconnexion
def main():
    logger.info("Démarrage du bot...")
    while True:
        try:
            app = Application.builder().token(TOKEN).build()
            app.add_error_handler(error_handler)
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("stats", stats_command))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
            app.add_handler(CallbackQueryHandler(button_callback))
            logger.info("Démarrage du polling...")
            app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du bot : {e}. Reconnexion dans 10 secondes...")
            time.sleep(10)

if __name__ == "__main__":
    main()
