import type { BlankEnv, HTTPResponseError } from "hono/types";
import type { Context } from "hono";
import { HTTPException } from "hono/http-exception";
import { ZodError } from "zod";
import { Env } from "@/app/env";
import { Prisma } from "@prisma/client";
import { DateTime } from "luxon";

function zod(err: any) {
   if (!err.success) {
      throw new ZodError(err.error.errors);
   }
}

function jsonCatch(err: null | undefined | any = null) {
   let msg;
   if (err == "SyntaxError: Unexpected end of JSON input") {
      msg = null;
   }
   throw new HTTPException(400, {
      message: msg ?? "Body tidak ditemukan",
   });
}

async function writeErrorLog(c: Context, err: any) {
    if (!Env.error_log) return;

    const now = DateTime.now().setZone("Asia/Jayapura").setLocale("id");
    const time = `[${now.toFormat("cccc, dd LLLL yyyy (HH:mm:ss)")}]`;
    const method = c.req.method;
    const url = c.req.url;
    const status = c.res.status ?? 500;
    const message = err?.message ?? String(err);
    const stack = Env.debug && err?.stack ? `\n${err.stack}` : "";

    const line = `${time} ${method} ${url} - ${status} :: ${message}${stack}`;
    const path = "logs/error.log";

    const exists = await Bun.file(path).exists();
    if (exists) {
        const prev = await Bun.file(path).text();
        await Bun.write(path, prev + line + "\n");
    } else {
        await Bun.write(path, line + "\n");
    }
}

async function router(err: Error | HTTPResponseError, c: Context<BlankEnv, any, {}>) {
   if (err instanceof HTTPException) {
      c.status(err.status);
      await writeErrorLog(c, err);
      return c.json({ errors: err.message });
   }

   if (err instanceof ZodError) {
      c.status(400);
      await writeErrorLog(c, err);
      return c.json({
         errors: err.issues.map((e) => ({
            path: e.path.join("."),
            message: e.message,
         })),
      });
   }

   if (err instanceof Prisma.PrismaClientKnownRequestError) {
      c.status(400);
      const message = err.meta?.["message"];
      await writeErrorLog(c, err);

      if (err.code === "P2025") {
         c.status(404);
         return c.json({ errors: message ?? "Data tidak ditemukan" });
      }

      if (err.code === "P2002") {
         return c.json({
            errors:
               message ??
               "Data yang anda masukan sudah terdaftar pada salah satu field",
         });
      }

      if (err.code === "P2003") {
         return c.json({
            errors: message ?? "Data relasi yang anda kirim tidak benar",
         });
      }

      return c.json({
         errors: Env.debug
            ? message ?? "Data tidak ditemukan"
            : "Data tidak ditemukan",
         code: err.code,
      });
   }

   c.status(500);
   await writeErrorLog(c, err);
   return c.json({
      errors: err.message || "Internal Server Error",
   });
}

export const handleAppError = {
   router,
   zod,
   jsonCatch,
};
