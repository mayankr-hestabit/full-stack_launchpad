import { Worker } from "bullmq";

const emailWorker = new Worker(
  "email-queue",
  async (job) => {
    console.log(`Processing job ${job.id}`);
    console.log(`Attempt number: ${job.attemptsMade + 1}`);

    console.log("Email data:", job.data);

    // throw new Error("Email service is temporarily unavailable");
  },
  {
    connection: {
      host: "127.0.0.1",
      port: 6379,
    },
  }
);

emailWorker.on("completed", (job) => {
  console.log(`Job ${job.id} completed successfully`);
});

emailWorker.on("failed", (job, error) => {
  console.log(
    `Job ${job?.id} failed: ${error.message}`
  );
});