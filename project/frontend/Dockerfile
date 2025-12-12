FROM node:20
WORKDIR /app

# Copy package manifests first and install inside the image
COPY package*.json ./

# Install all dependencies (including devDependencies) inside the image
RUN npm ci

# Copy the rest of the app (host node_modules is excluded via .dockerignore)
COPY . .

EXPOSE 5173
ENV VITE_API_URL=http://backend:8000

CMD ["npm", "run", "dev", "--", "--host"]
