import { PrismaClient, type Role, type User } from "@prisma/client";
import type { Context } from "hono";

import { getConnInfo } from "hono/bun";

const prismaClient = new PrismaClient();

export class Token {
   static async generate(user: User, context: Context) {
      const time = new Date().getTime();
      const random = crypto.randomUUID();
      const token =
         time.toString().slice(0, -1) + random.toString().replace(/\-/g, "");

      let ip;

      try {
         ip = getConnInfo(context).remote.address || "0.0.0.0";
      } catch (_) {
         ip = "0.0.0.0";
      }
      const userAgent = context.req.header("user-agent");

      await prismaClient.personalAksesToken.create({
         data: {
            user_id: user.id,
            name: user.username,
            ip_address: ip,
            user_agent: userAgent,
            token: token,
         },
      });

      return token;
   }

   static async verify(
      token: string,
      context: Context,
      role_id?: number
   ): Promise<boolean> {
      try {
         const tokenAkses = await prismaClient.personalAksesToken.findFirst({
            where: { token: token },
            include: {
               user: {
                  include: {
                     Role: true,
                  },
               },
            },
         });

         if (!tokenAkses || tokenAkses.token !== token.replace(/\+\|\+/g, "/"))
            return false;

         if (role_id && tokenAkses.user.role_id !== role_id) return false;

         context.set("user", tokenAkses.user);
         context.set("token", token);

         return true;
      } catch {
         return false;
      }
   }
   static async getUserByToken(
      token: string
   ): Promise<(User & { Role: Role }) | null> {
      try {
         const tokenAkses = await prismaClient.personalAksesToken.findFirst({
            where: { token: token },
            include: {
               user: {
                  include: {
                     Role: true,
                  },
               },
            },
         });

         if (!tokenAkses || tokenAkses.token !== token.replace(/\+\|\+/g, "/"))
            return null;

         return tokenAkses.user;
      } catch {
         return null;
      }
   }
}
