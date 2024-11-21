FROM python:3-alpine
# An argument needed to be passed
# docker-compose up --build --build-arg SECRET_KEY=your_actual_secret_key -t ku-polls .
# use this -> docker compose --env-file .env up --build
# run image in docker and add ports!
ARG SECRET_KEY=your_actual_secret_key
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

# Set needed settings
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=Asia/Bangkok
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}

# Test for secret key
RUN if [ -z "$SECRET_KEY" ]; then echo "No secret key specified in build-arg"; exit 1; fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Copy the entrypoint.sh script to the correct location
COPY entrypoint.sh /app/polls/entrypoint.sh

# Make the entrypoint.sh executable
RUN chmod +x /app/polls/entrypoint.sh

EXPOSE 8000

# Run application
CMD [ "/app/polls/entrypoint.sh" ]