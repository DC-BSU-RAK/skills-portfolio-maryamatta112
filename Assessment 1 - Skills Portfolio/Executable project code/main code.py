import tkinter as tk
from tkinter import messagebox
import requests
import html
import random


BG = "#eaf0ff"
CARD = "#ffffff"


class TriviaAPI:
    URL = "https://opentdb.com/api.php"
    CAT_URL = "https://opentdb.com/api_category.php"

    def get_categories(self):
        return requests.get(self.CAT_URL).json()["trivia_categories"]

    def get_questions(self, amount, difficulty=None, qtype=None, category=None):
        params = {"amount": amount}
        if difficulty: params["difficulty"] = difficulty
        if qtype: params["type"] = qtype
        if category: params["category"] = category
        return requests.get(self.URL, params=params).json()["results"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Data Driven Quiz App")
        self.geometry("900x600")
        self.configure(bg=BG)

        self.api = TriviaAPI()

        self.frames = {}
        for Page in (HomePage, QuizPage):
            frame = Page(self)
            self.frames[Page.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show("HomePage")

    def show(self, page):
        self.frames[page].tkraise()


class HomePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        card = tk.Frame(self, bg=CARD, padx=20, pady=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Open Trivia Quiz",
                 font=("Arial", 22, "bold"), bg=CARD).pack(pady=10)

        tk.Label(card, text="Number of Questions", bg=CARD).pack(anchor="w")
        self.amount = tk.Entry(card)
        self.amount.insert(0, "5")
        self.amount.pack(anchor="w")

        tk.Button(card, text="Start Quiz", command=self.start).pack(pady=15)

    def start(self):
        quiz = self.master.frames["QuizPage"]
        quiz.load(int(self.amount.get()))
        self.master.show("QuizPage")


class QuizPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.questions = []
        self.i = 0
        self.score = 0
        self.answer = tk.StringVar()

        self.card = tk.Frame(self, bg=CARD, padx=20, pady=20)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        self.q = tk.Label(self.card, wraplength=600, bg=CARD)
        self.q.pack(pady=10)

        self.opts = tk.Frame(self.card, bg=CARD)
        self.opts.pack()

        self.info = tk.Label(self.card, bg=CARD)
        self.info.pack()

        tk.Button(self.card, text="Submit", command=self.submit).pack(pady=5)
        tk.Button(self.card, text="Next", command=self.next).pack()

    def load(self, amount):
        self.questions = self.master.api.get_questions(amount)
        self.i = 0
        self.score = 0
        self.show_q()

    def show_q(self):
        for w in self.opts.winfo_children():
            w.destroy()

        if self.i >= len(self.questions):
            self.q.config(text=f"Finished! Score: {self.score}")
            return

        q = self.questions[self.i]
        self.correct = html.unescape(q["correct_answer"])
        answers = [html.unescape(a) for a in q["incorrect_answers"]] + [self.correct]
        random.shuffle(answers)

        self.q.config(text=html.unescape(q["question"]))
        self.answer.set("")

        for a in answers:
            tk.Radiobutton(self.opts, text=a, variable=self.answer,
                           value=a, bg=CARD).pack(anchor="w")

    def submit(self):
        if self.answer.get() == self.correct:
            self.score += 1
            messagebox.showinfo("Correct", "Correct answer!")
        else:
            messagebox.showinfo("Wrong", "Correct: " + self.correct)

    def next(self):
        self.i += 1
        self.show_q()


if __name__ == "__main__":
    App().mainloop()
