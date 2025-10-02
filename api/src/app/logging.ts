import * as winston from "winston";
import { Env } from "./env";

const { combine, timestamp, printf, colorize, json, uncolorize, errors } =
   winston.format;

const customFormat = printf(({ level, message, timestamp, ...meta }) => {
   const splat = meta[Symbol.for("splat") as any];
   const extra = Array.isArray(splat) ? splat[0] : undefined;

   let msg =
      typeof message === "object" ? JSON.stringify(message, null, 2) : message;
   if (extra && typeof extra === "object") {
      msg += `\n${JSON.stringify(extra, null, 2)}`;
   }

   return `[\n${timestamp}] \n ${level}: ${msg}`;
});

export const logger = winston.createLogger({
   level: "debug",
   format: combine(
      colorize(),
      timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
      errors({ stack: true }),
      customFormat
   ),
   transports: [
      ...(Env.debug ? [new winston.transports.Console()] : []),
      new winston.transports.File({
         filename: "logs/error.log",
         level: "error",
         format: winston.format.combine(
            uncolorize(),
            timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
            errors({ stack: true }),
            json()
         ),
      }),
   ],
   exitOnError: false,
});
