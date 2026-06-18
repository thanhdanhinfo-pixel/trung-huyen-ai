def check(answer:str, context:str):
    if not context.strip():
        return {
            "approved": False,
            "reason": "Không có ngữ cảnh."
        }
    return {
        "approved": True,
        "reason": "Có ngữ cảnh để đối chiếu."
    }
