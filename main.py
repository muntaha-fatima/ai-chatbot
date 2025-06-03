import chainlit as cl
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API key configure karo
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Main model
main_model = genai.GenerativeModel("gemini-1.5-flash")

# Extra agents
class Agent:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

    def run_sync(self, prompt):
        full_prompt = f"{self.instructions}\nUser says: {prompt}"
        response = main_model.generate_content(full_prompt)
        return response

coder_bot = Agent(name="CoderBot", instructions="You write code snippets.")
planner_bot = Agent(name="PlannerBot", instructions="You help with project planning.")

# Chat history storage
chat_history = []

async def calculator(expression):
    try:
        # WARNING: eval can be unsafe, use with trusted input or use a safe parser
        result = eval(expression, {"__builtins__": None}, {})
        return f"Calculator Result: {result}"
    except Exception as e:
        return f"Calculator Error: {str(e)}"

@cl.on_message
async def main_handler(message: cl.Message):
    global chat_history

    # Add user message to history
    chat_history.append(("User", message.content))


    # Multi-agent switching
    if message.content.startswith("code:"):
        prompt = message.content[5:].strip()
        response = coder_bot.run_sync(prompt)
        bot_reply = response.text
    elif message.content.startswith("plan:"):
        prompt = message.content[5:].strip()
        response = planner_bot.run_sync(prompt)
        bot_reply = response.text

    # Calculator function call
    elif message.content.startswith("calc:"):
        expr = message.content[5:].strip()
        bot_reply = await calculator(expr)

    # Normal conversation
    else:
        response = main_model.generate_content(message.content)
        bot_reply = response.text

    # Add bot reply to history
    chat_history.append(("Bot", bot_reply))

    # Show full chat history
    history_text = "\n".join([f"{speaker}: {text}" for speaker, text in chat_history[-10:]])  # last 10 messages
    await cl.Message(content=history_text).send()

