# TDS Virtual TA (Render Deployment)

This project implements a RAG-based virtual TA for the IITM TDS course, combining course content and Discourse posts.

## Deployment

- Built with Flask and OpenAI API (via AIProxy)
- Hosted on render.com using `Dockerfile`

## Environment Variables

- `AIPROXY_TOKEN` — required (set via Render's Environment Variables UI)

## Endpoints

- POST `/api/` with:
  ```json
  {
    "question": "...",
    "image": "base64string (optional)"
  }


##Credits
- IIT Madras BS Data Science.
- Special thanks to Reshav Sharma, June 2025.

