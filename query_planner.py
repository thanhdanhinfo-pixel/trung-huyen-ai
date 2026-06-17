class QueryPlanner:
    def plan(self, question:str):
        return {
            "question": question,
            "steps":[
                "Phân tích câu hỏi",
                "Tìm tài liệu",
                "Xếp hạng ngữ cảnh",
                "Sinh câu trả lời",
                "Kiểm chứng"
            ]
        }
