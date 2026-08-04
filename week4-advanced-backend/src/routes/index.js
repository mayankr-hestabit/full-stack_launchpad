import { Router } from "express";
import { createUser, getUsers, getUserById, updateUser, deleteUser } from "../controllers/userController.js";
import productRoutes from "./product.routes.js";
import validate from "../middlewares/validate.js";
import { createUserSchema, updateUserSchema } from "../validations/user.validation.js";

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

// Create user
router.post("/users", validate(createUserSchema), createUser);

// Get all users
router.get("/users", getUsers);

// Get specific user by its id
router.get("/users/:id", getUserById);

// Update user
router.put("/users/:id",validate(updateUserSchema), updateUser);

// Delete user
router.delete("/users/:id", deleteUser);

// for products
router.use("/products", productRoutes);

export default router;