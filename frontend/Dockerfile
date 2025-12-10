# Stage 1: Build the React application
FROM node:20-alpine as build-stage

WORKDIR /app

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the source code
COPY frontend/ ./

# Build the application
# This command compiles the React code into static files in the 'dist' folder
RUN npm run build

# Stage 2: Serve the application using a minimal web server (like Nginx)
# Using a static server is best practice for production React apps
FROM nginx:alpine

# Copy the built files from the previous stage into the Nginx public folder
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy a custom Nginx configuration to handle React's routing (single-page app support)
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose the default Nginx port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]