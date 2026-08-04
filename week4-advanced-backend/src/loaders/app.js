import express from "express";
import routes from "../routes/index.js";
import errorHandler from "../middlewares/error.middleware.js";
import {
  helmetMiddleware,
  corsMiddleware,
  rateLimiter,
} from "../middlewares/security.js";
import requestTracing from "../utils/tracing.js";


const createApp = () => {
  const app = express();

  // Security middleware
  app.use(helmetMiddleware);
  app.use(corsMiddleware);
  app.use(rateLimiter);

  // Middleware
  app.use(express.json({ limit: "10kb" }));
  app.use(requestTracing);

  // Routes
  app.use("/", routes);
  app.use("/api", routes);

  // Middleware
  app.use(errorHandler);

  return app;
};

export default createApp;