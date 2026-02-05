# --- Этап 1: Общая база ---
FROM node:18-alpine as base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# --- Этап 2: РАЗРАБОТКА (Local) ---
# Этот этап будет запускаться у тебя на компе
FROM base as development
EXPOSE 5173
CMD ["npm", "run", "dev"]

# --- Этап 3: СБОРКА (Build) ---
FROM base as build-stage
RUN npm run build

# --- Этап 4: ПРОДАКШЕН (Server) ---
# Этот этап запустится на сервере: легкий Nginx со статикой
FROM nginx:stable-alpine as production
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Копируем конфиг Nginx (создадим его в след. шаге)
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]