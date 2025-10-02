import { login } from "./login";
import { create } from "./create";
import { destroy } from "./destroy";
import { profil } from "./profil";
import { logout } from "./logout";
import { resetPassword } from "./reset-password";

export const UsersRepo = {
   create,
   destroy,
   login,
   profil,
   logout,
   resetPassword
};
