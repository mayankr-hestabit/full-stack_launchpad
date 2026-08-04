import * as userRepository from "../repositories/user.repository.js";
import logger from "../utils/logger.js";

export const createUser = async (userData, requestId) => {
  logger.info(
    { requestId },
    "User service: creating user"
  );

  return await userRepository.createUser(userData);
};

export const getUsers = async (requestId) => {
  logger.info(
    { requestId },
    "User service: getting users"
  );

  return await userRepository.getAllUsers();
};

export const getUserById = async (id, requestId) => {
  logger.info(
    {
      requestId,
      userId: id,
    },
    "User service: getting user by ID"
  );

  return await userRepository.getUserById(id);
};

export const updateUser = async (id, userData, requestId) => {
  logger.info(
    {
      requestId,
      userId: id,
    },
    "User service: updating user"
  );

  return await userRepository.updateUser(id, userData);
};

export const deleteUser = async (id, requestId) => {
  logger.info(
    {
      requestId,
      userId: id,
    },
    "User service: deleting user"
  );

  return await userRepository.deleteUser(id);
};