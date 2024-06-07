FROM node:21-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps --loglevel=error --no-audit
COPY . .
EXPOSE 8080
CMD ["npm", "start"]
