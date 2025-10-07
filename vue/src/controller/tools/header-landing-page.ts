import { ref } from 'vue'

export class HeaderLandingPage {
  onScroll = false
  className = 'on-scroll'
  cssRootName = '--header-height'
  header
  timeOut

  constructor(header) {
    this.header = header
  }

  init() {
    this.setHeightHeader()
    window.addEventListener('scroll', this.handleScroll)
  }

  handleScrollDebounced(scrollTop) {
    clearTimeout(this.timeOut)
    this.timeOut = setTimeout(() => {
      this.onScroll = scrollTop > 631
    }, 150)
  }

  handleScroll = () => {
    // Menggunakan arrow function
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    var sticky = this.header.offsetTop
    if (scrollTop > sticky) {
      this.header.classList.add(this.className)
    } else {
      this.header.classList.remove(this.className)
    }
    this.handleScrollDebounced(scrollTop)
  }

  setHeightHeader() {
    if (!this.header) return
    const height = this.header.offsetHeight ?? 30
    document.documentElement.style.setProperty(this.cssRootName, `${height}px`)
  }
}
