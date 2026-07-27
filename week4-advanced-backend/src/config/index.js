import dotenv from "dotenv";

// Load environment variables
dotenv.config({
  path: ".env.local",
});

const config = {
  PORT: process.env.PORT || 5000,
  MONGODB_URI: process.env.MONGODB_URI,
  NODE_ENV: process.env.NODE_ENV || "development",
};

export default config;