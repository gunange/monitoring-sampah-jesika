import { routerStore } from "@/stores/services/router-store";
import { AuthController } from "@/controller/controllers/AuthController";
import { path_route } from "./data-env";
const route = routerStore();

const menu = [
  {
    label: "Surat Masuk",
    icon: "pi pi-inbox",
    route: `/${path_route}/surat-masuk`,
  },
  {
    label: "Surat Keluar",
    icon: "pi pi-send",
    route: `/${path_route}/surat-keluar`,
  },
  {
    label: "Surat Disposisi",
    icon: "pi pi-share-alt",
    route: `/${path_route}/surat-disposisi`,
  },
  {
    label: "Belum Didisposisi",
    icon: "pi pi-clock",
    route: `/${path_route}/belum-disposisi`,
  },

  // Pengaduan menu removed
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
