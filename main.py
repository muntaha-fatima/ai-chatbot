# Chainlit aur Gemini ko import karo
import chainlit as cl
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env file se environment variables load karo (jaise API key)
load_dotenv()

# Google Gemini API key set karo
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini model ka object banao (1.5 flash use ho raha hai)
main_model = genai.GenerativeModel("gemini-1.5-flash")

# Ek Agent class define ki gayi hai jo alag alag bots ko represent karti hai
class Agent:
    def __init__(self, name, instructions):
        self.name = name  # Agent ka naam
        self.instructions = instructions  # Agent ko kya karna hai (uske instructions)

    def run_sync(self, prompt):
        # User ke prompt ke sath instructions add karke Gemini se jawab lo
        full_prompt = f"{self.instructions}\nUser says: {prompt}"
        response = main_model.generate_content(full_prompt)
        return response

# Coder aur Planner agents banaye gaye hain
coder_bot = Agent(name="CoderBot", instructions="You write code snippets.")  # Coding ke liye
planner_bot = Agent(name="PlannerBot", instructions="You help with project planning.")  # Planning ke liye

# Chat history list banayi gayi hai taake conversation track ho
chat_history = []

# Calculator function banaya gaya hai jo math expressions evaluate karega
async def calculator(expression):
    try:
        # ⚠️ WARNING: 'eval' dangerous ho sakta hai, sirf trusted input pe use karo
        result = eval(expression, {"__builtins__": None}, {})  # Safe scope
        return f"Calculator Result: {result}"
    except Exception as e:
        return f"Calculator Error: {str(e)}"

# Jab user koi message bheje to yeh function run hota hai
@cl.on_message
async def main_handler(message: cl.Message):
    global chat_history

    # User ka message history mein add karo
    chat_history.append(("User", message.content))

    # Command ke mutabiq agents ko use karo
    if message.content.startswith("code:"):
        # Code likhne ke liye CoderBot
        prompt = message.content[5:].strip()
        response = coder_bot.run_sync(prompt)
        bot_reply = response.text

    elif message.content.startswith("plan:"):
        # Planning ke liye PlannerBot
        prompt = message.content[5:].strip()
        response = planner_bot.run_sync(prompt)
        bot_reply = response.text

    elif message.content.startswith("calc:"):
        # Calculation ke liye calculator function
        expr = message.content[5:].strip()
        bot_reply = await calculator(expr)

    else:
        # Normal Gemini se conversation
        response = main_model.generate_content(message.content)
        bot_reply = response.text

    # Bot ka reply history mein add karo
    chat_history.append(("Bot", bot_reply))

    # Last 10 messages dikhane ke liye text bana lo
    history_text = "\n".join([f"{speaker}: {text}" for speaker, text in chat_history[-10:]])
    await cl.Message(content=history_text).send()
