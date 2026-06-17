class ReflectionEngine:
    def review(self, question, answer):
        return {
            "question": question,
            "answer_length": len(answer),
            "needs_improvement": len(answer) < 100
        }
