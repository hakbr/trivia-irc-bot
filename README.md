Here's a suitable GitHub repository description and `README.md` summary for your IRC Trivia Bot:

---

### **Repository Name:** `irc-trivia-bot`

### **GitHub Description:**
> 🎮 A feature-rich IRC trivia bot using OpenTDB for questions. Supports categories, difficulty levels, scoring, and real-time interaction.

---

### **README.md (Suggested Content):**

```markdown
# IRC Trivia Bot 🧠

A lightweight IRC trivia bot that fetches questions from the [Open Trivia Database (OpenTDB)](https://opentdb.com/). Users can play interactive trivia games directly in an IRC channel with support for scoring, categories, and difficulty levels.

## Features

- ✅ Connects to any IRC server and joins a specified channel
- 📚 Select trivia category and difficulty using `!trivia <category>=<difficulty>`
- 🔄 Random fallback if no questions match selection
- ⏱ Timed responses (30 seconds per question)
- 🧩 Multiple choice format with shuffled answers
- 📈 Tracks individual scores (up to 10 points to win)
- 🏆 Announces winner and resets game
- 💬 Commands:  
  - `!trivia` — Start a new trivia game  
  - `!score` — Show current leaderboard  
  - `!categories` — List available categories

## Installation

```bash
pip install irc requests
```

## Usage

Edit the last lines of the script to configure your IRC server, channel, and bot nickname:

```python
if __name__ == "__main__":
    bot = TriviaBot(channel="#yourchannel", nickname="TriviaBot", server="irc.libera.chat")
    bot.run()
```

Run the bot with:

```bash
python trivia_bot.py
```

## Requirements

- Python 3.6+
- `irc` library
- `requests` library

## Notes

- Uses a 30-second timeout for responses.
- Automatically rotates to a new question after each round or timeout.
- Supports real-time multiplayer play.

## License

GPL v3
