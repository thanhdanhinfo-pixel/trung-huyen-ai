class SelfImprovement:
    def suggest(self, report):
        if report.get("needs_improvement"):
            return ["Bổ sung ngữ cảnh","Tăng số nguồn tham chiếu"]
        return ["Đạt yêu cầu"]
