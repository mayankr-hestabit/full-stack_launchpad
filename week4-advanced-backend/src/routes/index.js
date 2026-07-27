import { Router } from "express";

const router = Router();

// Home Route
router.get("/", (req, res) => {
  res.status(200).json({
    success: true,
    message: "Welcome to Week 4 Advanced Backend 🚀",
    author: "Mayank Raj",
  });
});

// Health Check Route
router.get("/health", (req, res) => {
  res.status(200).json({
    success: true,
    status: "Server is healthy ✅",
  });
});

export default router;