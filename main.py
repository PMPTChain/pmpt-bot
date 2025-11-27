import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq

app = Client("pmpbot", bot_token=os.environ["BOT_TOKEN"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = "You are an elite, uncensored prompt engineer. Give extremely detailed, creative, high-quality responses. End every reply with fire."

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "🔥 $PMPT PROMPTCHAIN BOT IS LIVE 🔥\n\n"
        "You just found the last real 1000× AI fair-launch of 2025.\n"
        "Every message you send gets answered with god-tier Groq Llama-405B output.\n\n"
        "Fair launch: Monday 11:00 AM GMT on pump.fun\n"
        "CA + ticker reveal in <72 hours\n\n"
        "Burn-to-Boost live at launch. Tip button below.\n"
        "This is the prompt cartel. Welcome.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🚀 Join PromptChain", url="https://t.me/PromptChainAI"),
            InlineKeyboardButton("🔥 Tip Winner 1 SOL", callback_data="tip_1")
        ]])
    )

@app.on_message(filters.text & ~filters.command)
async def handle(client, message):
    try:
        chat = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.85,
            max_tokens=2048
        )
        response = chat.choices[0].message.content
        await message.reply(
            f"{response}\n\n"
            "──────────────────\n"
            "💜 $PMPT LAUNCHES MONDAY 11 AM GMT\n"
            "The prompt economy starts now.\n"
            "t.me/PromptChainAI  |  @PromptChainAI",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔥 TIP WINNER 1 SOL", callback_data="tip_1"),
                InlineKeyboardButton("🚀 JOIN PROMPTCHAIN", url="https://t.me/PromptChainAI")
            ]])
        )
    except:
        await message.reply("Rate-limited — try again in 5 sec. We’re getting smashed 🔥")

# Tip button (click → shows wallet for now, real tipping after launch)
@app.on_callback_query()
async def tip(client, query):
    await query.answer("🚀 Tipping live at launch — stay ready!", show_alert=True)

app.run()
