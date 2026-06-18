# Build Stage
FROM node:21-slim AS build
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps --loglevel=verbose --no-audit --timeout=600000

COPY . .

# Build argument for API server location
ARG BACKEND_API_URL
ENV BACKEND_API_URL=$BACKEND_API_URL

# Compile static assets in production mode
RUN npx webpack --mode production

# Production Stage
FROM nginx:alpine
# Copy Webpack bundle, logo, and the HTML template to the web root
COPY --from=build /app/build/ /usr/share/nginx/html/
COPY --from=build /app/index.html /usr/share/nginx/html/
COPY --from=build /app/logo.png /usr/share/nginx/html/

# Expose port 7860 as expected by Hugging Face Spaces
EXPOSE 7860

# Configure Nginx to listen on port 7860
RUN sed -i 's/listen\( \)*80;/listen 7860;/g' /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]