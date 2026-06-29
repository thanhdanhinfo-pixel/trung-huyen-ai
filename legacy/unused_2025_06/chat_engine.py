from agents.brain_agent import BrainAgent 
from services.context_builder import build_context

agent = BrainAgent()

def chat(question:str):
    result = agent.answer(question)
    context = build_context(result["documents"])
    return {
        "question": question,
        "context": context,
        "status": "prepared"
    }
