FROM gcc:latest

WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 runner

USER runner

CMD ["sleep", "infinity"]
