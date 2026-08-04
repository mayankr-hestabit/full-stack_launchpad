import emailQueue from "./email.job.js";

export const addEmailJob = async (emailData) => {
  const job = await emailQueue.add("send-email", emailData);

  console.log(`Email job added: ${job.id}`);

  return job;
};