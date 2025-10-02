import { Hono } from "hono";
import * as Middleware from "@/middleware";
import { OwnerRoute } from "@/controllers/owner";
import { UserService } from "@/services/UserService";
import { UserResponse } from "@/response/UserResponse";

export const owner = new Hono();

const userServiceStore = UserService.owner.store;

owner.use("/*", async (c, next) => {
   return userServiceStore.run(() =>
      Middleware.AuthBearer(
         c,
         async () => {
            await userServiceStore.setup(c);
            return next();
         },
         1
      )
   );
});

owner.get("", (c) =>
   c.json({
      data: UserResponse.auth(userServiceStore.user),
   })
);

/* ---- barista ---- */
owner.get("/barista", OwnerRoute.BaristaCtrl.index);
owner.post("/barista", OwnerRoute.BaristaCtrl.store);
owner.patch("/barista/:id", OwnerRoute.BaristaCtrl.update);
owner.patch("/barista/reset-password/:id", OwnerRoute.BaristaCtrl.resetPassword);
owner.delete("/barista/:id", OwnerRoute.BaristaCtrl.destroy);

/* ---- kategori-menu ---- */
owner.get("/kategori-menu", OwnerRoute.KategoriMenuCtrl.index);
owner.post("/kategori-menu", OwnerRoute.KategoriMenuCtrl.store);
owner.patch("/kategori-menu/:id", OwnerRoute.KategoriMenuCtrl.update);
owner.delete("/kategori-menu/:id", OwnerRoute.KategoriMenuCtrl.destroy);

/* ---- menu ---- */
owner.get("/menu", OwnerRoute.MenuCtrl.index);
owner.post("/menu/:id", OwnerRoute.MenuCtrl.gambarMenu);
owner.post("/menu", OwnerRoute.MenuCtrl.store);
owner.patch("/menu/:id", OwnerRoute.MenuCtrl.update);
owner.delete("/menu/:id", OwnerRoute.MenuCtrl.destroy);

/* ---- order ---- */
owner.get("/order", OwnerRoute.OrderCtrl.index);
owner.delete("/order/:id", OwnerRoute.OrderCtrl.destroy);