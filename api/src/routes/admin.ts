import { Hono } from "hono";
import * as Middleware from "@/middleware";
import { OwnerRoute } from "@/controllers/admin";
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
owner.get("/petugas", OwnerRoute.PetugasCtrl.index);
owner.post("/petugas", OwnerRoute.PetugasCtrl.store);
owner.patch("/petugas/:id", OwnerRoute.PetugasCtrl.update);
owner.patch("/petugas/reset-password/:id", OwnerRoute.PetugasCtrl.resetPassword);
owner.delete("/petugas/:id", OwnerRoute.PetugasCtrl.destroy);
