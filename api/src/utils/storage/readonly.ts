import { PrismaClient } from "@prisma/client";
import { HTTPException } from "hono/http-exception";
const dbClient = new PrismaClient();

export async function readonly(uid: string): Promise<Response> {
   const db = await dbClient.storage
      .findFirstOrThrow({
         where: {
            uid: uid,
         },
      })
      .catch((err) => {
         err.meta.message = "File Not Found";
         throw err;
      });
   try {
      const pathFile = `${db.path}/${db.name}`;

      const fileBuffer = await Bun.file(pathFile).arrayBuffer();
      const mimeType = db.mime_type || "application/octet-stream";

      return new Response(fileBuffer, {
         headers: {
            "Content-Type": mimeType,
         },
      });
   } catch (_) {
      throw new HTTPException(400, {
         message: "File Not Found",
      });
   }
}
