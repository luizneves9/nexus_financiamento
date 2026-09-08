FROM fin-base:1.0

WORKDIR /app
COPY . .

EXPOSE 8502
CMD ["streamlit", "run", "src/main.py", "--server.port=8502", "--server.address=0.0.0.0"]