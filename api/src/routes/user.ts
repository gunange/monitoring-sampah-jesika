import { Hono } from "hono";
import { UserController } from "@/controllers/user";
import * as Middleware from "@/middleware";

export const user = new Hono();

user.post("/", UserController.login);

user.use("/*", Middleware.AuthBearer);
user.get("", UserController.profil);
user.delete("", UserController.logout);
user.post("/ganti-password", UserController.resetPassword);