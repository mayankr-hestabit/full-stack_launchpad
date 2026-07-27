import config from "./src/config/index.js";
import createApp from "./src/loaders/app.js";
import connectDB from "./src/loaders/db.js";

const startServer = async () => {
  try {
    const app = createApp();

    await connectDB();

    app.listen(config.PORT, () => {
      console.log(`Server running on port ${config.PORT}`);
    });
  } catch (error) {
    console.error("Server Startup Failed", error);
    process.exit(1);
  }
};

startServer();