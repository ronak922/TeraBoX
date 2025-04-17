FROM hrishi2861/terabox:heroku

WORKDIR /app

COPY requirements.txt .

# Create a virtual environment
RUN python -m venv venv

# Install dependencies in the virtual environment
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
