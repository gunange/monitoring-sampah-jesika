import '@/controller/others/RuleVueValidate'

import { RequestApiController } from '@/controller/others/RequestApiController'

import AOS from 'aos'
import 'aos/dist/aos.css'

import { setDefaultOptions } from 'date-fns'
import { id } from 'date-fns/locale'

import { Form, Field, ErrorMessage } from 'vee-validate'

// other component
import vSelect from 'vue-select'
import { CountTo } from 'vue3-count-to'
import SvgIcon from '@jamescoyle/vue-icon'

export class appComponentSetup {
  constructor() {
    new RequestApiController().init()
    this.dateSetup()
    this.aosSetup()
  }

  aosSetup() {
    AOS.init({
      disable: false,
      startEvent: 'DOMContentLoaded',
      initClassName: 'aos-init',
      useClassNames: false,

      offset: 20,
      delay: 100,
      duration: 800,
      easing: 'ease-in-out',
      once: false,
      mirror: true,
    })
  }

  dateSetup() {
    setDefaultOptions({
      locale: id,
    })
  }
}

export class AppComponent {
  _app
  constructor(app) {
    this._app = app

    this.veeFormComponent()
    this.vSelectComponent()
    this.otherComponent()
  }

  veeFormComponent() {
    this._app.component('VeeForm', Form)
    this._app.component('VeeField', Field)
    this._app.component('VeeErrorMessage', ErrorMessage)
  }

  vSelectComponent() {
    vSelect.props.calculatePosition.default = (dropdownList, component, { width, top, left }) => {
      const newWidth = `${parseInt(width, 10) + 16}px`
      const newLeft = `${parseInt(left, 10) - 2}px`
      const newTop = `${parseInt(top, 10) + 7}px`

      dropdownList.style.top = newTop
      dropdownList.style.left = newLeft
      dropdownList.style.width = newWidth
    }
    this._app.component('v-select', vSelect)
  }
  otherComponent() {
    this._app.component('CountTo', CountTo)
    this._app.component('SvgIcon', SvgIcon)
  }
}

export const qrOption = {
  qrOptions: {
    typeNumber: 0,
    mode: 'Byte',
    errorCorrectionLevel: 'H',
  },
  imageOptions: {
    hideBackgroundDots: true,
    imageSize: 0.4,
    margin: 0,
  },
  dotsOptions: {
    type: 'extra-rounded',
    color: '#26249a',
    gradient: {
      type: 'linear',
      rotation: 0,
      colorStops: [
        { offset: 0, color: '#26249a' },
        { offset: 1, color: '#26249a' },
      ],
    },
  },
  backgroundOptions: {
    color: '#ffffff',
  },
  cornersSquareOptions: {
    type: 'rounded',
    color: '#26249a',
  },
  cornersDotOptions: {
    type: 'rounded',
    color: '#ED0A74',
  },
}
