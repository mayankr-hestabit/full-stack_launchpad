import helmet from "helmet";
import cors from "cors";
import rateLimit from "express-rate-limit";

export const helmetMiddleware = helmet();

export const corsMiddleware = cors({
  origin: "*",
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
  credentials: false,
});

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    message: "Too many requests. Please try again later.",
  },
});