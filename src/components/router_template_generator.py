from langchain_core.prompts import PromptTemplate
from src.logger import logging
import os

# CLEANER VERSION: No JSON instructions, just decision logic.
# The Pydantic model in router_llm.py handles the structure!
router_template = """
You are the Traffic Controller for a Banking Security System.
Your job is to classify the user's intent into one of two categories.

### DECISION GUIDELINES:

1. **CHAT (Conversational)** -> CHOOSE THIS FOR GREETINGS!
   - Greetings: "hi", "hello", "hey", "good morning".
   - Meta-questions: "who are you?", "what can you do?", "help".
   - Inputs that contain NO money, NO locations, and NO transaction verbs.
   - Example: "hi" -> CHAT
   - Example: "are you a bot?" -> CHAT

2. **SEARCH (Fraud Detection)**
   - Inputs describing a TRANSACTION, MONEY, or RISK.
   - Keywords: transfer, sent, $, usd, panama, account, wire, fraud, scam.
   - Example: "sent $50k" -> SEARCH
   - Example: "is this transfer safe?" -> SEARCH

### USER INPUT:
{query}
"""

template = PromptTemplate(
    template=router_template,
    input_variables=['query']
)

logging.info('saving router template')
if not os.path.exists("router_template.json"):
    pass 

template.save('router_template.json')
logging.info('✅ Optimized Router Template Saved.')