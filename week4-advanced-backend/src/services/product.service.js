import * as productRepository from "../repositories/product.repository.js";

export const createProduct = async (productData) => {
  return await productRepository.createProduct(productData);
};

export const getProducts = async (queryParams) => {
    const filter = {};
    filter.isDeleted = false;
    if (queryParams.search) {
        filter.$or = [
            {name: {
              $regex: queryParams.search,
                $options: "i",
              },
            },
            {category: {
              $regex: queryParams.search,
              $options: "i",
              },
            },
        ];
    }
    if (queryParams.category) {
      filter.category = queryParams.category;
    }

    if (queryParams.minPrice) {
      filter.price = {
        ...filter.price,
        $gte: Number(queryParams.minPrice),
      };
    }

    if (queryParams.maxPrice) {
      filter.price = {
        ...filter.price,
        $lte: Number(queryParams.maxPrice),
      };
    }
    let sort = {};
    if (queryParams.sort) {
      const [field, order] = queryParams.sort.split(":");
      sort[field] = order === "desc" ? -1 : 1;
    }

    const page = Number(queryParams.page) || 1;
    const limit = Number(queryParams.limit) || 10;
    const skip = (page - 1) * limit;

    return await productRepository.getAllProducts(filter, sort, skip, limit);
};

export const getProductById = async (id) => {
  return await productRepository.getProductById(id);
};

export const updateProduct = async (id, updateData) => {
  return await productRepository.updateProduct(id, updateData);
};

export const deleteProduct = async (id) => {
  return await productRepository.deleteProduct(id);
};