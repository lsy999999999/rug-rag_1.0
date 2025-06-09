export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number

export type IconVariant = 'outlined' | 'rounded' | 'sharp'

export type IconColor =
  | 'primary'
  | 'secondary'
  | 'success'
  | 'warning'
  | 'error'
  | 'inherit'
  | string

export interface IconProps {
  name: string
  size?: IconSize
  variant?: IconVariant
  color?: IconColor
  fill?: number
  weight?: number
  grade?: number
  opticalSize?: number
  title?: string
}

// Common Material Symbols icon names for reference
export const CommonIcons = {
  // Navigation
  home: 'home',
  menu: 'menu',
  close: 'close',
  back: 'arrow_back',
  forward: 'arrow_forward',
  up: 'arrow_upward',
  down: 'arrow_downward',
  left: 'arrow_back',
  right: 'arrow_forward',

  // Actions
  add: 'add',
  remove: 'remove',
  edit: 'edit',
  delete: 'delete',
  save: 'save',
  cancel: 'cancel',
  search: 'search',
  filter: 'filter_list',
  sort: 'sort',
  refresh: 'refresh',

  // Status
  check: 'check',
  checkCircle: 'check_circle',
  error: 'error',
  warning: 'warning',
  info: 'info',
  help: 'help',

  // UI
  settings: 'settings',
  account: 'account_circle',
  notifications: 'notifications',
  favorite: 'favorite',
  star: 'star',
  share: 'share',
  download: 'download',
  upload: 'upload',

  // Content
  copy: 'content_copy',
  cut: 'content_cut',
  paste: 'content_paste',
  link: 'link',
  attach: 'attach_file',

  // Media
  play: 'play_arrow',
  pause: 'pause',
  stop: 'stop',
  volume: 'volume_up',
  volumeOff: 'volume_off',

  // Communication
  email: 'email',
  phone: 'phone',
  chat: 'chat',
  comment: 'comment',

  // File
  folder: 'folder',
  folderOpen: 'folder_open',
  file: 'description',
  image: 'image',
  video: 'video_file',
  audio: 'audio_file',
} as const

export type CommonIconName = keyof typeof CommonIcons
