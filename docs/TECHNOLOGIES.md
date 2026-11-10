# Technology coverage

Snapshot: **2026-11-10** · **46 public, non-fork repositories**, excluding the profile repository.

The audit found **159 technology families** containing **229 distinct package/CDN identifiers**. It inspected 38 manifests across 34 repositories, plus root and one-level HTML files in 11 repositories without manifests.

**Coverage = repositories with a declared technology ÷ all eligible repositories.** A technology counts once per repository, even when several manifests or aliases declare it. The denominator includes repositories without manifests. Technologies and languages overlap, so their percentages do not sum to 100.

These percentages describe current public default branches. They are not proficiency scores, time spent, code-byte percentages, deployed runtime usage, or a complete history of everything used. Private and deleted repositories, transitive dependencies, undeclared imports, and tools used outside these repositories are outside the measurement.

Runtime, development, optional, and peer dependency declarations are included. Clear families are grouped (for example, React and React DOM); every original identifier remains in the table. Type declarations are grouped separately and do not imply that a repository is written in TypeScript. CDN identifiers prefixed with `cdn:` represent an explicitly linked service or library rather than an npm package.

The language table uses file-extension presence in first-party source, configuration, and test files. Generated/vendor directories and minified JavaScript/CSS files are excluded; data formats, assets, and languages embedded inside HTML are not inferred. The separate profile primary-language chart uses GitHub’s one primary-language label per repository.

## Source-language presence

| Language | Repositories | Coverage | Observed extensions |
| --- | ---: | ---: | --- |
| CSS | 38 / 46 | 82.61% | `.css` |
| JavaScript | 38 / 46 | 82.61% | `.cjs`, `.js`, `.jsx`, `.mjs` |
| HTML | 28 / 46 | 60.87% | `.html` |
| TypeScript | 12 / 46 | 26.09% | `.mts`, `.ts`, `.tsx` |
| EJS | 2 / 46 | 4.35% | `.ejs` |
| Python | 1 / 46 | 2.17% | `.py` |

## Complete technology inventory

| Technology | Category | Repositories | Coverage | Declared package/CDN identifiers |
| --- | --- | ---: | ---: | --- |
| Tailwind CSS | Styling | 32 / 46 | 69.57% | `@tailwindcss/postcss`, `@tailwindcss/typography`, `@tailwindcss/vite`, `tailwindcss` |
| React | UI framework | 31 / 46 | 67.39% | `react`, `react-dom` |
| TypeScript type definitions | Type definitions | 28 / 46 | 60.87% | `@types/bcryptjs`, `@types/canvas-confetti`, `@types/chai`, `@types/compression`, `@types/cors`, `@types/express`, `@types/jsonwebtoken`, `@types/leaflet`, `@types/markdown-it`, `@types/mocha`, `@types/node`, `@types/react`, `@types/react-dom`, `@types/three` |
| ESLint | Development tooling | 26 / 46 | 56.52% | `@eslint/eslintrc`, `@eslint/js`, `eslint`, `eslint-config-next`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh` |
| PostCSS | Build tooling | 20 / 46 | 43.48% | `postcss` |
| Vite | Build tooling | 17 / 46 | 36.96% | `@vitejs/plugin-react`, `vite`, `vite-plugin-pwa`, `vite-tsconfig-paths` |
| Autoprefixer | Build tooling | 16 / 46 | 34.78% | `autoprefixer` |
| Motion / Framer Motion | Animation | 14 / 46 | 30.43% | `framer-motion`, `motion` |
| Next.js | Web framework | 13 / 46 | 28.26% | `next` |
| Lucide React | Icons | 12 / 46 | 26.09% | `lucide-react` |
| React Icons | Icons | 12 / 46 | 26.09% | `react-icons` |
| TypeScript | Language tooling | 12 / 46 | 26.09% | `typescript` |
| GSAP | Animation | 11 / 46 | 23.91% | `@gsap/react`, `gsap` |
| React Router | Routing | 9 / 46 | 19.57% | `@react-router/dev`, `@react-router/node`, `@react-router/serve`, `react-router`, `react-router-dom` |
| clsx | Styling utility | 8 / 46 | 17.39% | `clsx` |
| Tailwind Merge | Styling | 8 / 46 | 17.39% | `tailwind-merge` |
| Three.js | 3D graphics | 8 / 46 | 17.39% | `three` |
| Express | Backend framework | 7 / 46 | 15.22% | `express` |
| globals | Library | 7 / 46 | 15.22% | `globals` |
| Drei | 3D graphics | 6 / 46 | 13.04% | `@react-three/drei` |
| Mongoose | Database | 6 / 46 | 13.04% | `mongoose` |
| React Three Fiber | 3D graphics | 6 / 46 | 13.04% | `@react-three/fiber` |
| Class Variance Authority | Styling utility | 5 / 46 | 10.87% | `class-variance-authority` |
| JSON Web Token | Authentication | 5 / 46 | 10.87% | `jsonwebtoken` |
| multer | Library | 5 / 46 | 10.87% | `multer` |
| Axios | HTTP client | 4 / 46 | 8.70% | `axios` |
| bcryptjs | Authentication | 4 / 46 | 8.70% | `bcryptjs` |
| cookie-parser | Library | 4 / 46 | 8.70% | `cookie-parser` |
| dotenv | Library | 4 / 46 | 8.70% | `dotenv` |
| Google Fonts | Typography | 4 / 46 | 8.70% | `cdn:google-fonts` |
| Radix UI | UI primitives | 4 / 46 | 8.70% | `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-label`, `@radix-ui/react-select`, `@radix-ui/react-slot`, `@radix-ui/react-switch`, `@radix-ui/react-toast`, `@radix-ui/react-visually-hidden` |
| React Hook Form | Forms | 4 / 46 | 8.70% | `react-hook-form` |
| Remix Icon | Icons | 4 / 46 | 8.70% | `remixicon` |
| Tailwind CSS Animate | Animation | 4 / 46 | 8.70% | `tailwindcss-animate` |
| Cloudinary | Media service | 3 / 46 | 6.52% | `cloudinary` |
| cors | Library | 3 / 46 | 6.52% | `cors` |
| Locomotive Scroll | Animation | 3 / 46 | 6.52% | `locomotive-scroll` |
| MongoDB driver | Database | 3 / 46 | 6.52% | `mongodb` |
| Nodemon | Development tooling | 3 / 46 | 6.52% | `nodemon` |
| Socket.IO | Realtime | 3 / 46 | 6.52% | `@socket.io/redis-adapter`, `socket.io`, `socket.io-client` |
| TW Animate CSS | Animation | 3 / 46 | 6.52% | `tw-animate-css` |
| Vercel Analytics | Analytics | 3 / 46 | 6.52% | `@vercel/analytics` |
| Zod | Validation | 3 / 46 | 6.52% | `zod` |
| bcrypt | Authentication | 2 / 46 | 4.35% | `bcrypt` |
| Clerk | Authentication | 2 / 46 | 4.35% | `@clerk/nextjs` |
| debug | Library | 2 / 46 | 4.35% | `debug` |
| EJS | Templating | 2 / 46 | 4.35% | `ejs` |
| express-session | Library | 2 / 46 | 4.35% | `express-session` |
| Font Awesome | Icons | 2 / 46 | 4.35% | `font-awesome` |
| helmet | Library | 2 / 46 | 4.35% | `helmet` |
| Hook Form resolvers | Forms | 2 / 46 | 4.35% | `@hookform/resolvers` |
| http-errors | Library | 2 / 46 | 4.35% | `http-errors` |
| jQuery | UI library | 2 / 46 | 4.35% | `jquery` |
| Lenis | Animation | 2 / 46 | 4.35% | `lenis` |
| morgan | Library | 2 / 46 | 4.35% | `morgan` |
| next-themes | Library | 2 / 46 | 4.35% | `next-themes` |
| Nodemailer | Email | 2 / 46 | 4.35% | `nodemailer` |
| ogl | Library | 2 / 46 | 4.35% | `ogl` |
| Passport | Authentication | 2 / 46 | 4.35% | `passport`, `passport-local`, `passport-local-mongoose` |
| React Chart.js | Charts | 2 / 46 | 4.35% | `react-chartjs-2` |
| react-datepicker | Library | 2 / 46 | 4.35% | `react-datepicker` |
| react-toastify | Library | 2 / 46 | 4.35% | `react-toastify` |
| Recharts | Charts | 2 / 46 | 4.35% | `recharts` |
| Redux | State management | 2 / 46 | 4.35% | `@reduxjs/toolkit`, `react-redux` |
| tsx | Language tooling | 2 / 46 | 4.35% | `tsx` |
| uuid | Library | 2 / 46 | 4.35% | `uuid` |
| Zustand | State management | 2 / 46 | 4.35% | `zustand` |
| @popperjs/core | Library | 1 / 46 | 2.17% | `@popperjs/core` |
| @use-gesture/react | Library | 1 / 46 | 2.17% | `@use-gesture/react` |
| Animate.css | Animation | 1 / 46 | 2.17% | `animate.css` |
| Anime.js | Animation | 1 / 46 | 2.17% | `animejs` |
| baseline-browser-mapping | Library | 1 / 46 | 2.17% | `baseline-browser-mapping` |
| body-parser | Library | 1 / 46 | 2.17% | `body-parser` |
| Bootstrap | UI framework | 1 / 46 | 2.17% | `bootstrap` |
| canvas-confetti | Library | 1 / 46 | 2.17% | `canvas-confetti` |
| Chainlink Contracts | Web3 | 1 / 46 | 2.17% | `@chainlink/contracts` |
| Chakra UI | UI framework | 1 / 46 | 2.17% | `@chakra-ui/icons`, `@chakra-ui/react` |
| Chart.js | Charts | 1 / 46 | 2.17% | `chart.js` |
| classnames | Styling utility | 1 / 46 | 2.17% | `classnames` |
| cobe | Library | 1 / 46 | 2.17% | `cobe` |
| compression | Library | 1 / 46 | 2.17% | `compression` |
| concurrently | Library | 1 / 46 | 2.17% | `concurrently` |
| connect-flash | Library | 1 / 46 | 2.17% | `connect-flash` |
| connect-mongo | Library | 1 / 46 | 2.17% | `connect-mongo` |
| ControlKit | UI controls | 1 / 46 | 2.17% | `cdn:controlkit.js` |
| Create React App | Build tooling | 1 / 46 | 2.17% | `react-scripts` |
| cron | Library | 1 / 46 | 2.17% | `cron` |
| cross-env | Library | 1 / 46 | 2.17% | `cross-env` |
| date-fns | Library | 1 / 46 | 2.17% | `date-fns` |
| dayjs | Library | 1 / 46 | 2.17% | `dayjs` |
| Drizzle | Database | 1 / 46 | 2.17% | `drizzle-kit`, `drizzle-orm` |
| EmailJS | Email | 1 / 46 | 2.17% | `@emailjs/browser` |
| Emotion | Styling | 1 / 46 | 2.17% | `@emotion/react`, `@emotion/styled` |
| ethers.js | Web3 | 1 / 46 | 2.17% | `ethers` |
| express-fileupload | Library | 1 / 46 | 2.17% | `express-fileupload` |
| express-rate-limit | Library | 1 / 46 | 2.17% | `express-rate-limit` |
| express-validator | Library | 1 / 46 | 2.17% | `express-validator` |
| Google Generative AI SDK | AI | 1 / 46 | 2.17% | `@google/generative-ai` |
| Hardhat | Web3 tooling | 1 / 46 | 2.17% | `@nomicfoundation/hardhat-chai-matchers`, `@nomicfoundation/hardhat-ethers`, `@nomicfoundation/hardhat-ignition`, `@nomicfoundation/hardhat-ignition-ethers`, `@nomicfoundation/hardhat-network-helpers`, `@nomicfoundation/hardhat-toolbox`, `@nomicfoundation/hardhat-verify`, `@nomicfoundation/ignition-core`, `hardhat`, `hardhat-gas-reporter` |
| ioredis | Database | 1 / 46 | 2.17% | `ioredis` |
| isbot | Library | 1 / 46 | 2.17% | `isbot` |
| JOSE | Authentication | 1 / 46 | 2.17% | `jose` |
| LayerZero | Web3 | 1 / 46 | 2.17% | `@layerzerolabs/lz-evm-oapp-v2` |
| Leaflet | Maps | 1 / 46 | 2.17% | `leaflet` |
| Lettering.js | Typography | 1 / 46 | 2.17% | `cdn:lettering.js` |
| Lit Protocol | Web3 | 1 / 46 | 2.17% | `@lit-protocol/lit-node-client` |
| maath | Library | 1 / 46 | 2.17% | `maath` |
| markdown-it | Library | 1 / 46 | 2.17% | `markdown-it` |
| Materialize | UI framework | 1 / 46 | 2.17% | `materialize-css` |
| moment | Library | 1 / 46 | 2.17% | `moment` |
| nanoid | Library | 1 / 46 | 2.17% | `nanoid` |
| Neon | Database | 1 / 46 | 2.17% | `@neondatabase/serverless` |
| NextAuth.js | Authentication | 1 / 46 | 2.17% | `next-auth` |
| OpenZeppelin Contracts | Web3 | 1 / 46 | 2.17% | `@openzeppelin/contracts` |
| path | Library | 1 / 46 | 2.17% | `path` |
| PDF.js | Documents | 1 / 46 | 2.17% | `pdfjs-dist` |
| Postgres.js | Database | 1 / 46 | 2.17% | `postgres` |
| postprocessing | Library | 1 / 46 | 2.17% | `postprocessing` |
| Prettier | Development tooling | 1 / 46 | 2.17% | `prettier` |
| qrcode | Library | 1 / 46 | 2.17% | `qrcode` |
| qrcode-terminal | Library | 1 / 46 | 2.17% | `qrcode-terminal` |
| Rapier | 3D physics | 1 / 46 | 2.17% | `@dimforge/rapier3d-compat` |
| React Google Maps | Maps | 1 / 46 | 2.17% | `@react-google-maps/api` |
| React Leaflet | Maps | 1 / 46 | 2.17% | `react-leaflet` |
| React Spring Three | Animation | 1 / 46 | 2.17% | `@react-spring/three` |
| React Three Postprocessing | 3D graphics | 1 / 46 | 2.17% | `@react-three/postprocessing` |
| React Three Rapier | 3D physics | 1 / 46 | 2.17% | `@react-three/rapier` |
| react-color | Library | 1 / 46 | 2.17% | `react-color` |
| react-dropzone | Library | 1 / 46 | 2.17% | `react-dropzone` |
| react-hot-toast | Library | 1 / 46 | 2.17% | `react-hot-toast` |
| react-infinite-scroll-component | Library | 1 / 46 | 2.17% | `react-infinite-scroll-component` |
| react-player | Library | 1 / 46 | 2.17% | `react-player` |
| react-vertical-timeline-component | Library | 1 / 46 | 2.17% | `react-vertical-timeline-component` |
| Recoil | State management | 1 / 46 | 2.17% | `recoil` |
| Resend | Email | 1 / 46 | 2.17% | `resend` |
| Sanity | Content management | 1 / 46 | 2.17% | `@sanity/image-url`, `@sanity/vision`, `next-sanity`, `sanity`, `sanity-plugin-markdown` |
| server-only | Library | 1 / 46 | 2.17% | `server-only` |
| Shery.js | Animation | 1 / 46 | 2.17% | `sheryjs` |
| Sign Protocol | Web3 | 1 / 46 | 2.17% | `@ethsign/sp-sdk` |
| Solidity Coverage | Web3 tooling | 1 / 46 | 2.17% | `solidity-coverage` |
| sonner | Library | 1 / 46 | 2.17% | `sonner` |
| Stream | Video and realtime | 1 / 46 | 2.17% | `@stream-io/node-sdk`, `@stream-io/video-react-sdk` |
| Styled Components | Styling | 1 / 46 | 2.17% | `styled-components` |
| sweetalert | Library | 1 / 46 | 2.17% | `sweetalert` |
| swiper | Library | 1 / 46 | 2.17% | `swiper` |
| Testing Library | Testing | 1 / 46 | 2.17% | `@testing-library/jest-dom`, `@testing-library/react`, `@testing-library/user-event` |
| Textillate | Animation | 1 / 46 | 2.17% | `textillate` |
| ts-node-dev | Language tooling | 1 / 46 | 2.17% | `ts-node-dev` |
| tsParticles | Animation | 1 / 46 | 2.17% | `tsparticles` |
| TypeChain | Web3 tooling | 1 / 46 | 2.17% | `@typechain/ethers-v6`, `@typechain/hardhat`, `typechain` |
| validator | Library | 1 / 46 | 2.17% | `validator` |
| Valtio | State management | 1 / 46 | 2.17% | `valtio` |
| Viem | Web3 | 1 / 46 | 2.17% | `viem` |
| Vitest | Testing | 1 / 46 | 2.17% | `vitest` |
| web-vitals | Library | 1 / 46 | 2.17% | `web-vitals` |
| Web3Auth | Authentication | 1 / 46 | 2.17% | `@web3auth/base`, `@web3auth/ethereum-provider`, `@web3auth/modal` |
| whatsapp-web.js | Library | 1 / 46 | 2.17% | `whatsapp-web.js` |
| Workbox | Progressive web apps | 1 / 46 | 2.17% | `workbox-core`, `workbox-precaching`, `workbox-routing`, `workbox-strategies` |
| Workspace package: backend | Project dependency | 1 / 46 | 2.17% | `backend` |

<details>
<summary>Repositories behind each technology</summary>

| Technology | Repositories with evidence |
| --- | --- |
| Tailwind CSS | `Apple-iPhone15`, `Baithak`, `book-store-website`, `card`, `Cinefy`, `Code-Vault`, `devndez`, `Edusavvy`, `HackShastra1`, `HackShastra2.0`, `IPL-Score-Predictor`, `ochi-clone`, `OTP-Generator`, `Password-Generator`, `Pen-Brawl`, `PitchDeck`, `Portfolio`, `Portfolio-2.0`, `react-api-project`, `Refokus`, `Resumify`, `Routing`, `Samyoj`, `shirt-showcaser`, `songs`, `Spools`, `Strot`, `tailwind`, `todo-list`, `Unoverse`, `Wastify`, `Zentry` |
| React | `4th-Dimension`, `Apple-iPhone15`, `Baithak`, `book-store-website`, `card`, `Cinefy`, `Code-Vault`, `devndez`, `Edusavvy`, `HackShastra1`, `HackShastra2.0`, `HRMS`, `IPL-Score-Predictor`, `ochi-clone`, `Pen-Brawl`, `PitchDeck`, `Portfolio`, `Portfolio-2.0`, `react-api-project`, `Refokus`, `Resumify`, `Routing`, `Samyoj`, `shirt-showcaser`, `songs`, `Spools`, `Strot`, `todo-list`, `Unoverse`, `Wastify`, `Zentry` |
| TypeScript type definitions | `4th-Dimension`, `Apple-iPhone15`, `Baithak`, `book-store-website`, `card`, `Cinefy`, `devndez`, `Edusavvy`, `HackShastra1`, `HackShastra2.0`, `IPL-Score-Predictor`, `ochi-clone`, `Pen-Brawl`, `PitchDeck`, `Portfolio`, `Portfolio-2.0`, `react-api-project`, `Refokus`, `Resumify`, `Routing`, `Samyoj`, `shirt-showcaser`, `songs`, `Spools`, `Strot`, `Unoverse`, `Wastify`, `Zentry` |
| ESLint | `Apple-iPhone15`, `Baithak`, `book-store-website`, `card`, `Cinefy`, `Code-Vault`, `devndez`, `Edusavvy`, `HackShastra1`, `HackShastra2.0`, `IPL-Score-Predictor`, `ochi-clone`, `Pen-Brawl`, `PitchDeck`, `Portfolio`, `Portfolio-2.0`, `react-api-project`, `Refokus`, `Routing`, `Samyoj`, `shirt-showcaser`, `songs`, `Spools`, `Strot`, `Unoverse`, `Zentry` |
| PostCSS | `Apple-iPhone15`, `Baithak`, `book-store-website`, `card`, `Cinefy`, `Edusavvy`, `HackShastra1`, `ochi-clone`, `Pen-Brawl`, `PitchDeck`, `Portfolio`, `react-api-project`, `Refokus`, `Routing`, `shirt-showcaser`, `songs`, `Spools`, `todo-list`, `Wastify`, `Zentry` |
| Vite | `Apple-iPhone15`, `book-store-website`, `card`, `Cinefy`, `Edusavvy`, `HackShastra1`, `IPL-Score-Predictor`, `ochi-clone`, `Portfolio`, `react-api-project`, `Refokus`, `Resumify`, `Routing`, `shirt-showcaser`, `songs`, `Spools`, `Zentry` |
| Autoprefixer | `Apple-iPhone15`, `book-store-website`, `card`, `Cinefy`, `Edusavvy`, `HackShastra1`, `ochi-clone`, `Pen-Brawl`, `Portfolio`, `react-api-project`, `Refokus`, `Routing`, `shirt-showcaser`, `songs`, `Spools`, `Zentry` |
| Motion / Framer Motion | `card`, `Code-Vault`, `devndez`, `HackShastra1`, `HackShastra2.0`, `ochi-clone`, `Portfolio-2.0`, `Refokus`, `Resumify`, `shirt-showcaser`, `Spools`, `Strot`, `Unoverse`, `Wastify` |
| Next.js | `4th-Dimension`, `Baithak`, `Code-Vault`, `devndez`, `HackShastra2.0`, `Pen-Brawl`, `PitchDeck`, `Portfolio-2.0`, `Samyoj`, `Strot`, `todo-list`, `Unoverse`, `Wastify` |
| Lucide React | `Baithak`, `Code-Vault`, `devndez`, `HackShastra2.0`, `IPL-Score-Predictor`, `Pen-Brawl`, `PitchDeck`, `Portfolio-2.0`, `Samyoj`, `Strot`, `Unoverse`, `Wastify` |
| React Icons | `book-store-website`, `card`, `Edusavvy`, `HackShastra1`, `HackShastra2.0`, `HRMS`, `ochi-clone`, `Portfolio-2.0`, `Refokus`, `songs`, `Spools`, `Zentry` |
| TypeScript | `4th-Dimension`, `Baithak`, `devndez`, `HackShastra2.0`, `Pen-Brawl`, `PitchDeck`, `Portfolio-2.0`, `Resumify`, `Samyoj`, `Strot`, `Unoverse`, `Wastify` |
| GSAP | `Apple-iPhone15`, `GSAP`, `HackShastra1`, `HackShastra2.0`, `obys-agency`, `ochi-clone`, `Password-Generator`, `Portfolio-2.0`, `Resumify`, `Squid-Game`, `Zentry` |
| React Router | `book-store-website`, `Cinefy`, `Edusavvy`, `HRMS`, `Portfolio`, `react-api-project`, `Resumify`, `Routing`, `Spools` |
| clsx | `Baithak`, `devndez`, `HackShastra2.0`, `Pen-Brawl`, `PitchDeck`, `Resumify`, `Samyoj`, `Wastify` |
| Tailwind Merge | `Baithak`, `devndez`, `HackShastra2.0`, `Pen-Brawl`, `PitchDeck`, `Resumify`, `Samyoj`, `Wastify` |
| Three.js | `3d-Cube`, `3D-Robo`, `4th-Dimension`, `obys-agency`, `Pen-Brawl`, `Portfolio-2.0`, `shirt-showcaser`, `Unoverse` |
| Express | `book-store-website`, `HRMS`, `InstaClone`, `Pinterest`, `Sabu`, `Spools`, `Unoverse` |
| globals | `book-store-website`, `Edusavvy`, `HackShastra1`, `IPL-Score-Predictor`, `shirt-showcaser`, `Spools`, `Zentry` |
| Drei | `4th-Dimension`, `Apple-iPhone15`, `Pen-Brawl`, `Portfolio`, `shirt-showcaser`, `Unoverse` |
| Mongoose | `book-store-website`, `HRMS`, `InstaClone`, `Pinterest`, `Spools`, `Strot` |
| React Three Fiber | `4th-Dimension`, `Apple-iPhone15`, `Pen-Brawl`, `Portfolio`, `shirt-showcaser`, `Unoverse` |
| Class Variance Authority | `Baithak`, `HackShastra2.0`, `PitchDeck`, `Samyoj`, `Wastify` |
| JSON Web Token | `book-store-website`, `HRMS`, `Spools`, `Strot`, `Unoverse` |
| multer | `book-store-website`, `HRMS`, `InstaClone`, `Pinterest`, `Spools` |
| Axios | `book-store-website`, `Cinefy`, `HRMS`, `react-api-project` |
| bcryptjs | `book-store-website`, `HRMS`, `Spools`, `Strot` |
| cookie-parser | `HRMS`, `InstaClone`, `Pinterest`, `Spools` |
| dotenv | `book-store-website`, `HRMS`, `Pinterest`, `Spools` |
| Google Fonts | `Neumorphic-Calculator`, `premier`, `Squid-Game`, `Zenzone` |
| Radix UI | `Baithak`, `PitchDeck`, `Samyoj`, `Wastify` |
| React Hook Form | `book-store-website`, `Portfolio-2.0`, `Samyoj`, `songs` |
| Remix Icon | `obys-agency`, `premier`, `tailwind`, `Zenzone` |
| Tailwind CSS Animate | `Baithak`, `PitchDeck`, `Samyoj`, `Wastify` |
| Cloudinary | `book-store-website`, `Portfolio-2.0`, `Spools` |
| cors | `book-store-website`, `HRMS`, `Unoverse` |
| Locomotive Scroll | `obys-agency`, `ochi-clone`, `Refokus` |
| MongoDB driver | `HackShastra2.0`, `Pinterest`, `Portfolio-2.0` |
| Nodemon | `book-store-website`, `HRMS`, `Spools` |
| Socket.IO | `Pen-Brawl`, `Spools`, `Unoverse` |
| TW Animate CSS | `HackShastra2.0`, `Resumify`, `Samyoj` |
| Vercel Analytics | `HackShastra2.0`, `Portfolio-2.0`, `Unoverse` |
| Zod | `Portfolio-2.0`, `Samyoj`, `Unoverse` |
| bcrypt | `book-store-website`, `HRMS` |
| Clerk | `Baithak`, `Wastify` |
| debug | `InstaClone`, `Pinterest` |
| EJS | `InstaClone`, `Pinterest` |
| express-session | `InstaClone`, `Pinterest` |
| Font Awesome | `Password-Generator`, `Zenzone` |
| helmet | `book-store-website`, `Spools` |
| Hook Form resolvers | `Portfolio-2.0`, `Samyoj` |
| http-errors | `InstaClone`, `Pinterest` |
| jQuery | `HRMS`, `obys-agency` |
| Lenis | `HackShastra2.0`, `Portfolio-2.0` |
| morgan | `InstaClone`, `Pinterest` |
| next-themes | `HackShastra2.0`, `Samyoj` |
| Nodemailer | `book-store-website`, `HRMS` |
| ogl | `Portfolio-2.0`, `Resumify` |
| Passport | `InstaClone`, `Pinterest` |
| React Chart.js | `book-store-website`, `HRMS` |
| react-datepicker | `Baithak`, `HRMS` |
| react-toastify | `book-store-website`, `HRMS` |
| Recharts | `Code-Vault`, `IPL-Score-Predictor` |
| Redux | `Cinefy`, `HRMS` |
| tsx | `Pen-Brawl`, `Portfolio-2.0` |
| uuid | `InstaClone`, `Pinterest` |
| Zustand | `Resumify`, `Unoverse` |
| @popperjs/core | `HRMS` |
| @use-gesture/react | `HackShastra2.0` |
| Animate.css | `obys-agency` |
| Anime.js | `Portfolio-2.0` |
| baseline-browser-mapping | `HackShastra2.0` |
| body-parser | `book-store-website` |
| Bootstrap | `HRMS` |
| canvas-confetti | `Pen-Brawl` |
| Chainlink Contracts | `Wastify` |
| Chakra UI | `Spools` |
| Chart.js | `HRMS` |
| classnames | `Refokus` |
| cobe | `Wastify` |
| compression | `Unoverse` |
| concurrently | `Pen-Brawl` |
| connect-flash | `Pinterest` |
| connect-mongo | `Pinterest` |
| ControlKit | `obys-agency` |
| Create React App | `HRMS` |
| cron | `Spools` |
| cross-env | `Spools` |
| date-fns | `Spools` |
| dayjs | `Samyoj` |
| Drizzle | `Wastify` |
| EmailJS | `Portfolio` |
| Emotion | `Spools` |
| ethers.js | `Wastify` |
| express-fileupload | `Spools` |
| express-rate-limit | `book-store-website` |
| express-validator | `book-store-website` |
| Google Generative AI SDK | `Wastify` |
| Hardhat | `Wastify` |
| ioredis | `Unoverse` |
| isbot | `Resumify` |
| JOSE | `Portfolio-2.0` |
| LayerZero | `Wastify` |
| Leaflet | `Wastify` |
| Lettering.js | `obys-agency` |
| Lit Protocol | `Wastify` |
| maath | `shirt-showcaser` |
| markdown-it | `PitchDeck` |
| Materialize | `HRMS` |
| moment | `HRMS` |
| nanoid | `Portfolio-2.0` |
| Neon | `Wastify` |
| NextAuth.js | `PitchDeck` |
| OpenZeppelin Contracts | `Wastify` |
| path | `book-store-website` |
| PDF.js | `Resumify` |
| Postgres.js | `Wastify` |
| postprocessing | `Unoverse` |
| Prettier | `Portfolio-2.0` |
| qrcode | `Sabu` |
| qrcode-terminal | `Sabu` |
| Rapier | `Pen-Brawl` |
| React Google Maps | `Wastify` |
| React Leaflet | `Wastify` |
| React Spring Three | `Portfolio` |
| React Three Postprocessing | `Unoverse` |
| React Three Rapier | `Pen-Brawl` |
| react-color | `shirt-showcaser` |
| react-dropzone | `Resumify` |
| react-hot-toast | `Wastify` |
| react-infinite-scroll-component | `Cinefy` |
| react-player | `Cinefy` |
| react-vertical-timeline-component | `Portfolio` |
| Recoil | `Spools` |
| Resend | `Strot` |
| Sanity | `PitchDeck` |
| server-only | `PitchDeck` |
| Shery.js | `obys-agency` |
| Sign Protocol | `Wastify` |
| Solidity Coverage | `Wastify` |
| sonner | `Samyoj` |
| Stream | `Baithak` |
| Styled Components | `PitchDeck` |
| sweetalert | `HRMS` |
| swiper | `book-store-website` |
| Testing Library | `HRMS` |
| Textillate | `obys-agency` |
| ts-node-dev | `Unoverse` |
| tsParticles | `Squid-Game` |
| TypeChain | `Wastify` |
| validator | `HRMS` |
| Valtio | `shirt-showcaser` |
| Viem | `Wastify` |
| Vitest | `Unoverse` |
| web-vitals | `HRMS` |
| Web3Auth | `Wastify` |
| whatsapp-web.js | `Sabu` |
| Workbox | `Spools` |
| Workspace package: backend | `Spools` |

</details>

The [machine-readable audit](../data/technologies.json) includes counts, repository membership, measurement definitions, and GitHub source URLs. The [repository metadata snapshot](../data/repository-metrics.json) records the eligible set. The scheduled workflow rescans complete repository trees and immutable manifest blobs, then rebuilds the graphs and this inventory.
