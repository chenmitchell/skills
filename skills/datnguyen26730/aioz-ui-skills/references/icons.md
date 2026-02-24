---
name: aioz-ui-icons
description: Complete icon reference for AIOZ UI V2. Use this when adding icons to components, mapping Figma icon layer names to import statements, or discovering which icons are available in @aioz-ui/icon-react. Contains setup instructions, all ~500 icon names with their import identifiers, and Figma MCP name mapping rules.
---

# AIOZ UI V2 – Icon Reference

Icons ship in `@aioz-ui/icon-react` as React SVG components.

---

## Setup

### tsconfig.json paths

```json
{
  "compilerOptions": {
    "paths": {
      "@aioz-ui/icon-react": [
        "../../packages/aioz-ui/packages/icon-react/src/lucide-react.suffixed"
      ]
    }
  }
}
```

### package.json

```json
{
  "dependencies": {
    "@aioz-ui/icon-react": "workspace:^"
  }
}
```

### Importing icons

```tsx
// Named imports — always use the suffixed (PascalCase + "Icon") format
import {
  Search01Icon,
  Plus01Icon,
  Wallet01Icon,
  ArrowDownIcon,
} from '@aioz-ui/icon-react'
```

### Icon component props

```tsx
<Search01Icon size={16} />          // size prop (number, default 24)
<Search01Icon size={16} className="text-icon-neutral" />  // color via className
<Search01Icon size={20} strokeWidth={1.5} />              // stroke width
```

Use `className="text-{color-token}"` to color icons — they inherit `currentColor`.

---

## Figma MCP → Import Name Mapping Rule

**Pattern:** `icon/24px/outline/{icon-name}` → strip prefix → PascalCase → append `Icon`

| Figma MCP Layer Name               | Icon Filename    | Import             |
| ---------------------------------- | ---------------- | ------------------ |
| `icon/24px/outline/bell-02`        | `bell-02`        | `Bell02Icon`       |
| `icon/24px/outline/file-shield-02` | `file-shield-02` | `FileShield02Icon` |
| `icon/24px/outline/file-05`        | `file-05`        | `File05Icon`       |
| `icon/24px/outline/wallet-01`      | `wallet-01`      | `Wallet01Icon`     |
| `icon/24px/outline/arrow-down`     | `arrow-down`     | `ArrowDownIcon`    |
| `icon/24px/outline/search-01`      | `search-01`      | `Search01Icon`     |
| `icon/24px/outline/plus-01`        | `plus-01`        | `Plus01Icon`       |
| `icon/24px/outline/trash-01`       | `trash-01`       | `Trash01Icon`      |
| `icon/24px/outline/eye-open`       | `eye-open`       | `EyeOpenIcon`      |
| `icon/24px/outline/bar-chart-01`   | `bar-chart-01`   | `BarChart01Icon`   |

**Conversion rules:**

1. Take the last segment after the final `/`: `wallet-01`
2. Split by `-`: `["wallet", "01"]`
3. Capitalize each part: `["Wallet", "01"]`
4. Join + append `Icon`: `Wallet01Icon`

---

## Available Icons (complete list)

Source: `packages/aioz-ui/packages/icon-react/src/icons/`

### Navigation & Layout

```
ArrowDownIcon, ArrowUpIcon, ArrowLeftIcon, ArrowRightIcon
ArrowDoubleDownIcon, ArrowDoubleUpIcon, ArrowDoubleLeftIcon, ArrowDoubleRightIcon
ChevronDownIcon, ChevronUpIcon, ChevronLeftIcon, ChevronRightIcon
Layout01Icon, Layout02Icon, Layout03Icon, Layout04Icon
LayoutBottomIcon, LayoutGridIcon, LayoutLeftIcon, LayoutRightIcon, LayoutTopIcon
Menu01Icon, Menu02Icon, Menu03Icon, Menu04Icon, Menu05Icon
Home01Icon, Home02Icon, Home03Icon, Home04Icon, Home05Icon
```

### Actions

```
Plus01Icon, Plus02Icon, Plus03Icon
Trash01Icon, Trash02Icon, Trash03Icon
Edit01Icon, Edit02Icon, Edit03Icon, Edit04Icon, EditContainedIcon
DeleteIcon, CopyLeftIcon, CopyRightIcon
Download01Icon, DownloadIcon, Upload01Icon, UploadIcon
Search01Icon, Search02Icon
FilterIcon, Filter01Icon, Filter02Icon, Filter03Icon
SortHorizontalIcon, SortVertical01Icon, SortVertical02Icon
RefreshIcon, ArrowRefresh01Icon, ArrowRefresh02Icon
SaveIcon, Save01Icon, Save02Icon
ShareIcon, SendIcon, Send01Icon, Send02Icon
```

### Files & Documents

```
FileIcon, File01Icon, File02Icon, File03Icon, File04Icon, File05Icon, File06Icon
FileCheckIcon, FileCodeIcon, FileLockIcon, FilePlusIcon, FileMinusIcon
FileShield01Icon, FileShield02Icon, FileShield03Icon
FolderIcon, FolderOpenIcon, FolderPlusIcon, FolderCodeIcon
BookIcon, Book01Icon, Book02Icon, Book03Icon, Book04Icon, Book05Icon
NoteIcon, Note01Icon, Note02Icon
```

### Communication

```
Mail01Icon, Mail02Icon, Mail03Icon, Mail04Icon
MessageCircleIcon, MessageSquareIcon, MessageTextIcon
BellIcon, Bell01Icon, Bell02Icon, Bell03Icon, Bell04Icon
BellRinging01Icon, BellRinging02Icon, BellRinging03Icon, BellRinging04Icon
BellOff01Icon, BellOff02Icon
```

### Finance & Crypto

```
WalletIcon, Wallet01Icon, Wallet02Icon, Wallet03Icon, Wallet04Icon, WalletConnectIcon
CoinIcon, CoinsIcon, CoinsRotateIcon, CoinHandIcon, CoinNumberIcon
CurrencyDollarIcon, CurrencyEuroIcon, CurrencyBitcoinIcon
BankIcon, BankNote01Icon, BankNote02Icon, BankNote03Icon
TrendUp01Icon, TrendUp02Icon, TrendDown01Icon, TrendDown02Icon
BarChart01Icon, BarChart02Icon, BarChart03Icon, BarChart04Icon, BarChart05Icon
LineChartUp01Icon, LineChartUp02Icon, LineChartDown01Icon
PieChart01Icon, PieChart02Icon, PieChart03Icon
```

### Security & Identity

```
LockIcon, Lock01Icon, Lock02Icon, Lock03Icon, Lock04Icon
LockOpen01Icon, LockOpen02Icon, LockOpen03Icon
ShieldIcon, Shield01Icon, Shield02Icon, ShieldCheckIcon, ShieldPlusIcon
KeyIcon, Key01Icon, Key02Icon
FingerprintIcon, Fingerprint01Icon, Fingerprint02Icon
FaceId01Icon, FaceId02Icon
UserProfile01Icon, UserProfile02Icon, UserProfile03Icon, UserProfileCircleIcon
UserProfileGroupIcon, UsersProfiles01Icon, UsersProfiles02Icon
```

### Status & Alerts

```
CheckIcon, Check02Icon, CheckBrokenIcon, CheckContainedIcon, CheckSquareContainedIcon
AlertCircleIcon, AlertSquareIcon, AlertTriangleIcon, WarningIcon
InfoSquare01ContainedIcon, InfoCircleContainedIcon
HelpCircleContainedIcon, HelpSquareContainedIcon
CircleCheckIcon, CircleCheckFilledIcon
XIcon, X01Icon, X02Icon, X03Icon, XCircleContainedIcon, XCircleFilledIcon, XSquareContainedIcon
MinusCircleContainedIcon, MinusSquareContainedIcon
ProgressIcon, ProgressCheckmarkIcon, ProgressErrorIcon, ProgressIncompleteIcon
```

### UI Controls

```
EyeOpenIcon, EyeClosedIcon
ToggleRightIcon, ToogleLeftIcon
SwitchHorizontalIcon
ExpandIcon, Expand02Icon, MaximiseIcon, MinimiseIcon
ZoomInIcon, ZoomOutIcon
GrabIcon, CursorIcon, Cursor01Icon
DragIcon, MoveIcon
```

### Time & Calendar

```
CalendarIcon, Calendar01Icon, Calendar02Icon, Calendar03Icon, Calendar04Icon
CalendarCheckIcon, CalendarPlusIcon, CalendarMinusIcon
ClockIcon, Clock01Icon, ClockCheckIcon, ClockPlusIcon
StopwatchIcon, Stopwatch01Icon, Stopwatch02Icon, Stopwatch03Icon
HourglassIcon, Hourglass01Icon, Hourglass02Icon
```

### Media & Content

```
ImageIcon, Image01Icon, Image02Icon, Image03Icon, Image04Icon
VideoOnIcon, VideoOffIcon, CameraIcon, Camera01Icon, Camera02Icon
PlayIcon, Play01Icon, Play02Icon, PauseIcon, Pause01Icon, Pause02Icon
RecordIcon, RecordingIcon, MicrophoneIcon, Microphone01Icon, Microphone02Icon
VolumeIcon, Volume01Icon, Volume02Icon, Volume03Icon, Volume04Icon
```

### Web & Technology

```
GlobeIcon, Globe01Icon, Globe02Icon, Globe03Icon, Globe04Icon
LinkIcon, LinkAngledIcon, LinkBrokenIcon, LinkExternalIcon
BrowserIcon, BrowserCodeIcon, ComputerIcon, LaptopIcon, Laptop01Icon
ServerIcon, Server01Icon, Server02Icon, Server03Icon
CloudIcon, Cloud01Icon, Cloud02Icon
WifiOnIcon, WifiOffIcon
SettingsIcon, GearIcon
CodeIcon, Code01Icon, Code02Icon, BracketsIcon, TerminalIcon
```

### Social & Brand

```
DiscordIcon, TelegramIcon, TwitterIcon, FacebookIcon, YoutubeIcon
GoogleIcon, MicrosoftIcon, MetamaskIcon, PhantomIcon
EthIcon, BnbIcon, CoinbaseWalletIcon, TrustWalletIcon
```

### Miscellaneous

```
StarIcon, Star01Icon, Star02Icon, StarFilledIcon, StarsIcon
HeartIcon, FavouriteIcon
TagIcon, TicketIcon, Ticket01Icon, Ticket02Icon
GiftIcon, Gift01Icon, Gift02Icon
RocketIcon, Rocket02Icon
TrophyIcon, MedalIcon, DiamondIcon
SunIcon, Sun01Icon, Sun02Icon, Moon01Icon, Moon02Icon
```

---

## Common Usage Patterns

```tsx
// Navigation icon + label
import { BarChart01Icon, ComputerIcon, Wallet01Icon, Book01Icon, FilterIcon } from "@aioz-ui/icon-react"

<nav>
  <a className="flex items-center gap-2 text-subtitle-neutral">
    <BarChart01Icon size={16} />
    <span className="text-body-02">Dashboard</span>
  </a>
</nav>

// Action button with icon
import { Plus01Icon, Search01Icon, Trash01Icon, EyeOpenIcon } from "@aioz-ui/icon-react"
import { Button } from "@aioz-ui/core-v2/components"

<Button variant="primary" size="md" leftIcon={<Plus01Icon size={16} />}>
  Add site
</Button>

// Search input with icon
import { Input } from "@aioz-ui/core-v2/components"
import { Search01Icon } from "@aioz-ui/icon-react"

<Input
  placeholder="Search..."
  size="sm"
  endIcon={<Search01Icon size={16} className="text-icon-neutral" />}
/>

// Icon-only action buttons (table quick actions)
<button className="w-8 h-8 rounded-lg border border-border-neutral flex items-center justify-center text-icon-neutral hover:bg-sf-neutral hover:text-title-neutral transition-colors">
  <EyeOpenIcon size={16} />
</button>
<button className="w-8 h-8 rounded-lg border border-border-error flex items-center justify-center text-onsf-text-error hover:bg-sf-error-sec transition-colors">
  <Trash01Icon size={16} />
</button>

// Status icon in header
import { CoinsIcon } from "@aioz-ui/icon-react"

<div className="w-7 h-7 rounded-full border border-border-neutral flex items-center justify-center bg-sf-screen">
  <CoinsIcon size={16} className="text-icon-neutral" />
</div>
```
