import express from "express";
import * as productController from "../controllers/product.controller.js";
import validate from "../middlewares/validate.js";

import { createProductSchema, updateProductSchema } from "../validations/product.validation.js";

const router = express.Router();

router.post("/", validate(createProductSchema), productController.createProduct);

router.get("/", productController.getProducts);

router.get("/:id", productController.getProductById);

router.patch("/:id", validate(updateProductSchema), productController.updateProduct);

router.delete("/:id", productController.deleteProduct);

export default router;