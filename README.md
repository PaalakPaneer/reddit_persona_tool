Reddit Persona Generator
Generate a detailed psychological and behavioral persona for any public Reddit user using OpenAI GPT models and their Reddit activity.

Features
Scrapes a Reddit user’s posts and comments using the PRAW library.

Sends the data to OpenAI’s GPT model to build a structured persona.

Outputs a clean JSON file with citations.

Optional: Generate a styled PDF report using Jinja2 templates and pdfkit.

Dependencies
Install all required Python packages using:

nginx
Copy
Edit
pip install -r requirements.txt
Python packages:

praw

openai

python-dotenv

jinja2

pdfkit

External dependency (required for PDF generation):

wkhtmltopdf (must be installed separately)

Install wkhtmltopdf
Download from:

https://wkhtmltopdf.org/downloads.html

After installation:

Ensure it is added to your system PATH (you can select this during install).

Or manually add the binary path to your environment:

C:\Program Files\wkhtmltopdf\bin

To confirm installation:

wkhtmltopdf --version
Setup
Clone the repository:

git clone https://github.com/your-username/reddit-persona-generator

Create a .env file in the project root with the following content:

OPENAI_API_KEY=your_openai_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=any_user_agent_description

Install dependencies:

pip install -r requirements.txt

How to Use
1. Generate JSON Persona
Run the following command:

ruby
Copy
Edit
python persona_generator.py https://www.reddit.com/user/USERNAME/
This will:

Extract the Reddit username

Scrape recent posts and comments (up to 50 each)

Send the data to OpenAI

Save the persona as a JSON file in the data/ folder

2. Generate PDF Report (optional)
Make sure wkhtmltopdf is installed and on your system PATH.

Then run:

nginx
Copy
Edit
python generate_pdf.py USERNAME
This will:

Load the JSON file from data/USERNAME_persona.json

Render a styled HTML template

Generate a PDF in the output/ folder

File Structure
persona_generator.py — Reddit scraper + GPT persona builder

generate_pdf.py — HTML-to-PDF converter

templates/persona_template.html — Jinja2 template for the PDF

data/ — stores JSON persona files

output/ — stores generated PDF reports

Notes
The OpenAI output must be valid JSON only. Markdown, code blocks, or extra text will break the parser.

For best results, use gpt-4 or gpt-3.5-turbo if you don’t have GPT-4 access.

To Do (Optional Enhancements)
Add retry logic for OpenAI API failures

Enable scraping more than 50 items

Improve template styling

Add charts/visuals to the PDF