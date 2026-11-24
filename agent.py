"""
agent.py - Person 3 (AI)

Job: use Gemini to (1) explain a prediction in plain English and
(2) act as an agent that can call our Python functions as tools.

The Gemini API key is read from the .env file - never type it in this file.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env into environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

# Instructions Gemini must always follow (judges will ask about this!)
SYSTEM_INSTRUCTION = (
    "You explain India VIX predictions to retail option traders in simple English. "
    "Always mention that predictions are uncertain. "
    "Never recommend buying or selling any specific option or stock."
)


def explain(prediction):
    """Return a short plain-English explanation of a prediction dictionary.

    FAKE VERSION - returns fixed text until the Gemini call is built.
    """
    # TODO(Person 3):
    #   1. from google import genai; client = genai.Client(api_key=API_KEY)
    #   2. Build a prompt that includes the prediction dictionary
    #   3. Call client.models.generate_content(...) with SYSTEM_INSTRUCTION
    #   4. Return the response text (3 lines max)
    direction = prediction["direction"]
    conf = round(prediction["confidence"] * 100)
    return (
        f"Our model gives a {conf}% chance that VIX will {direction} over the next 5 trading days. "
        "A rising VIX usually means bigger market swings, which helps option buyers and adds risk for sellers. "
        "This is a probability, not a certainty."
    )


def ask_agent(question, history=None):
    """Answer a user's question, letting Gemini call our tools.

    FAKE VERSION - echoes the question until the agent is built.
    """
    # TODO(Person 3): give Gemini tools (function calling):
    #   get_latest_vix() and model.predict_today()
    #   so it decides when to fetch data / run the model before answering.
    return f"(Agent not built yet) You asked: {question}"


if __name__ == "__main__":
    from model import predict_today
    print(explain(predict_today()))
