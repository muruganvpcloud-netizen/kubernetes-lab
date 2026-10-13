FROM python:3.12-alpine
WORKDIR /app
COPY app/server.py /app/server.py
RUN adduser -D -u 10001 appuser
USER appuser
ENV PORT=8080 APP_VERSION=v1 PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python","/app/server.py"]
