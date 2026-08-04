import { addEmailJob } from "./email.producer.js";

const job = await addEmailJob({
  to: "mayank@example.com",
  subject: "Test Email",
  message: "This is my first BullMQ job!",
});

console.log("Created job:", job.id);

process.exit(0);