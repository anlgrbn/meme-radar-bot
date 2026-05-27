import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import anthropic
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

SCAN_SYSTEM = """Sen bir memecoin sinyal analistisın. Amerikan internet kültüründe memecoin fırsatı yaratabilecek trendleri tespit ediyorsun.

Bugünün tarihi: {date}

Kurallar:
- Her sinyal için heat: hot (hemen bas), warm (takip et), cool (zayıf)
- Token isimleri kısa ve komik olmalı
- Türkçe yaz
- Gerçekçi ve güncel ol

Yanıtı düz metin olarak ver, her sinyal şu formatta:
🔥 HOT / ⚡ WARM / 📡 COOL
Kaynak: ...
Açıklama: ...
Token fikirleri: $TOKEN1 $TOKEN2
Ne yapmalısın: ...
---"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📡 *MEME RADAR BOT*\n\n"
        "Kullanılabilir komutlar:\n\n"
        "/tara — Günlük sabah taraması\n"
        "/etkinlik — Canlı etkinlik modu\n"
        "/haftalik — Haftalık derin analiz\n"
        "/hayvan — Hayvan meme odağı\n"
        "/politik — Politik figür odağı\n"
        "/takvim — Bugünün ulusal günleri\n"
        "/absurt — Absürt haber odağı",
        parse_mode="Markdown"
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str = "daily", focus: str = "all"):
    msg = await update.message.reply_text("🔄 Taranıyor, bekle...")

    mode_prompts = {
        "daily": "Günlük sabah taraması. Amerika'da bu sabah ne konuşuluyor? Viral olan var mı?",
        "event": "Canlı etkinlik modu. Bugün büyük bir Amerikan etkinliği var mı? Anlık viral moment nerede?",
        "weekly": "Derin haftalık analiz. Bu hafta Amerikan internet kültüründe hangi temalar öne çıktı?"
    }

    focus_prompts = {
        "all": "tüm kategoriler",
        "animals": "özellikle viral hayvan memleri",
        "politics": "özellikle Amerikan politikacıları ve absürt açıklamalar",
        "calendar": "özellikle bugünün ulusal günleri",
        "absurd": "özellikle absürt Amerikan haberleri (Florida Man tarzı)"
    }

    date_str = datetime.now().strftime("%A, %B %d, %Y")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SCAN_SYSTEM.format(date=date_str),
            messages=[{
                "role": "user",
                "content": f"{mode_prompts.get(mode, mode_prompts['daily'])}\nOdak: {focus_prompts.get(focus, focus_prompts['all'])}\n\nEn az 4, en fazla 6 sinyal ver."
            }]
        )

        result = response.content[0].text
        header = f"📡 *MEME RADAR* — {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        await msg.edit_text(header + result, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Scan error: {e}")
        await msg.edit_text(f"❌ Hata: {str(e)}")

async def cmd_tara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="daily", focus="all")

async def cmd_etkinlik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="event", focus="all")

async def cmd_haftalik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="weekly", focus="all")

async def cmd_hayvan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="daily", focus="animals")

async def cmd_politik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="daily", focus="politics")

async def cmd_takvim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="daily", focus="calendar")

async def cmd_absurt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await scan(update, context, mode="daily", focus="absurd")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tara", cmd_tara))
    app.add_handler(CommandHandler("etkinlik", cmd_etkinlik))
    app.add_handler(CommandHandler("haftalik", cmd_haftalik))
    app.add_handler(CommandHandler("hayvan", cmd_hayvan))
    app.add_handler(CommandHandler("politik", cmd_politik))
    app.add_handler(CommandHandler("takvim", cmd_takvim))
    app.add_handler(CommandHandler("absurt", cmd_absurt))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
