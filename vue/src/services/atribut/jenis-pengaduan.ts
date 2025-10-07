import { get } from "@/controller/others/RequestApiController";
import { reactive } from "vue";

class AtributOnServer {
   data = reactive({ load: false, run: false, data: [] });

   get collection() {
      return "publics";
   }

   get items() {
      return (
         this.data.data ?? []
      );
   }

   async init(): Promise<void> {
      if (this.data.run) return;
      this.data.run = true;
      this.data.load = true;

      const { status, data } = await get(
         `${this.collection}/atribut/jenis-pengaduan`
      );

      status === 200 ? (this.data.data = data) : (this.data.run = false);

      this.data.load = false;
   }
}

export const jenisPengaduan = new AtributOnServer();
