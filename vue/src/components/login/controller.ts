import { tokenName } from "@/config/appInfo.js";
import { toastStore } from "@/stores/services/toast-store";

import { delay } from "@/controller/tools";
import { reactive } from "vue";

import { routerStore } from "@/stores/services/router-store";
import { post } from "@/controller/others/RequestApiController";

export class Controller {
   router = routerStore().router;

   post = reactive({
      sukses: false,
      load: false,
      data: null,
      errors: null,
      message: null,
   });

   get toast() {
      return toastStore().toast;
   }
   get collection() {
      return "user";
   }

   async onSubmit(body: any): Promise<void> {
      if (this.post.load) return;

      this.reset();
      this.post.load = true;

      try {
         const { data, status, error, message } = await post(
            this.collection,
            body,
            false
         );

         this.post.sukses = status === 200 || status == 201;
         this.post.data = data;

         if (this.post.sukses) {
            const router = this.router;
            const data = this.post.data ?? null;
            var routeTo = null;

            routeTo = this.routeRedirect(data);

            if (routeTo) {
               localStorage.setItem(tokenName, data.token);
               router.push(routeTo);
               return;
            } else {
               this.post.sukses = false;
               this.post.data.errors = ["Tidak menemukan route"];
            }
         } else {
            this.post.message = message;
            this.post.errors = error;
         }
         await delay(250);
      } catch (_) {}
      this.post.load = false;
   }

   routeRedirect(data: any): any {
      var routeTo = null;
      if (data && data.role === "4dm1n") {
         routeTo = "/admin";
      } else if (data && data.role === "petugas") {
         routeTo = "/petugas";
      } 
      return routeTo;
   }

   reset(): void {
      this.post.load = false;
      this.post.sukses = false;
      this.post.data = null;
   }
}
