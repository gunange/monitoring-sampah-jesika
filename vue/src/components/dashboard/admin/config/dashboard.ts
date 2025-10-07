import { routerStore } from "@/stores/services/router-store";
import { AuthController } from "@/controller/controllers/AuthController";
import { path_route } from "./data-env";
const route = routerStore();

const menu = [
   {
      label: "Camat",
      icon: "pi pi-home",
      route: `/${path_route}/camat`,
   },
   {
      label: "Staf",
      icon: "pi pi-users",
      route: `/${path_route}/staf`,
   },
  
];

const profilMenu = [
   {
      label: "Logout",
      icon: "pi pi-power-off text-red-500",
      command: () => {
         const auth = new AuthController();
         auth.signOut(() => {
            route.router.replace("/login");
         });
      },
   },
];

export const sidebar = {
   menu: menu,
};

export const navbar = {
   profilMenu: profilMenu,
};
