import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq

import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Poll
from typing import List, Dict

# Add to your existing app = Client(...)
DUEL_SUBMISSIONS: List[Dict] = []  # List of {'user_id': int, 'prompt': str, 'response': str}
ACTIVE_DUEL = None  # Current duel state

@app.on_message(filters.command("duel_start") & filters.user(id=OWNER_ID))  # OWNER_ID = your Telegram ID
async def start_duel(client, message):
    global ACTIVE_DUEL
    if len(DUEL_SUBMISSIONS) < 8:
        await message.reply("Need at least 8 submissions to start duel!")
        return
    random.shuffle(DUEL_SUBMISSIONS)
    bracket = pair_bracket(DUEL_SUBMISSIONS)
    ACTIVE_DUEL = {'round': 1, 'bracket': bracket, 'winners': []}
    await message.reply("🔥 PROMPT DUEL STARTED! Round 1 bracket posted.")
    await post_round_polls(client, bracket)

def pair_bracket(submissions: List[Dict]) -> List[List[Dict]]:
    bracket = []
    for i in range(0, len(submissions), 2):
        pair = submissions[i:i+2]
        bracket.append(pair)
    return bracket

async def post_round_polls(client, bracket: List[List[Dict]]):
    for pair in bracket:
        poll_text = f"DUEL ROUND {ACTIVE_DUEL['round']}\n\nPair {len(bracket)}:\n"
        options = []
        for j, sub in enumerate(pair):
            poll_text += f"Player {j+1}: {sub['prompt'][:100]}...\n"
            options.append(f"Player {j+1}: {sub['prompt'][:50]}...")
        poll = await client.send_poll(
            chat_id=CHANNEL_ID,  # Your TG channel ID
            question=poll_text,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        # Store poll ID for results
        pair.append({'poll_id': poll.id})
    # Timer for results in 30 min – use asyncio.sleep or scheduler

@app.on_poll()
async def handle_poll_results(client, poll):
    if poll.poll.id in [p.get('poll_id') for pair in ACTIVE_DUEL['bracket'] for p in pair]:
        # Get winner (highest votes)
        winner_index = poll.poll.options.index(max(poll.poll.options, key=lambda o: o.voter_count))
        winner = ACTIVE_DUEL['bracket'][poll.poll.id // len(options)] [winner_index]  # Simplified – track properly
        ACTIVE_DUEL['winners'].append(winner)
        # Burn loser stake (call on-chain burn function here)
        await burn_loser_stake(client, loser['user_id'], 0.1)  # 10% burn
        if len(ACTIVE_DUEL['winners']) == len(ACTIVE_DUEL['bracket']):
            # Next round
            ACTIVE_DUEL['round'] += 1
            ACTIVE_DUEL['bracket'] = pair_bracket(ACTIVE_DUEL['winners'])
            ACTIVE_DUEL['winners'] = []
            if len(ACTIVE_DUEL['bracket']) == 1:
                # Final winner
                champion = ACTIVE_DUEL['bracket'][0][0]
                await client.send_message(CHANNEL_ID, f"🏆 CHAMPION: {champion['prompt'][:100]}!\nMinted as NFT #001")
                await mint_nft(client, champion)  # Call NFT mint
                ACTIVE_DUEL = None
            else:
                await post_round_polls(client, ACTIVE_DUEL['bracket'])

async def burn_loser_stake(client, user_id, percent):
    # Call Solana burn RPC or on-chain function
    # For now, simulate
    await client.send_message(CHANNEL_ID, f"🔥 Loser burned {percent*100}% stake!")

async def mint_nft(client, submission):
    # Call Metaplex or thirdweb mint
    await client.send_message(CHANNEL_ID, "NFT minted – royalties forever!")

# Run with your existing app.run()

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
