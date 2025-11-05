import { Hono } from "hono";
import * as Middleware from "@/middleware";
import { AdminRoute } from "@/controllers/admin";
import { UserService } from "@/services/UserService";
import { UserResponse } from "@/response/UserResponse";

export const admin = new Hono();

const userServiceStore = UserService.admin.store;

admin.use("/*", async (c, next) => {
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

admin.get("", (c) =>
   c.json({
      data: UserResponse.auth(userServiceStore.user),
   })
);

/* ---- petugas ---- */
admin.get("/petugas", AdminRoute.PetugasCtrl.index);
admin.post("/petugas", AdminRoute.PetugasCtrl.store);
admin.patch("/petugas/:id", AdminRoute.PetugasCtrl.update);
admin.patch("/petugas/reset-password/:id", AdminRoute.PetugasCtrl.resetPassword);
admin.delete("/petugas/:id", AdminRoute.PetugasCtrl.destroy);
