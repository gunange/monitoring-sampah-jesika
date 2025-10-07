import 'primeicons/primeicons.css'

import { locale } from './locale'
import { gunangePreset, gunangePt } from './presets'

/* ----------- css -----------  */

import AutoComplete from 'primevue/autocomplete'
import AnimateOnScroll from 'primevue/animateonscroll'
import Avatar from 'primevue/avatar'
import AvatarGroup from 'primevue/avatargroup'
import Badge from 'primevue/badge'
import BadgeDirective from 'primevue/badgedirective'
import BlockUI from 'primevue/blockui'
import Button from 'primevue/button'
import ButtonGroup from 'primevue/buttongroup'
import Breadcrumb from 'primevue/breadcrumb'

import DatePicker from 'primevue/datepicker'

import Card from 'primevue/card'
import CascadeSelect from 'primevue/cascadeselect'
import Carousel from 'primevue/carousel'
import Checkbox from 'primevue/checkbox'
import Chip from 'primevue/chip'
import Chips from 'primevue/chips'
import ColorPicker from 'primevue/colorpicker'
import Column from 'primevue/column'
import ColumnGroup from 'primevue/columngroup'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmPopup from 'primevue/confirmpopup'
import ContextMenu from 'primevue/contextmenu'
import DataTable from 'primevue/datatable'
import DataView from 'primevue/dataview'

import DeferredContent from 'primevue/deferredcontent'
import Dialog from 'primevue/dialog'
import Divider from 'primevue/divider'
import Dock from 'primevue/dock'
import Dropdown from 'primevue/dropdown'
import DynamicDialog from 'primevue/dynamicdialog'
import Fieldset from 'primevue/fieldset'
import FileUpload from 'primevue/fileupload'
import FocusTrap from 'primevue/focustrap'
import Galleria from 'primevue/galleria'
import Image from 'primevue/image'
import InlineMessage from 'primevue/inlinemessage'
import Inplace from 'primevue/inplace'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import ToggleSwitch from 'primevue/toggleswitch'

import InputText from 'primevue/inputtext'
import InputMask from 'primevue/inputmask'
import InputNumber from 'primevue/inputnumber'
import Knob from 'primevue/knob'
import Listbox from 'primevue/listbox'

import Menu from 'primevue/menu'
import Menubar from 'primevue/menubar'
import Message from 'primevue/message'
import MultiSelect from 'primevue/multiselect'
import OrderList from 'primevue/orderlist'
import OrganizationChart from 'primevue/organizationchart'
import OverlayPanel from 'primevue/overlaypanel'
import Paginator from 'primevue/paginator'
import Panel from 'primevue/panel'
import PanelMenu from 'primevue/panelmenu'
import Password from 'primevue/password'
import PickList from 'primevue/picklist'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Rating from 'primevue/rating'
import RadioButton from 'primevue/radiobutton'
import Ripple from 'primevue/ripple'
import Row from 'primevue/row'
import SelectButton from 'primevue/selectbutton'
import ScrollPanel from 'primevue/scrollpanel'
import ScrollTop from 'primevue/scrolltop'
import Skeleton from 'primevue/skeleton'
import Slider from 'primevue/slider'
import Sidebar from 'primevue/sidebar'
import SpeedDial from 'primevue/speeddial'
import SplitButton from 'primevue/splitbutton'
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import Steps from 'primevue/steps'
import StyleClass from 'primevue/styleclass'
import TabMenu from 'primevue/tabmenu'
import TieredMenu from 'primevue/tieredmenu'
import Textarea from 'primevue/textarea'
import Toast from 'primevue/toast'
import Toolbar from 'primevue/toolbar'

import Tag from 'primevue/tag'
import Terminal from 'primevue/terminal'
import Timeline from 'primevue/timeline'
import ToggleButton from 'primevue/togglebutton'
import Tooltip from 'primevue/tooltip'
import Tree from 'primevue/tree'
import TreeSelect from 'primevue/treeselect'
import TreeTable from 'primevue/treetable'

import KeyFilter from 'primevue/keyfilter'

import Popover from 'primevue/popover'
import OverlayBadge from 'primevue/overlaybadge'

// Tabs
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'

// Accordion
import Accordion from 'primevue/accordion'
import AccordionPanel from 'primevue/accordionpanel'
import AccordionHeader from 'primevue/accordionheader'
import AccordionContent from 'primevue/accordioncontent'

// Step
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepPanels from 'primevue/steppanels'
import StepItem from 'primevue/stepitem'
import Step from 'primevue/step'
import StepPanel from 'primevue/steppanel'

export class AppPrimeConfig {
  private _app

  constructor(app: any) {
    this._app = app
  }

  init() {
    this.runComponent()
    this.runDirective()
  }

  runComponent() {
    this._app.component('AutoComplete', AutoComplete)
    this._app.component('Avatar', Avatar)
    this._app.component('AvatarGroup', AvatarGroup)
    this._app.component('Badge', Badge)
    this._app.component('BlockUI', BlockUI)
    this._app.component('Breadcrumb', Breadcrumb)
    this._app.component('Button', Button)
    this._app.component('ButtonGroup', ButtonGroup)
    this._app.component('DatePicker', DatePicker)
    this._app.component('Card', Card)
    this._app.component('Carousel', Carousel)
    this._app.component('CascadeSelect', CascadeSelect)
    this._app.component('Checkbox', Checkbox)
    this._app.component('Chip', Chip)
    this._app.component('Chips', Chips)
    this._app.component('ColorPicker', ColorPicker)
    this._app.component('Column', Column)
    this._app.component('ColumnGroup', ColumnGroup)
    this._app.component('ConfirmDialog', ConfirmDialog)
    this._app.component('ConfirmPopup', ConfirmPopup)
    this._app.component('ContextMenu', ContextMenu)
    this._app.component('DataTable', DataTable)
    this._app.component('DataView', DataView)

    this._app.component('DeferredContent', DeferredContent)
    this._app.component('Dialog', Dialog)
    this._app.component('Divider', Divider)
    this._app.component('Dock', Dock)
    this._app.component('Dropdown', Dropdown)
    this._app.component('DynamicDialog', DynamicDialog)
    this._app.component('Fieldset', Fieldset)
    this._app.component('FileUpload', FileUpload)
    this._app.component('Galleria', Galleria)
    this._app.component('Image', Image)
    this._app.component('InlineMessage', InlineMessage)
    this._app.component('Inplace', Inplace)
    this._app.component('InputGroup', InputGroup)
    this._app.component('InputGroupAddon', InputGroupAddon)
    this._app.component('InputMask', InputMask)
    this._app.component('InputNumber', InputNumber)
    this._app.component('ToggleSwitch', ToggleSwitch)
    this._app.component('InputText', InputText)
    this._app.component('Knob', Knob)
    this._app.component('Listbox', Listbox)

    this._app.component('Menu', Menu)
    this._app.component('Menubar', Menubar)
    this._app.component('Message', Message)
    this._app.component('MultiSelect', MultiSelect)
    this._app.component('OrderList', OrderList)
    this._app.component('OrganizationChart', OrganizationChart)
    this._app.component('OverlayPanel', OverlayPanel)
    this._app.component('Paginator', Paginator)
    this._app.component('Panel', Panel)
    this._app.component('PanelMenu', PanelMenu)
    this._app.component('Password', Password)
    this._app.component('PickList', PickList)
    this._app.component('ProgressBar', ProgressBar)
    this._app.component('ProgressSpinner', ProgressSpinner)
    this._app.component('RadioButton', RadioButton)
    this._app.component('Rating', Rating)
    this._app.component('Row', Row)
    this._app.component('SelectButton', SelectButton)
    this._app.component('ScrollPanel', ScrollPanel)
    this._app.component('ScrollTop', ScrollTop)
    this._app.component('Slider', Slider)
    this._app.component('Sidebar', Sidebar)
    this._app.component('Skeleton', Skeleton)
    this._app.component('SpeedDial', SpeedDial)
    this._app.component('SplitButton', SplitButton)
    this._app.component('Splitter', Splitter)
    this._app.component('SplitterPanel', SplitterPanel)
    this._app.component('Steps', Steps)

    this._app.component('Tag', Tag)
    this._app.component('Textarea', Textarea)
    this._app.component('Terminal', Terminal)
    this._app.component('TieredMenu', TieredMenu)
    this._app.component('Timeline', Timeline)
    this._app.component('Toast', Toast)
    this._app.component('Toolbar', Toolbar)
    this._app.component('ToggleButton', ToggleButton)
    this._app.component('Tree', Tree)
    this._app.component('TreeSelect', TreeSelect)
    this._app.component('TreeTable', TreeTable)
    this._app.component('Popover', Popover)
    this._app.component('OverlayBadge', OverlayBadge)

    // Tabs
    this._app.component('Tabs', Tabs)
    this._app.component('TabList', TabList)
    this._app.component('Tab', Tab)
    this._app.component('TabPanels', TabPanels)
    this._app.component('TabMenu', TabMenu)
    this._app.component('TabPanel', TabPanel)

    // Accordion
    this._app.component('Accordion', Accordion)
    this._app.component('AccordionPanel', AccordionPanel)
    this._app.component('AccordionHeader', AccordionHeader)
    this._app.component('AccordionContent', AccordionContent)

    // Step
    this._app.component('Stepper', Stepper)
    this._app.component('StepList', StepList)
    this._app.component('StepPanels', StepPanels)
    this._app.component('StepItem', StepItem)
    this._app.component('Step', Step)
    this._app.component('StepPanel', StepPanel)
  }
  runDirective() {
    this._app.directive('tooltip', Tooltip)
    this._app.directive('badge', BadgeDirective)
    this._app.directive('ripple', Ripple)
    this._app.directive('styleclass', StyleClass)
    this._app.directive('focustrap', FocusTrap)
    this._app.directive('animateonscroll', AnimateOnScroll)
    this._app.directive('keyfilter', KeyFilter)
  }
}

export const primeConfUse = {
  zIndex: {
    modal: 2001, //dialog, sidebar
    overlay: 2001, //dropdown, overlaypanel
    menu: 2001, //overlay menus
    tooltip: 2001, //tooltip
  },
  pt: gunangePt,
  // unstyled: true,
  ripple: true,
  locale: locale.id,
  theme: {
    preset: gunangePreset,
    options: {
      // darkModeSelector: '.gunange-dark',
      darkModeSelector: 'system',
      cssLayer: {
        name: 'primevue',
        order: 'theme, base, primevue',
      },
    },
  },
}

export const breakpoints = {
  dialog: {
    '1351px': '50vw',
    '995px': '85vw',
    '815px': '95vw',
    '575px': '92vw',
    '340px': '98vw',
  },
}

export const twilightConf = {
  colors: {
    primary: 'rgb(var(--primary))',
    'primary-inverse': 'rgb(var(--primary-inverse))',
    'primary-hover': 'rgb(var(--primary-hover))',
    'primary-active-color': 'rgb(var(--primary-active-color))',

    'primary-highlight': 'rgb(var(--primary)/var(--primary-highlight-opacity))',
    'primary-highlight-inverse': 'rgb(var(--primary-highlight-inverse))',
    'primary-highlight-hover': 'rgb(var(--primary)/var(--primary-highlight-hover-opacity))',

    'primary-50': 'rgb(var(--primary-50))',
    'primary-100': 'rgb(var(--primary-100))',
    'primary-200': 'rgb(var(--primary-200))',
    'primary-300': 'rgb(var(--primary-300))',
    'primary-400': 'rgb(var(--primary-400))',
    'primary-500': 'rgb(var(--primary-500))',
    'primary-600': 'rgb(var(--primary-600))',
    'primary-700': 'rgb(var(--primary-700))',
    'primary-800': 'rgb(var(--primary-800))',
    'primary-900': 'rgb(var(--primary-900))',
    'primary-950': 'rgb(var(--primary-950))',

    'surface-0': 'rgb(var(--surface-0))',
    'surface-50': 'rgb(var(--surface-50))',
    'surface-100': 'rgb(var(--surface-100))',
    'surface-200': 'rgb(var(--surface-200))',
    'surface-300': 'rgb(var(--surface-300))',
    'surface-400': 'rgb(var(--surface-400))',
    'surface-500': 'rgb(var(--surface-500))',
    'surface-600': 'rgb(var(--surface-600))',
    'surface-700': 'rgb(var(--surface-700))',
    'surface-800': 'rgb(var(--surface-800))',
    'surface-900': 'rgb(var(--surface-900))',
    'surface-950': 'rgb(var(--surface-950))',
  },
}
