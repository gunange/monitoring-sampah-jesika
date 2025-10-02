import { z, type ZodType } from "zod";
import { Env } from "@/app/env";
import type { Context } from "hono";
import { HeandleRequest } from "../heandle-request";

export interface SchemaOptions {
   max_file_size?: number;
   allow_file_type?: string[];
}

const MAX_FILE_SIZE: number = Env.storage_max_size;
const ACCEPTED_TYPES: string[] = Env.storage_allow_file_type;

async function schema(
   c: Context,
   options: SchemaOptions = {}
): Promise<{
   file: File;
}> {
   const { max_file_size = MAX_FILE_SIZE, allow_file_type = ACCEPTED_TYPES } =
      options;

   const validate: ZodType = z.object({
      file: z
         .instanceof(File)
         .refine(
            (file) => file.size <= max_file_size,
            `Max file size is ${Math.round(max_file_size / 1024 / 1024)}MB.`
         )
         .refine(
            (file) => {
               if (Env.debug_storage) {
                  console.log("File received:", file);
                  console.log("Type of file:", typeof file);
               }
               return allow_file_type.includes(file?.type || "");
            },
            {
               message: `Only ${allow_file_type.join(
                  ", "
               )} formats are supported.`,
            }
         ),
   });

   const body = await HeandleRequest.parse(c);
   const data = await validate.parseAsync(body);

   return {
      file: data.file,
   };
}

export const STORAGE_VALIDATOR = {
   schema,
};
