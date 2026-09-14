# TODO: a three-stage build. See README.md.
FROM node:latest
WORKDIR /app
COPY . .
RUN npm install && npm run build
CMD npm start
