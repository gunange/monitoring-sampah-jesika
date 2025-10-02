import { PrismaClient } from "@prisma/client";
import { logger } from "./logging";
import { Env } from "./env";

const prismaClient = new PrismaClient({
   log: [
      {
         emit: "event",
         level: "query",
      },
      {
         emit: "event",
         level: "error",
      },
      {
         emit: "event",
         level: "info",
      },
      {
         emit: "event",
         level: "warn",
      },
   ],
});

prismaClient.$on("query", (e) => {
   if (Env.debug_sql) logger.info(e);
});

prismaClient.$on("error", (e) => {
   logger.error(e);
});

prismaClient.$on("info", (e) => {
   if (Env.debug_sql) logger.info(e);
});

prismaClient.$on("warn", (e) => {
   if (Env.debug_sql) logger.warn(e);
});

export default prismaClient;
