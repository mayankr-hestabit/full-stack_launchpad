const express = require("express");
const mongoose = require("mongoose");

const app = express();

const PORT = 3001;
const MONGO_URI =
  process.env.MONGO_URI || "mongodb://localhost:27017/day2db";

app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    message: "Node server is running",
  });
});

app.get("/api/health", async (req, res) => {
  const mongoState = mongoose.connection.readyState;

  res.json({
    server: "running",
    mongodb: mongoState === 1 ? "connected" : "not connected",
  });
});

async function startServer() {
  try {
    await mongoose.connect(MONGO_URI);

    console.log("MongoDB connected");

    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (error) {
    console.error("MongoDB connection failed:", error.message);
    process.exit(1);
  }
}

startServer();