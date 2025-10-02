// import { Env } from "@/app/env";
import { Hono } from "hono";
import { cors } from "hono/cors";

// Optional: import routes dan middleware
import { Route } from "@/routes";
import { LogClientAcsses } from "@/middleware";
import { handleAppError } from "@/utils";

// Inisialisasi Hono App
const app = new Hono().basePath("/api");

// Middleware global
app.use(cors());
app.use("*", LogClientAcsses);

// Routing
app.route("/pelanggan", Route.pelanggan);
app.route("/publics", Route.publics);
app.route("/user", Route.user);
app.route("/owner", Route.owner);
app.route("/barista", Route.barista);

// Handler 404
app.notFound((c) =>
   c.json(
      {
         message: "Not Found",
         errors: "Resource Not Found",
      },
      404
   )
);

// Handler error global
app.onError(handleAppError.router);

export default app;
