from services.semantic_search import search 

class BrainAgent:
    def answer(self, question:str):
        docs = search(question)
        return {
            "question": question,
            "documents": docs,
            "status": "ready_for_llm"
        }
