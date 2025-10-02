import chalk from "chalk";
import type { Context, Next } from "hono";
import { Env } from "../app/env";
import { DateTime } from "luxon";

export const LogClientAcsses = async (c: Context, next: Next) => {
   const start = Date.now();
   await next();

   if(!Env.access_log) return;

   const duration = Date.now() - start;
   const now = DateTime.now().setZone("Asia/Jayapura").setLocale("id");

   const time = chalk.cyan(`[${now.toFormat("cccc, dd LLLL yyyy (HH:mm:ss)")}]`);

   let methodColor = chalk.white;
   switch (c.req.method) {
      case "GET":
         methodColor = chalk.blueBright;
         break;
      case "POST":
         methodColor = chalk.greenBright;
         break;
      case "PUT":
         methodColor = chalk.magentaBright;
         break;
      case "PATCH":
         methodColor = chalk.yellow;
         break;
      case "DELETE":
         methodColor = chalk.redBright;
         break;
      case "ALL":
         methodColor = chalk.gray;
         break;
   }

   const method = methodColor(c.req.method);
   const url = c.req.url;
   const status = c.res.status;
   const durationStr = `${duration}ms`;

   const urlColored = chalk.hex("#FFD700")(url);
   const statusDuration = chalk.hex("#ff69b4")(`- ${status} (${durationStr})`);
   const logLine = `${time} ${method} ${urlColored} ${statusDuration}`;
   console.log(logLine);
   const path = "logs/access.log";
   if(!Env.access_log) return;
   const exists = await Bun.file(path).exists();

   if (exists) {
      const prev = await Bun.file(path).text();
      await Bun.write(path, prev + logLine + "\n");
   } else {
      await Bun.write(path, logLine + "\n");
   }
};
