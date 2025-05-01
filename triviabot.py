import irc.client
import requests
import html
import threading
import random

class TriviaBot:
    def __init__(self, channel, nickname, server, port=6667):
        self.channel = channel
        self.nickname = nickname
        self.client = irc.client.Reactor()
        self.connection = self.client.server().connect(server, port, nickname)

        self.current_question = None
        self.correct_answer = None
        self.awaiting_answer = False
        self.answers_map = {}
        self.scores = {}
        self.max_score = 10

        self.category = None
        self.difficulty = None

        self.categories = self.get_categories()

        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("pubmsg", self.on_message)

        self.timer = None

    def on_connect(self, connection, event):
        connection.join(self.channel)

    def get_categories(self):
        try:
            resp = requests.get("https://opentdb.com/api_category.php")
            data = resp.json()
            return {c["name"].lower(): c["id"] for c in data["trivia_categories"]}
        except:
            return {}

    def fetch_trivia_question(self):
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        if self.category in self.categories:
            url += f"&category={self.categories[self.category]}"
        if self.difficulty in ["easy", "medium", "hard"]:
            url += f"&difficulty={self.difficulty}"

        try:
            response = requests.get(url)
            data = response.json()

            if data.get("response_code") != 0 or not data.get("results"):
                print("No trivia questions found for the selected category/difficulty, falling back to random question.")
                return self.fetch_random_trivia_question()

            result = data["results"][0]
            question = html.unescape(result["question"])
            correct = html.unescape(result["correct_answer"])
            incorrect = [html.unescape(i) for i in result["incorrect_answers"]]
            options = incorrect + [correct]
            random.shuffle(options)
            self.answers_map = {chr(65 + i): opt for i, opt in enumerate(options)}
            correct_letter = [k for k, v in self.answers_map.items() if v == correct][0]
            return question, correct_letter.lower(), correct_letter
        except Exception as e:
            print("Error fetching trivia:", e)
            return None, None, None

    def fetch_random_trivia_question(self):
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        try:
            response = requests.get(url)
            data = response.json()

            if data.get("response_code") != 0 or not data.get("results"):
                print("Error fetching random trivia.")
                return None, None, None

            result = data["results"][0]
            question = html.unescape(result["question"])
            correct = html.unescape(result["correct_answer"])
            incorrect = [html.unescape(i) for i in result["incorrect_answers"]]
            options = incorrect + [correct]
            random.shuffle(options)
            self.answers_map = {chr(65 + i): opt for i, opt in enumerate(options)}
            correct_letter = [k for k, v in self.answers_map.items() if v == correct][0]
            return question, correct_letter.lower(), correct_letter
        except Exception as e:
            print("Error fetching random trivia:", e)
            return None, None, None

    def ask_question(self):
        if self.awaiting_answer:
            return

        question, correct_answer, correct_letter = self.fetch_trivia_question()
        if question:
            self.current_question = question
            self.correct_answer = correct_letter.lower()
            self.awaiting_answer = True

            self.connection.privmsg(self.channel, f"🧠 Trivia: {self.current_question}")
            for letter, option in sorted(self.answers_map.items()):
                self.connection.privmsg(self.channel, f"  {letter}: {option}")
            self.connection.privmsg(self.channel, "(Reply with A, B, C, or D — 30 seconds!)")

            if self.timer:
                self.timer.cancel()

            self.timer = threading.Timer(30.0, self.reveal_answer)
            self.timer.start()
        else:
            self.connection.privmsg(self.channel, "⚠ Could not load a question.")

    def on_message(self, connection, event):
        user = irc.client.NickMask(event.source).nick
        message = event.arguments[0].strip()

        if message.startswith("!trivia") and not self.awaiting_answer:
            self.scores.clear()
            self.category = self.difficulty = None

            parts = message.split(" ", 1)
            if len(parts) > 1 and "=" in parts[1]:
                try:
                    cat, diff = parts[1].split("=", 1)
                    self.category = cat.strip().lower()
                    self.difficulty = diff.strip().lower()
                except:
                    pass

            self.connection.privmsg(self.channel, f"🎮 New game! Category: {self.category}, Difficulty: {self.difficulty}")
            self.ask_question()

        elif self.awaiting_answer and message.upper() in self.answers_map:
            guess = message.lower()
            if guess == self.correct_answer:
                self.awaiting_answer = False
                self.scores[user] = self.scores.get(user, 0) + 1
                score = self.scores[user]
                self.connection.privmsg(self.channel, f"✅ Correct, {user}! Score: {score}/10")

                self.display_scores()

                if score >= self.max_score:
                    self.connection.privmsg(self.channel, f"🏆 {user} wins the quiz!")
                    self.scores.clear()
                    self.category = self.difficulty = None
                else:
                    self.ask_question()

        elif message == "!score":
            self.display_scores()

        elif message == "!categories":
            cats = sorted(self.categories.keys())
            self.connection.privmsg(self.channel, "📚 Categories: " + ", ".join(cats))

    def display_scores(self):
        if not self.scores:
            self.connection.privmsg(self.channel, "📊 No scores yet.")
        else:
            leaderboard = " | ".join(f"{u}: {s}" for u, s in sorted(self.scores.items(), key=lambda x: -x[1]))
            self.connection.privmsg(self.channel, f"📊 Scores: {leaderboard}")

    def reveal_answer(self):
        if self.awaiting_answer:
            self.awaiting_answer = False
            correct_text = self.answers_map[self.correct_answer.upper()]
            self.connection.privmsg(self.channel, f"⏰ Time's up! The correct answer was: {self.correct_answer.upper()} - {correct_text}")
            self.display_scores()
            self.ask_question()

    def run(self):
        self.client.process_forever()

if __name__ == "__main__":
    bot = TriviaBot(channel="#test", nickname="TriviaBot", server="irc.libera.chat")
    bot.run()
