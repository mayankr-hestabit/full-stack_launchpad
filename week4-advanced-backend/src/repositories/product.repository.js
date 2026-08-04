import Product from "../models/Product.js";

export const createProduct = async (productData) => {
  return await Product.create(productData);
};

export const getAllProducts = async (filter, sort, skip, limit) => {
  return await Product.find(filter).sort(sort).skip(skip).limit(limit);
};

export const getProductById = async (id) => {
  return await Product.findById(id);
};

export const updateProduct = async (id, productData) => {
  return await Product.findByIdAndUpdate(id, productData, {
    new: true,
    runValidators: true,
  });
};

export const deleteProduct = async (id) => {
  return await Product.findByIdAndUpdate(
    id,
    {
      isDeleted: true,
    },
    {
      new: true,
    }
  );
};