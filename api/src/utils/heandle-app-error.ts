import type { BlankEnv, HTTPResponseError } from "hono/types";
import type { Context } from "hono";
import { HTTPException } from "hono/http-exception";
import { ZodError } from "zod";
import { Env } from "@/app/env";
import { Prisma } from "@prisma/client";

const debug = Env.debug;

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

function router(err: Error | HTTPResponseError, c: Context<BlankEnv, any, {}>) {
   if (err instanceof HTTPException) {
      c.status(err.status);
      return c.json({ errors: err.message });
   }

   if (err instanceof ZodError) {
      c.status(400);
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
         errors: debug
            ? message ?? "Data tidak ditemukan"
            : "Data tidak ditemukan",
         code: err.code,
      });
   }

   c.status(500);
   return c.json({
      errors: err.message || "Internal Server Error",
   });
}

export const handleAppError = {
   router,
   zod,
   jsonCatch,
};
