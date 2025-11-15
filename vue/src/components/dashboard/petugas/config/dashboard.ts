import { routerStore } from "@/stores/services/router-store";
import { AuthController } from "@/controller/controllers/AuthController";
import { path_route } from "./data-env";
const route = routerStore();

const menu = [
  {
    label: "Config",
    icon: "pi pi-cog",
    route: `/${path_route}/home`,
  },
  {
    label: "Dataset",
    icon: "pi pi-chart-line",
    route: `/${path_route}/dataset`,
  },
  
  {
    label: "Save Logs",
    icon: "pi pi-folder-open",
    route: `/${path_route}/save-logs`,
  },
  {
    label: "Traffic",
    icon: "pi pi-upload",
    route: `/${path_route}/traffic`,
  },
  {
    label: "Monitoring",
    icon: "pi pi-camera",
    route: `/${path_route}/monitoring`,
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
