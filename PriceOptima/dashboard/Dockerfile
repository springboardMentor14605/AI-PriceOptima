# Use the official Node image for a lightweight React setup
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy the package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the entire frontend project
COPY . .

# Expose the Vite default port
EXPOSE 5173

# Start the Vite server, enabling network access (--host)
CMD ["npm", "run", "dev", "--", "--host"]
