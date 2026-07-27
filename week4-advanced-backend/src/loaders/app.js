import express from "express";
import routes from "../routes/index.js";

const createApp = () => {
  const app = express();

  // Middleware
  app.use(express.json());

  // Routes
  app.use("/", routes);

  return app;
};

export default createApp;