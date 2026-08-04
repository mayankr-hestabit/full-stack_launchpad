import pino from "pino";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const logFile = path.join(__dirname, "../logs/app.log");

const logger = pino(
  {
    level: "info",
  },
  pino.destination({
    dest: logFile,
    sync: true,
  })
);

export default logger;