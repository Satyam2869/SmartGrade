# SmartGrade

Lightweight, offline, CSV-backed presentation grading app.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

This opens the app in your browser (usually at `http://localhost:8501`).

## Usage

1. **Live Grading Deck tab** — enter a Group Identifier and group size (1–5),
   then score each student on Slide Quality, Delivery & Body Language, and
   Q&A Handling (0–10 each). Totals update live as you move the sliders.
   Click **Lock & Save Group Marks** to write the group to
   `presentation_grades.csv`. Re-saving a SAP ID that already exists
   overwrites that student's record instead of duplicating it.

2. **Administrative Exporter tab** — view the full gradebook, filter by
   group, and download a portal-ready CSV with one click.

3. **Reports tab** — email results directly to students. Each student's
   email is fetched automatically from their linked SAP ID (see below) —
   nothing to type. Send an individual CSV/PDF, or use **Send Results to
   Entire Group** to email everyone in a group at once.

## Email setup (required for the Reports tab)

1. Open `config.py`.
2. Set `SENDER_EMAIL` to the address you'll send from.
3. Set `SENDER_PASSWORD` to an **App Password** (not your normal login
   password). For Gmail: Google Account → Security → 2-Step Verification →
   App passwords → generate one for "Mail", and paste the 16-character
   code in.

## How student emails get linked

- The first time you grade a student, enter their **Email** alongside
  their Name and SAP ID in the Live Grading Deck.
- That email is saved and permanently linked to their SAP ID.
- The next time you re-grade the same SAP ID, you can leave the Email
  field blank — the previously saved email is kept automatically. Type a
  new email only if you want to change it.
- Students log in on the **Student Login** tab using their **SAP ID +
  Email** (no separate password) — so the email on file also doubles as
  their login credential.

## Data file

All grades (including each student's linked email) are stored in
`presentation_grades.csv` in the same folder as `app.py`. Delete this
file to reset the gradebook. No database setup is required.
