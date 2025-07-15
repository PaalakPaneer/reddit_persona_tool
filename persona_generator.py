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
    prompt = f"""
You are an AI researcher tasked with building a psychological and behavioral profile of a Reddit user from their public posts and comments.

Output a JSON object with the following keys (no markdown, no extra text, JSON only!):

- Name
- Archetype
- Basic Demographics:
    - Age
    - Location
    - Occupation
    - Social Status
- Personality & Traits:
    - Description
- Writing Style:
    - Expression
- Habits & Behavior:
    - Common Behaviors
- Motivations:
    - Driving Factors (Provide 3–5 distinct, specific points)
- Frustrations:
    - Challenges (Provide 3–5 distinct, specific points)
- Interests & Communities:
    - Interests (Provide 3–5 distinct, specific points)
    - Active Subreddits
- Citations:
    - A list of 5+ objects with:
        - quote
        - subreddit
        - url

Make sure each list field (Interests, Motivations, Frustrations, etc.) contains multiple specific entries, not a single paragraph or sentence.

Reddit Posts:
{json.dumps(posts[:20], indent=2)}

Reddit Comments:
{json.dumps(comments[:20], indent=2)}
"""

    print("Sending data to OpenAI...")

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content.strip()

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        print("GPT returned non-JSON content. Saving raw response.")
        return {"raw_response": result}


def save_persona(username: str, persona_data: dict):
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", f"{username}_persona.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(persona_data, f, indent=2, ensure_ascii=False)
    print(f"Persona saved to {filepath}")


def save_persona_txt(username: str, persona_data: dict):
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", f"{username}_persona.txt")

    if "raw_response" in persona_data:
        print("GPT response was invalid JSON, cannot save .txt persona.")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("GPT response could not be parsed. Raw content below:\n\n")
            f.write(persona_data["raw_response"])
        return

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"User Persona: u/{username}\n")
        f.write(f"Name: {persona_data.get('Name', 'N/A')}\n")
        f.write(f"Archetype: {persona_data.get('Archetype', 'N/A')}\n\n")

        # Basic Info
        f.write("Basic Info\n")
        basic = persona_data.get("Basic Demographics", {})
        f.write(f"Age Range: {basic.get('Age', 'N/A')}\n")
        f.write(f"Location: {basic.get('Location', 'N/A')}\n")
        f.write(f"Occupation: {basic.get('Occupation', 'N/A')}\n")
        f.write(f"Social Status: {basic.get('Social Status', 'N/A')}\n\n")

        # Traits
        f.write("Personality & Traits\n")
        traits = persona_data.get("Personality & Traits", {})
        f.write(f"{traits.get('Description', 'N/A')}\n\n")

        # Writing Style
        f.write("Writing Style\n")
        writing = persona_data.get("Writing Style", {})
        f.write(f"Expression: {writing.get('Expression', 'N/A')}\n\n")

        # Habits
        f.write("Habits & Behavior\n")
        habits = persona_data.get("Habits & Behavior", {})
        f.write(f"{habits.get('Common Behaviors', 'N/A')}\n\n")

        # Motivations
        f.write("Motivations\n")
        motiv = persona_data.get("Motivations", {}).get("Driving Factors", [])
        if isinstance(motiv, list):
            for m in motiv:
                f.write(f"- {m}\n")
        else:
            f.write(f"{motiv}\n")
        f.write("\n")

        # Frustrations
        f.write("Frustrations\n")
        frust = persona_data.get("Frustrations", {}).get("Challenges", [])
        if isinstance(frust, list):
            for fr in frust:
                f.write(f"- {fr}\n")
        else:
            f.write(f"{frust}\n")
        f.write("\n")

        # Interests
        f.write("Interests & Communities\n")
        interests = persona_data.get("Interests & Communities", {})
        f.write("Active Subreddits:\n")
        for sub in interests.get("Active Subreddits", []):
            f.write(f"- r/{sub}\n")
        f.write("\nInterests:\n")
        for interest in interests.get("Interests", []):
            f.write(f"- {interest}\n")
        f.write("\n")

        # Citations
        f.write("Citations\n")
        for cite in persona_data.get("Citations", []):
            f.write(f"{cite.get('subreddit', '')}: \"{cite.get('quote', '')}\"\n")
            f.write(f"{cite.get('url', '')}\n\n")

    print(f"Text file saved to {filepath}")

def normalize_list_fields(persona_data):
    """Ensure Interests and Subreddits are always lists."""
    communities = persona_data.get("Interests & Communities", {})

    if isinstance(communities.get("Interests"), str):
        communities["Interests"] = [s.strip() for s in communities["Interests"].split(",")]

    if isinstance(communities.get("Active Subreddits"), str):
        communities["Active Subreddits"] = [s.strip() for s in communities["Active Subreddits"].split(",")]

    persona_data["Interests & Communities"] = communities
    return persona_data

def main():
    if len(sys.argv) != 2:
        print("Usage: python persona_generator.py https://www.reddit.com/user/USERNAME/")
        return

    url = sys.argv[1]
    username = get_reddit_username(url)
    print(f"Username extracted: u/{username}")

    print(f"Scraping Reddit data for u/{username}...")
    posts, comments = scrape_user_data(username)

    print(f"Generating persona for u/{username}...")
    persona_data = generate_persona_with_gpt(username, posts, comments)
    persona_data = normalize_list_fields(persona_data)

    save_persona(username, persona_data)
    print(f"Generating .txt file for u/{username}...")
    save_persona_txt(username, persona_data)


if __name__ == "__main__":
    main()
