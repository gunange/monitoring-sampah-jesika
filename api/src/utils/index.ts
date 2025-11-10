import type { Context, Next } from "hono";
import { z, type ZodType } from "zod";

import { convertTypes } from "./convert-type";
import { HeandleRequest } from "./heandle-request";
import { handleAppError } from "./heandle-app-error";
import { HTTPException } from "hono/http-exception";
import { Token } from "@/app/token";
import prismaClient from "@/app/database";
import { requestApi } from "./request-api";


export {
   prismaClient as dbClient,
   HTTPException,
   Token,
   z as zod,
   handleAppError,
   HeandleRequest,
   convertTypes,
   requestApi,
};

export type { Context, Next, ZodType };
