# TDS-Project-1
This is one of the project in my course called Tools for Data Science in IITM BS Data Science.This project is about LLM based Automation Agent

# Build
docker build -t yourdockerhub/llm-agent .

# Run
podman run --rm -e AIPROXY_TOKEN=$AIPROXY_TOKEN -p 8000:8000 yourdockerhub/llm-agent
