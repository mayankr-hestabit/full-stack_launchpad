const express = require("express");
const app = express();
const PORT = 3000;

app.get("/", (req, res) => {
  res.send("Node app is running inside Docker container");
});

app.get("/api", (req, res) => {
  res.json({
    message: "API is working",
    environment: "Docker"
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});