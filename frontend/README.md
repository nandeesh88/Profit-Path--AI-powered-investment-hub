# Frontend - Profit Path

This is the Next.js/React frontend for the Profit Path FinTech SaaS platform.

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout wrapper
│   ├── page.tsx                 # Home page
│   ├── globals.css              # Global styles
│   ├── dashboard/               # Dashboard page
│   ├── expenses/                # Expenses page
│   ├── goals/                   # Goals page
│   ├── investments/             # Investments page
│   ├── login/                   # Login page
│   ├── onboarding/              # Onboarding page
│   └── signup/                  # Signup page
│
├── components/                   # React Components
│   ├── auth/
│   │   ├── login-form.tsx       # Login form component
│   │   ├── signup-form.tsx      # Signup form component
│   │   └── profile-setup.tsx    # Profile setup component
│   ├── dashboard/
│   │   ├── sidebar.tsx          # Dashboard sidebar
│   │   ├── budget-tracker.tsx   # Budget tracking component
│   │   ├── expense-chart.tsx    # Expense visualization
│   │   ├── trend-chart.tsx      # Trend analysis chart
│   │   └── kpi-card.tsx         # KPI display card
│   ├── expenses/
│   │   ├── add-expense-form.tsx # Add expense form
│   │   └── expense-list.tsx     # Expense listing
│   ├── goals/
│   │   ├── add-goal-form.tsx    # Add goal form
│   │   └── goal-card.tsx        # Goal display card
│   ├── investments/
│   │   ├── investment-card.tsx  # Investment option card
│   │   └── investment-recommendation.tsx  # AI recommendations
│   ├── ui/                      # Base UI components (shadcn/ui)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── dialog.tsx
│   │   └── ... (other UI components)
│   ├── protected-route.tsx      # Protected route wrapper
│   └── theme-provider.tsx       # Theme/dark mode provider
│
├── hooks/                        # Custom React Hooks
│   ├── use-mobile.ts            # Mobile detection hook
│   └── use-toast.ts             # Toast notification hook
│
├── lib/                          # Utility Functions
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Authentication utilities
│   ├── auth-context.tsx         # Auth context provider
│   └── utils.ts                 # General utilities
│
├── public/                       # Static Assets
│   ├── placeholder-logo.svg     # Logo
│   ├── placeholder-user.jpg     # User avatar placeholder
│   └── ... (other images)
│
├── styles/                       # Global Stylesheets
│   └── globals.css              # Global CSS
│
├── package.json                 # Dependencies
├── tsconfig.json                # TypeScript config
├── next.config.mjs              # Next.js config
├── postcss.config.mjs           # PostCSS config
├── components.json              # Component library config
└── next-env.d.ts                # Next.js type definitions
```

## Technology Stack

- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Utility-first CSS
- **shadcn/ui** - Reusable component library
- **Recharts** - Data visualization
- **React Hook Form** - Form management
- **Zod** - Schema validation

## Setup & Development

### Installation

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run start
```

### Lint Code

```bash
npm run lint
```

## Key Features

### Authentication
- Login/Signup pages with form validation
- Session-based authentication
- Protected routes with automatic redirects
- Profile setup after signup

### Dashboard
- Overview of financial KPIs
- Visual charts and analytics
- Budget tracking
- Trend analysis

### Expense Tracking
- Add/edit/delete expenses
- Category-based organization
- Summary statistics
- Monthly expense reports

### Investment Hub
- Browse investment options
- Filter by risk level
- AI-powered recommendations
- Expected returns visualization

### Goal Planning
- Create and track financial goals
- Progress monitoring
- Priority categorization
- Goal recommendations

## Component Architecture

All components follow these principles:
- **Composition** - Components are built from smaller, reusable pieces
- **Props-based** - Configuration through props
- **TypeScript** - Full type safety
- **Accessibility** - WCAG compliant
- **Responsive** - Mobile-first design

## State Management

- **React Context API** - For authentication state
- **Component State** - Local state with hooks
- **Custom Hooks** - Reusable logic extraction

## API Integration

Frontend communicates with backend via:
- Base URL: `http://localhost:8000/api/v1`
- Authentication: JWT tokens
- CORS: Configured for localhost development

See `lib/api.ts` for API client configuration.

## Styling

- Tailwind CSS utility classes
- Custom CSS in `styles/globals.css`
- Dark mode support via theme context
- Glassmorphism design aesthetic

## Performance & Optimization

- Next.js image optimization
- Code splitting
- CSS purging
- Tree-shaking enabled

## Contributing

When adding new components:
1. Create in appropriate folder under `components/`
2. Use TypeScript for type safety
3. Follow existing naming conventions
4. Add proper prop types
5. Include JSDoc comments for public components

## Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### Build errors
```bash
rm -rf .next
npm install
npm run build
```

### Type errors
```bash
npm run lint
```
