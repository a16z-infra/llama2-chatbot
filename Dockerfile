FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD streamlit run --server.port 8080 --server.address 0.0.0.0 llama2_chatbot.py
