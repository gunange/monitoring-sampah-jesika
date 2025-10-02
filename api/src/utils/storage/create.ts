import type { Context } from "hono";
import { STORAGE_VALIDATOR, type SchemaOptions } from "./storage-validator";
import { extname } from "path";
import { Env } from "@/app/env";
import { PrismaClient } from "@prisma/client";

const dbClient = new PrismaClient();

export async function create(
   c: Context,
   label: string,
   path: string,
   options?: SchemaOptions
): Promise<{
   uid: string;
   file_name: string;
   mime_type: string;
   file_size: string | number;
}> {
   const { file } = await STORAGE_VALIDATOR.schema(c, options);

   // Akses informasi file
   const fileType = file.type;
   const fileSize = file.size;
   const uid = Bun.randomUUIDv7();
   const fileName = `${label}${extname(file.name)}`;

   const fileBuffer = await file.arrayBuffer();

   const cleanedPath =
      path.endsWith("/") && path.lastIndexOf("/") > 0
         ? path.slice(0, path.lastIndexOf("/"))
         : path;

   const dirPath = `${Env.storage_path}/${cleanedPath}`;
   await Bun.write(`${dirPath}/${fileName}`, new Uint8Array(fileBuffer), {
      createPath: true,
   });

   await dbClient.storage.create({
      data: {
         uid: uid,
         path: dirPath,
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
