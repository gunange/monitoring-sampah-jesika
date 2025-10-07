import { defineStore } from 'pinia'
import { reactive } from 'vue'
import { ref } from 'vue'

const defaultAtribut = {
  error: false,
  load: false,
  run: false,
  status: 'on-going',
  data: [],
}

export const homeStore = defineStore('homeStore', {
  state: () => ({
    onScroll: false,
    form_registrasi: {
      form: {},
      atribut: {
        prodi: { ...defaultAtribut },
        agama: { ...defaultAtribut },
        jk: { ...defaultAtribut },
        negara: { ...defaultAtribut },
        wilayah: { ...defaultAtribut },
        jt: { ...defaultAtribut },
        at: { ...defaultAtribut },
        kk: { ...defaultAtribut },
        alat_transportasi: { ...defaultAtribut },
        kebutuhan_khusus: { ...defaultAtribut },
      },
      sesi: {
        error: false,
        load: false,
        run: false,
        msg: false,
        data: null,
      },
    },
    ref_form: {},
  }),
  actions: {
    reset_form() {
      this.form_registrasi.form = {}
    },
  },
  getters: {
    default_atribut: () => defaultAtribut,
  },
})
