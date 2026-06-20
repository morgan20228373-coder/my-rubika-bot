from rubpy import BotClient
from rubpy.bot.models import (
    Button,
    Keypad,
    KeypadRow,
    ButtonTypeEnum,
    ChatKeypadTypeEnum
)
import requests
import json
import os

BOT_TOKEN = "BHDEHE0NPWDAOUSTSLNXVVCCHVQEQPYIBXETNIUOGESVZLPEXIVATZHMQBWBYOFS"
OPENROUTER_API_KEY = "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"

MODEL = "nex-agi/nex-n2-pro:free"

BOT_NAME = "Icarus"
MODEL_NAME = "Nova 130"

CREATOR = "@i_d_098"

OWNER_COMMAND = "I am the creator of you robot model Nova 130"

bot = BotClient(BOT_TOKEN)

# ------------------
# ذخیره سازی
# ------------------

memory = {}
rules = []
owner = None


def load_file(name, default):
    if os.path.exists(name):
        try:
            with open(name, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return default


def save_file(name, data):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


memory = load_file("memory.json", {})
rules = load_file("rules.json", [])
owner = load_file("owner.json", {}).get("id")


# ------------------
# منو شیشه‌ای
# ------------------

def send_menu(chat_id):
    keypad = Keypad(
        rows=[
            KeypadRow(
                buttons=[
                    Button(id="help", type=ButtonTypeEnum.SIMPLE, button_text="📚 راهنما"),
                    Button(id="clear", type=ButtonTypeEnum.SIMPLE, button_text="🗑 پاکسازی"),
                ]
            ),
            KeypadRow(
                buttons=[
                    Button(id="restart", type=ButtonTypeEnum.SIMPLE, button_text="🔄 شروع مجدد")
                ]
            )
        ],
        resize_keyboard=True
    )

    bot.edit_chat_keypad(chat_id, ChatKeypadTypeEnum.NEW, keypad)


# ------------------
# AI
# ------------------

def ask_ai(uid, text):
    if uid not in memory:
        memory[uid] = []

    system = f"""
تو Icarus هستی.

مدل: {MODEL_NAME}
سازنده: {CREATOR}

فارسی جواب بده.
"""

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system}
        ] + memory[uid] + [
            {"role": "user", "content": text}
        ]
    }

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json=data
    )

    answer = r.json()["choices"][0]["message"]["content"]

    memory[uid].append({"role": "user", "content": text})
    memory[uid].append({"role": "assistant", "content": answer})

    save_file("memory.json", memory)

    return answer


# ------------------
# Handler
# ------------------

def handler(client, update):

    global owner, rules

    if not update.new_message:
        return

    chat = update.chat_id
    text = update.new_message.text

    if not text:
        return

    t = text.strip().lower()

    button_id = None
    try:
        button_id = update.new_message.aux_data.button_id
    except:
        pass

    # ------------------
    # سازنده
    # ------------------

    if owner is None and text == OWNER_COMMAND:
        owner = chat
        save_file("owner.json", {"id": owner})

        client.send_message(chat, "✅ Creator registered.")
        return

    # ------------------
    # HELP
    # ------------------

    if button_id == "help" or t in ["help", "راهنما", "📚 راهنما"]:
        client.send_message(
            chat,
            f"🤖 {BOT_NAME}\nمدل: {MODEL_NAME}\nسازنده: {CREATOR}"
        )
        return

    # ------------------
    # CLEAR
    # ------------------

    if button_id == "clear" or t in ["clear", "پاکسازی", "🗑 پاکسازی"]:
        memory.pop(chat, None)
        save_file("memory.json", memory)

        client.send_message(chat, "🗑 Memory cleared")
        return

    # ------------------
    # RESTART
    # ------------------

    if button_id == "restart" or t in ["restart", "شروع مجدد", "🔄 شروع مجدد"]:
        memory.pop(chat, None)
        save_file("memory.json", memory)

        client.send_message(chat, "🔄 Restarted")

        send_menu(chat)
        return

    # ------------------
    # اولین پیام
    # ------------------

    if t == "/start":
        send_menu(chat)
        client.send_message(chat, f"سلام 👋 من {BOT_NAME} هستم")
        return

    # ------------------
    # AI
    # ------------------

    answer = ask_ai(chat, text)
    client.send_message(chat, answer[:4000])


# ------------------
# Run
# ------------------

bot.add_handler(handler)

print(f"{BOT_NAME} ONLINE - {MODEL_NAME}")

bot.run()