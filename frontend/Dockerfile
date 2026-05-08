FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
COPY package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY public/ ./public/
COPY src/     ./src/
ARG REACT_APP_API_URL=http://localhost:8000
ARG REACT_APP_WS_URL=ws://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL
RUN npm run build
FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=builder /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]