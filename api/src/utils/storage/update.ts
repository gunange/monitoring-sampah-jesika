import type { Context } from "hono";
import { STORAGE_VALIDATOR, type SchemaOptions } from "./storage-validator";
import { basename, extname } from "path";
import { PrismaClient } from "@prisma/client";

const dbClient = new PrismaClient();

export async function update(
   c: Context,
   uid: string,
   options?: SchemaOptions
): Promise<{
   uid: string ;
   file_name: string;
   mime_type: string;
   file_size: string | number;
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
   const { file } = await STORAGE_VALIDATOR.schema(c, options);

   // Akses informasi file
   const fileType = file.type;
   const fileSize = file.size;

   const newExtname = extname(file.name);
   const oldBasename = basename(db.name, extname(db.name));
   const fileName = `${oldBasename}${newExtname}`;

   const oldFile = `${db.path}/${db.name}`;

   // Delete Old File
   if (db.mime_type !== fileType)
      await ((await Bun.file(oldFile)) as any).delete();

   const filePath = `${db.path}/${fileName}`;
   await Bun.write(filePath, new Uint8Array(await file.arrayBuffer()), {
      createPath: true,
   });

   await dbClient.storage.update({
      where: {
         uid: uid,
      },
      data: {
         name: fileName,
         mime_type: fileType,
         size: String(fileSize),
      },
   });

   return {
      uid: uid,
      file_name: fileName,
      mime_type: fileType,
      file_size: fileSize,
   };
}
