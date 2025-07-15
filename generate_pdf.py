import os
import json
import pdfkit
from jinja2 import Environment, FileSystemLoader

def load_persona_data(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)

def render_html(template_path, context):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    return template.render(context)

def generate_pdf(username):
    data_path = f"data/{username}_persona.json"
    template_path = "templates/persona_template.html"
    output_path = f"output/{username}_persona.pdf"

    print(f"Loading persona data from {data_path}...")
    data = load_persona_data(data_path)

    # Build the context to pass to the template
    context = {
        "name": data.get("Name") or username,
        "username": username,
        "archetype": data.get("Archetype", "N/A"),
        "age_range": data.get("Basic Demographics", {}).get("Age", "N/A"),
        "location_guess": data.get("Basic Demographics", {}).get("Location", "N/A"),
        "occupation_guess": data.get("Basic Demographics", {}).get("Occupation", "N/A"),
        "traits": data.get("Personality & Traits", {}).get("Description", "").split(". "),
        "interests": data.get("Interests & Communities", {}).get("Interests", []),
        "favorite_subreddits": data.get("Interests & Communities", {}).get("Active Subreddits", []),
        "frustrations": data.get("Frustrations", {}).get("Challenges", ""),
        "motivations": data.get("Motivations", {}).get("Driving Factors", ""),
        "personality_insights": {},  # Optional, can leave blank if not in data
        "writing_style": data.get("Writing Style", {}).get("Expression", "N/A"),
        "citations": data.get("Citations", [])
    }

    print("Rendering HTML...")
    html = render_html(template_path, context)

    os.makedirs("output", exist_ok=True)
    print(f"Generating PDF at {output_path}...")
    pdfkit.from_string(html, output_path)

    print(f"PDF saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python generate_pdf.py USERNAME")
    else:
        generate_pdf(sys.argv[1])
