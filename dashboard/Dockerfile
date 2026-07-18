FROM nginx:1.27-alpine

RUN apk add --no-cache openssl     && mkdir -p /etc/nginx/ssl     && openssl req -x509 -nodes -days 3650 -newkey rsa:2048       -keyout /etc/nginx/ssl/selfsigned.key       -out /etc/nginx/ssl/selfsigned.crt       -subj "/CN=easy-auditoria.local"

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

EXPOSE 80 443
