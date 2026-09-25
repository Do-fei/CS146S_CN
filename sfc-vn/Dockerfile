FROM python:3.12-slim AS build

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pillow \
    && python3 tools/export_web.py

FROM nginx:alpine

COPY deploy/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/player /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
