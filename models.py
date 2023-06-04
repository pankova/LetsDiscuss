class User:
    def __init__(self, name, hash, partner_id = 0):
        self.name = name
        self.hash = hash
        self.partner_id = partner_id


class Question:
    def __init__(self, id, text):
        self.id = id
        self.text = text


class Section:
    def __init__(self, id, page_order, text, questions):
        self.id = id
        self.page_order = page_order
        self.text = text
        self.questions = questions


class Option:
    def __init__(self, id, text):
        self.id = id
        self.text = text


class Answer:
    def __init__(self, question_text, user_answer, partner_answer):
        self.question_text = question_text
        self.user_answer = user_answer
        self.partner_answer = partner_answer
        

class SectionAnswer:
    def __init__(self, id, title, answers):
        self.id = id
        self.title = title
        self.answers = answers


class QuestionnareResult:
    def __init__(self, user_name, partner_name, sectionAnswers):
        self.user_name = user_name
        self.partner_name = partner_name
        self.sectionAnswers = sectionAnswers
