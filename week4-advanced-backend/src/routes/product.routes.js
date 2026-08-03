import express from "express";
import * as productController from "../controllers/product.controller.js";

const router = express.Router();

router.post("/", productController.createProduct);

router.get("/", productController.getProducts);

router.get("/:id", productController.getProductById);

router.patch("/:id", productController.updateProduct);

router.delete("/:id", productController.deleteProduct);

export default router;