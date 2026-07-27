import mongoose from "mongoose";
import config from "../config/index.js";

const connectDB = async () => {
  try {
    await mongoose.connect(config.MONGODB_URI);

    console.log("Database Connected");
  } catch (error) {
    console.error("Database Connection Failed");
    console.log(error)

    process.exit(1);
  }
};

export default connectDB;