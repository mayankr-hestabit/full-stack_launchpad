import * as userService from "../services/user.service.js";
import logger from "../utils/logger.js";

export const createUser = async (req, res, next) => {
  try {
    logger.info(
      { requestId: req.requestId },
      "Creating user"
    );

    const user = await userService.createUser(req.body, req.requestId);

    logger.info(
      { requestId: req.requestId },
      "User created successfully"
    );

    res.status(201).json({
      success: true,
      data: user,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        error: error.message,
      },
      "Failed to create user"
    );

    next(error);
  }
};

export const getUsers = async (req, res, next) => {
  try {
    logger.info(
      { requestId: req.requestId },
      "Getting users"
    );

    const users = await userService.getUsers(req.requestId);

    logger.info(
      {
        requestId: req.requestId,
        count: users.length,
      },
      "Users fetched successfully"
    );

    res.status(200).json({
      success: true,
      count: users.length,
      data: users,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        error: error.message,
      },
      "Failed to fetch users"
    );

    next(error);
  }
};

export const getUserById = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "Getting user by ID"
    );

    const user = await userService.getUserById(req.params.id, req.requestId);

    if (!user) {
      logger.warn(
        {
          requestId: req.requestId,
          userId: req.params.id,
        },
        "User not found"
      );

      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "User fetched successfully"
    );

    res.status(200).json({
      success: true,
      data: user,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        userId: req.params.id,
        error: error.message,
      },
      "Failed to fetch user"
    );

    next(error);
  }
};

export const updateUser = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "Updating user"
    );

    const user = await userService.updateUser(
      req.params.id,
      req.body, 
      req.requestId
    );

    if (!user) {
      logger.warn(
        {
          requestId: req.requestId,
          userId: req.params.id,
        },
        "User not found for update"
      );

      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "User updated successfully"
    );

    res.status(200).json({
      success: true,
      data: user,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        userId: req.params.id,
        error: error.message,
      },
      "Failed to update user"
    );

    next(error);
  }
};

export const deleteUser = async (req, res, next) => {
  try {
    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "Deleting user"
    );

    const user = await userService.deleteUser(req.params.id, req.requestId);

    if (!user) {
      logger.warn(
        {
          requestId: req.requestId,
          userId: req.params.id,
        },
        "User not found for deletion"
      );

      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    logger.info(
      {
        requestId: req.requestId,
        userId: req.params.id,
      },
      "User deleted successfully"
    );

    res.status(200).json({
      success: true,
      message: "User deleted successfully",
      data: user,
    });
  } catch (error) {
    logger.error(
      {
        requestId: req.requestId,
        userId: req.params.id,
        error: error.message,
      },
      "Failed to delete user"
    );

    next(error);
  }
};