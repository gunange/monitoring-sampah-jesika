import { delay } from "@/controller/tools";
import { reactive } from "vue";
import { TimeApp } from "@/controller/tools";
import { post } from "@/controller/others/RequestApiController";
import { toastStore } from "@/stores/services/toast-store";

export class Controller {
   get collection() {
      return `publics/registrasi`;
   }
   get time() {
      return new TimeApp();
   }
   get toast() {
      return toastStore().toast;
   }
}
export class Cruds extends Controller {
   modal = reactive({
      show: false,
      label: "Label",
      act: null,
      proses_form: false,
      uid: null,
   });

   async open(): Promise<void> {
      await delay(50);
      this.modal.show = true;
   }
   async close(): Promise<void> {
      await delay(50);
      await this.reset();
   }

   async reset(): Promise<void> {
      this.modal.act = null;
      this.modal.proses_form = false;
      this.modal.label = "Label";
      this.modal.show = false;
      this.modal.uid = null;

      delay(100);
   }
   setUid(uid) {
      this.modal.uid = uid;
   }

   /*
    * Fungsi daari crud yanng sebenarnnya adda dibawah ini
    */

   async add(body: any): Promise<{
      data: any;
      status: number;
      message: string;
      error: string;
   }> {
      const { data, status, message, error } = await post(
         this.collection,
         body,
         false
      );

      return { data, status, message, error };
   }
}
