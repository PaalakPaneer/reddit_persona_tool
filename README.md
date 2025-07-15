# Reddit Persona Generator

Generate a detailed psychological and behavioral profile for any public Reddit user using OpenAI GPT models and their Reddit activity.

---

## Features

- 🔍 Scrapes a Reddit user’s posts and comments using the **PRAW** library  
- 🧠 Sends the data to OpenAI’s GPT model to build a structured persona  
- 🗂 Outputs a clean **JSON file** with citations and personality traits  
- 🖨️ Generates a **styled PDF report** using Jinja2 and `pdfkit`  

---

## Dependencies

Install all Python packages:

```bash
pip install -r requirements.txt
```

### Python packages:

- `praw`
- `openai`
- `python-dotenv`
- `jinja2`
- `pdfkit`

### External dependency (for PDF generation)

You must install [`wkhtmltopdf`](https://wkhtmltopdf.org/downloads.html) manually.

After installation:

- Ensure it's added to your system **PATH** (select this during install)
- Or manually add the binary path:
  ```
  C:\Program Files\wkhtmltopdf\bin
  ```

Verify with:

```bash
wkhtmltopdf --version
```

---

## Setup

1. **Clone the repository**

```bash
git clone https://github.com/your-username/reddit-persona-generator.git
cd reddit-persona-generator
```

2. **Create a `.env` file** in the root directory:

```
OPENAI_API_KEY=your_openai_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=any_user_agent_description
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## How to Use

### 1. Generate JSON Persona

```bash
python persona_generator.py https://www.reddit.com/user/USERNAME/
```

This will:
- Extract the Reddit username
- Scrape up to 50 posts and comments
- Send the data to OpenAI
- Save a persona file in `data/USERNAME_persona.json`

---

### 2. Generate PDF Report (Optional)

Make sure `wkhtmltopdf` is installed and accessible via PATH.

```bash
python generate_pdf.py USERNAME
```

This will:
- Load the JSON file from `data/`
- Render a Jinja2 HTML template
- Output a PDF to `output/USERNAME_persona.pdf`

---

## Important Notes

- Make sure **`.env` is listed in your `.gitignore`**
- The GPT response must be valid JSON — no Markdown or extra formatting
- Use GPT-4 or GPT-3.5-turbo depending on your access level

---

## To Do

- Retry logic for OpenAI API failures  
- Scrape more than 50 items  
- Add charts or visuals to the PDF  
- Improve PDF design and color scheme  

---
