import * as productService from "../services/product.service.js";
import logger from "../utils/logger.js";

export const createProduct = async (req, res, next) => {
  try {
    logger.info(
      { requestId: req.requestId },
      "Creating product"
    );

    const product = await productService.createProduct(req.body, req.requestId);

    logger.info(
      { requestId: req.requestId },
      "Product created successfully"
    );

    res.status(201).json({
      success: true,
      data: product,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        error: error.message,
      },
      "Failed to create product"
    );

    next(error);
  }
};

export const getProducts = async (req, res, next) => {
  try {
    logger.info(
      { requestId: req.requestId },
      "Getting products"
    );

    const products = await productService.getProducts(req.query, req.requestId);

    logger.info(
      {
        requestId: req.requestId,
        count: products.length,
      },
      "Products fetched successfully"
    );

    res.status(200).json({
      success: true,
      count: products.length,
      data: products,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        error: error.message,
      },
      "Failed to fetch products"
    );

    next(error);
  }
};

export const getProductById = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Getting product by ID"
    );

    const product = await productService.getProductById(req.params.id, req.requestId);

    if (!product) {
      logger.warn(
        {
          requestId: req.requestId,
          productId: req.params.id,
        },
        "Product not found"
      );

      return res.status(404).json({
        success: false,
        message: "Product not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Product fetched successfully"
    );

    res.status(200).json({
      success: true,
      data: product,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        productId: req.params.id,
        error: error.message,
      },
      "Failed to fetch product"
    );

    next(error);
  }
};

export const updateProduct = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Updating product"
    );

    const product = await productService.updateProduct(
      req.params.id,
      req.body, 
      req.requestId
    );

    if (!product) {
      logger.warn(
        {
          requestId: req.requestId,
          productId: req.params.id,
        },
        "Product not found for update"
      );

      return res.status(404).json({
        success: false,
        message: "Product not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Product updated successfully"
    );

    res.status(200).json({
      success: true,
      data: product,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        productId: req.params.id,
        error: error.message,
      },
      "Failed to update product"
    );

    next(error);
  }
};

export const deleteProduct = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Deleting product"
    );

    const product = await productService.deleteProduct(req.params.id, req.requestId);

    if (!product) {
      logger.warn(
        {
          requestId: req.requestId,
          productId: req.params.id,
        },
        "Product not found for deletion"
      );

      return res.status(404).json({
        success: false,
        message: "Product not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        productId: req.params.id,
      },
      "Product deleted successfully"
    );

    res.status(200).json({
      success: true,
      message: "Product deleted successfully",
      data: product,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        productId: req.params.id,
        error: error.message,
      },
      "Failed to delete product"
    );

    next(error);
  }
};