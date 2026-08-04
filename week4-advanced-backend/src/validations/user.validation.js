import { z } from "zod";

/* ---------- Create User ---------- */
export const createUserSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Name is required")
    .max(50, "Name cannot exceed 50 characters"),

  email: z
    .string()
    .trim()
    .toLowerCase()
    .email("Invalid email address"),

  password: z
    .string()
    .min(8, "Password must be at least 8 characters"),

  age: z
    .number()
    .min(18, "Age must be at least 18")
    .optional(),

  isActive: z
    .boolean()
    .optional(),
});

/* ---------- Update User ---------- */
export const updateUserSchema = createUserSchema.partial();