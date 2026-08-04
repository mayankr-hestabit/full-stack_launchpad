import emailQueue from "./email.job.js";

await emailQueue.obliterate({ force: true });

console.log("Email queue cleared");

await emailQueue.close();