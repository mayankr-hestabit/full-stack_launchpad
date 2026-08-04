import crypto from "crypto";

const requestTracing = (req, res, next) => {
  const requestId = req.headers["x-request-id"] || crypto.randomUUID();

  req.requestId = requestId;

  res.setHeader("X-Request-ID", requestId);

  console.log(
    `[${requestId}] ${req.method} ${req.originalUrl}`
  );

  next();
};

export default requestTracing;