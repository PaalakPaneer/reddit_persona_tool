import os
import sys
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
import praw
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


def get_reddit_username(url: str) -> str:
    parts = url.rstrip("/").split("/")
    username = parts[-1]
    if username.startswith("u/"):
        username = username[2:]
    return username


def scrape_user_data(username: str, limit: int = 50):
    """Scrapes recent posts and comments from a Reddit user."""
    user = reddit.redditor(username)
    posts = []
    comments = []

    try:
        for submission in user.submissions.new(limit=limit):
            posts.append({
                "title": submission.title,
                "subreddit": str(submission.subreddit),
                "score": submission.score,
                "created_utc": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat(),
                "text": submission.selftext,
                "url": submission.url
            })

        for comment in user.comments.new(limit=limit):
            comments.append({
                "body": comment.body,
                "subreddit": str(comment.subreddit),
                "score": comment.score,
                "created_utc": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
                "link": f"https://www.reddit.com{comment.permalink}"
            })
    except Exception as error:
        print(f"Error scraping user: {error}")

    return posts, comments


def generate_persona_with_gpt(username: str, posts: list, comments: list) -> dict:
    """Sends Reddit data to GPT-4 and returns the generated persona."""
    prompt = f"""
You are an expert researcher tasked with writing a detailed and expressive user persona from a Reddit user's public posts and comments.

Below is activity from Reddit user u/{username}. Your goal is to analyze their behavioral signals and **write a full narrative-style persona document** that covers:

---

1. **Name & Archetype**  
Suggest a persona name (even a made-up one is fine) and assign a Jungian-style archetype (The Creator, The Seeker, The Sage, etc.).

2. **Basic Demographics**  
Age range, possible location (city/country), occupation guess, and anything that points to their social status or lifestyle.

3. **Personality & Traits**  
Describe personality in natural language, including MBTI-style insights (e.g., “She’s likely an ENFP – extroverted, intuitive, and spontaneous.”)

4. **Writing Style**  
Describe how they express themselves online — slang use, humor, tone, verbosity, spelling, grammar, sentence structure, etc.

5. **Habits & Behavior**  
Summarize their most common behaviors, e.g., do they post more than comment? Do they engage in NSFW content? What themes recur?

6. **Motivations**  
What drives this person to post? Express themselves? Connect with communities? Think about psychological drivers.

7. **Frustrations**  
What annoys them, frustrates them, or comes through as emotional pain points in their posts?

8. **Interests & Communities**  
Which subreddits are they active in? What hobbies, fandoms, or internet cultures do they belong to?

9. **Citations**  
Give at least 5 post or comment snippets (with subreddit name and link) that justify your conclusions. These should be short quotes (1–2 sentences each).

---

Make the result rich in personality, formatted for a designer/marketer audience. 
IMPORTANT: Output must be valid JSON ONLY — no Markdown, no bullet points, no explanation, no code formatting. Just pure JSON.
Make sure all fields are present and well-structured.

Reddit Posts:
{json.dumps(posts[:20], indent=2)}

Reddit Comments:
{json.dumps(comments[:20], indent=2)}
"""
    print("🧠 Sending data to OpenAI...")

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    result = response.choices[0].message.content.strip()

    try:
        persona_data = json.loads(result)
        # 🔧 Force specific fields to be lists if they’re mistakenly returned as strings
        for key in ["traits", "interests", "frustrations", "motivations", "favorite_subreddits"]:
            if isinstance(persona_data.get(key), str):
                persona_data[key] = [persona_data[key]]
        return persona_data
    except json.JSONDecodeError:
        print("⚠️ GPT returned non-JSON content. Saving raw response.")
        return {"raw_response": result}


def save_persona(username: str, persona_data: dict) -> str:
    """Saves the generated persona to a JSON file."""
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", f"{username}_persona.json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(persona_data, file, indent=2, ensure_ascii=False)
    print(f"✅ Persona saved to {filepath}")
    return filepath


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python persona_generator.py https://www.reddit.com/user/USERNAME/")
        return

    url = sys.argv[1]
    username = get_reddit_username(url)
    print(f"Username extracted: u/{username}")

    print(f"🔍 Scraping Reddit data for u/{username}...")
    posts, comments = scrape_user_data(username)

    print(f"🧠 Generating persona for u/{username}...")
    persona_data = generate_persona_with_gpt(username, posts, comments)

    save_persona(username, persona_data)


if __name__ == "__main__":
    main()
