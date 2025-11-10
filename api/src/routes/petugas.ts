import { Hono } from "hono";
import * as Middleware from "@/middleware";
import { PetugasRoute } from "@/controllers/petugas";
import { UserService } from "@/services/UserService";
import { PetugasResponse } from "@/response/PetugasResponse";
import { admin } from "./admin";

export const petugas = new Hono();

const userServiceStore = UserService.petugas.store;

petugas.use("/*", async (c, next) => {
   return userServiceStore.run(() =>
      Middleware.AuthBearer(
         c,
         async () => {
            await userServiceStore.setup(c);
            return next();
         },
         2
      )
   );
});

petugas.get("", (c) =>
   c.json({
      data: PetugasResponse.profil(userServiceStore.profil),
   })
);


/* ---- dataset ---- */
petugas.get("/dataset", PetugasRoute.DatasetCtrl.index);
petugas.post("/dataset", PetugasRoute.DatasetCtrl.store);
petugas.delete("/dataset/:id", PetugasRoute.DatasetCtrl.destroy);
