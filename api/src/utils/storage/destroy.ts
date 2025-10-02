import { PrismaClient } from "@prisma/client";
import { HTTPException } from "hono/http-exception";
const dbClient = new PrismaClient();

export async function destroy(uid: string): Promise<{
   uid: string;
   file_name: string;
   file_size: string | number;
   mime_type: string;
}> {
   const db = await dbClient.storage
      .findFirstOrThrow({
         where: {
            uid: uid,
         },
      })
      .catch((err) => {
         err.meta.message = "UID Storage tidak falid";
         throw err;
      });

   // Delete Old File
   try {
      const oldFile = `${db.path}/${db.name}`;

      await ((await Bun.file(oldFile)) as any).delete();
      await dbClient.storage.delete({
         where: {
            uid: uid,
         },
      });

      return {
         uid: uid,
         file_name: db.name,
         file_size: db.size,
         mime_type: db.mime_type,
      };
   } catch (_) {
      return {
         uid: "null",
         file_name: "null",
         file_size: "null",
         mime_type: "null",
      };
   }
}
