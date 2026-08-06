import { z } from "zod";

/* ---------- Create Product ---------- */
export const createProductSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "Product name is required")
    .max(100, "Product name cannot exceed 100 characters"),

  description: z
    .string()
    .trim()
    .max(500, "Description cannot exceed 500 characters")
    .optional(),

  price: z
    .number()
    .min(0, "Price cannot be negative"),

  stock: z
    .number()
    .min(0, "Stock cannot be negative")
    .optional(),

  category: z
    .string()
    .trim()
    .min(1, "Category is required"),

  isAvailable: z
    .boolean()
    .optional(),

  isDeleted: z
    .boolean()
    .optional(),
});

/* ---------- Update Product ---------- */
export const updateProductSchema = createProductSchema.partial();