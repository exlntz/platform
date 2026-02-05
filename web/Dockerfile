# --- Этап 1: Общая база ---
FROM node:22-alpine as base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# --- Этап 2: РАЗРАБОТКА (Local) ---
FROM base as development
EXPOSE 5173
CMD ["npm", "run", "dev"]

# --- Этап 3: СБОРКА (Build) ---
FROM base as build-stage
# Передаем аргументы сборки, чтобы Vite видел их в vite.config.js
ARG VITE_IS_PROD=true
ARG VITE_IS_DOCKER=true
ENV VITE_IS_PROD=$VITE_IS_PROD
ENV VITE_IS_DOCKER=$VITE_IS_DOCKER

RUN npm run build

# --- Этап 4: ПРОДАКШЕН (Nginx) ---
FROM nginx:stable-alpine as production
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]