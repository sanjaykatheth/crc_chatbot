import json

class UserChat:
    def __init__(self):
        # Initialize properties
        self.user_id = None 
        self.user_email=None
        self.user_question = None
        self.sql = None
        self.plot_code = None
        self.sql_result = None

    def to_json(self):
        return {
            "user_question": self.user_question,
            "sql": self.sql,
            "plot_code": self.plot_code,
            "sql_result": self.sql_result
        }


class UserChatList:
    def __init__(self):
        # Initialize properties
        self.chat_history = []

    def AddHistory(self, chat):
        self.chat_history.append(chat)

    def to_json(self):
        return [chat.to_json() for chat in self.chat_history]
    def __iter__(self):
        return iter(self.chat_history)

    def __len__(self):
        return len(self.chat_history)

    def __getitem__(self, index):
        return self.chat_history[index]