class PlannerAgent:
    def create_plan(self, goal:str):
        return {
            "goal": goal,
            "steps":[
                "Thu thập dữ liệu",
                "Phân tích",
                "Đề xuất",
                "Thực thi",
                "Đánh giá"
            ]
        }
