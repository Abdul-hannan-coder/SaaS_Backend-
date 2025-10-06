# 🚀 Next.js File & Folder Renaming Agent

An intelligent Cursor AI agent specifically designed for Next.js projects to clean up messy file and folder structures by applying Next.js best practices and conventions.

## 🎯 Purpose

Transform chaotic Next.js project structures into clean, SEO-friendly, and route-optimized organizations that follow Next.js App Router and Pages Router conventions.

## ✨ Features

- **Next.js Specific**: Tailored for App Router and Pages Router conventions
- **Route-Safe Renaming**: Maintains Next.js file-based routing functionality
- **SEO-Friendly URLs**: Creates readable, search-engine optimized route names
- **Component Organization**: Proper component categorization and naming
- **Import Safety**: Warns about potential import/export issues
- **Descriptive Naming**: Self-documenting file and folder names

## 🏗️ Next.js Conventions Supported

### App Router Structure (Next.js 13+)
```
app/
├── (auth)/                    # Route groups
│   ├── login/page.tsx        # /login route
│   └── register/page.tsx     # /register route
├── dashboard/
│   ├── page.tsx              # /dashboard route
│   ├── layout.tsx            # Dashboard layout
│   └── loading.tsx           # Loading UI
├── api/
│   └── users/route.ts        # API endpoint
└── globals.css               # Global styles
```

### Component Organization
```
components/
├── ui/                       # Reusable UI components
│   ├── Button.tsx
│   └── Modal.tsx
├── forms/                    # Form components
│   ├── LoginForm.tsx
│   └── ContactForm.tsx
├── layout/                   # Layout components
│   ├── Header.tsx
│   └── Footer.tsx
└── features/                 # Feature-specific components
    ├── user-profile/
    └── dashboard/
```

## 📋 Naming Conventions

### Folder Naming

| Type | Convention | Example |
|------|------------|---------|
| Route folders | kebab-case | `user-profile/`, `api-docs/` |
| Route groups | (group-name) | `(auth)/`, `(dashboard)/` |
| Component folders | PascalCase | `UserCard/`, `NavBar/` |
| Utility folders | kebab-case | `lib/`, `utils/`, `hooks/` |

### File Naming

| File Type | Convention | Example |
|-----------|------------|---------|
| Pages | page.tsx | `app/dashboard/page.tsx` |
| Layouts | layout.tsx | `app/dashboard/layout.tsx` |
| API Routes | route.ts | `app/api/users/route.ts` |
| Components | PascalCase.tsx | `UserProfileCard.tsx` |
| Hooks | usePascalCase.ts | `useUserData.ts` |
| Utils | camelCase.ts | `formatDate.ts` |

## 🚀 Quick Start

### 1. Setup in Cursor
1. Copy the system prompt from `cursor-nextjs-renaming-agent-prompt.md`
2. Open Cursor IDE
3. Go to Settings → AI → Custom Instructions
4. Paste the system prompt and save

### 2. Usage Example
```
"My Next.js project has folders like 'comp', 'pages stuff', 'api things' and files like 'card.tsx', 'form.js', 'page1.tsx'"
```

**Agent Response:**
```bash
# Rename folders
mv "comp" "components"
mv "pages stuff" "app"
mv "api things" "app/api"

# Rename files with descriptive names
mv "components/card.tsx" "components/UserProfileCard.tsx"
mv "components/form.js" "components/ContactForm.tsx"
mv "app/page1.tsx" "app/page.tsx"
```

## 📖 Transformation Examples

### Example 1: App Router Cleanup

**Before:**
```
my-app/
├── comp/
│   ├── card.tsx
│   └── form.js
├── pages stuff/
│   ├── page1.tsx
│   └── dash.tsx
└── api things/
    └── user.ts
```

**After:**
```
my-app/
├── components/
│   ├── UserProfileCard.tsx
│   └── ContactForm.tsx
├── app/
│   ├── user-profile/page.tsx
│   └── dashboard/page.tsx
└── app/api/
    └── users/route.ts
```

### Example 2: Component Organization

**Before:**
```
components/
├── comp1.tsx
├── comp2.tsx
├── form.tsx
└── modal.tsx
```

**After:**
```
components/
├── ui/
│   ├── Button.tsx
│   └── Modal.tsx
├── forms/
│   └── ContactForm.tsx
└── features/
    └── UserProfileCard.tsx
```

## 🎯 Descriptive Naming Philosophy

### ❌ Avoid Generic Names
```
comp/            → components/
pages stuff/     → app/
api things/      → app/api/
card.tsx         → UserProfileCard.tsx
form.js          → ContactForm.tsx
modal.tsx        → DeleteConfirmationModal.tsx
```

### ✅ Use Purpose-Driven Names
```
user-profile/           # User profile pages
dashboard/              # Dashboard section
contact-form/           # Contact form page
api/users/             # User API endpoints

UserRegistrationForm.tsx    # User signup form
EmailNotificationPanel.tsx  # Email notifications
PaymentProcessingModal.tsx  # Payment processing
NavigationBreadcrumbs.tsx   # Navigation breadcrumbs
```

## 🛡️ Safety Features

### Route Protection
- Maintains Next.js file-based routing
- Preserves special file names (`page.tsx`, `layout.tsx`)
- Keeps route groups and dynamic routes intact

### Import Safety
```bash
# Warns about potential import issues
# Before: import Card from './card'
# After:  import UserProfileCard from './UserProfileCard'
```

### Backup Strategy
```bash
# Automatic backup before renaming
cp -r . ../backup-$(date +%Y%m%d-%H%M%S)
```

## 🔧 Advanced Features

### Route Group Handling
```bash
# Handles route groups properly
mv "(auth)" "(authentication)"
mv "(dash)" "(dashboard)"
```

### Dynamic Route Preservation
```bash
# Preserves dynamic routes
mv "[id]" "[userId]"  # More descriptive
mv "[...slug]" "[...blogSlug]"  # Context-aware
```

### API Route Organization
```bash
# Organizes API routes logically
mv "api/user.ts" "api/users/route.ts"
mv "api/post.ts" "api/blog-posts/route.ts"
```

## 📊 Best Practices Checklist

- [ ] **Route-friendly** folder names (kebab-case)
- [ ] **SEO-optimized** URLs from folder structure
- [ ] **Descriptive component** names indicating purpose
- [ ] **Proper Next.js** special file names
- [ ] **Organized components** by category (ui, forms, features)
- [ ] **Consistent naming** across similar components
- [ ] **Import-safe** operations
- [ ] **TypeScript compatible** file extensions

## 🚨 Common Next.js Issues Fixed

### Issue: Generic Component Names
```bash
# Problem: card.tsx, form.tsx, modal.tsx
# Solution: UserProfileCard.tsx, ContactForm.tsx, DeleteModal.tsx
```

### Issue: Non-Route-Friendly Folders
```bash
# Problem: "User Profile", "API_STUFF"
# Solution: "user-profile", "api"
```

### Issue: Mixed File Extensions
```bash
# Problem: component.js in TypeScript project
# Solution: Component.tsx
```

## 🔄 Workflow Integration

### Development Workflow
```bash
# 1. Backup project
cp -r . ../backup-$(date +%Y%m%d-%H%M%S)

# 2. Run renaming commands
# (Generated by agent)

# 3. Update imports
# Search and replace in IDE

# 4. Test routing
npm run dev

# 5. Commit changes
git add .
git commit -m "Reorganize project structure with descriptive naming"
```

### Post-Rename Checklist
- [ ] Test all routes work correctly
- [ ] Update import statements
- [ ] Check TypeScript compilation
- [ ] Verify API endpoints
- [ ] Update documentation

## 🆘 Troubleshooting

### Route Not Working
```bash
# Check file structure matches Next.js conventions
app/user-profile/page.tsx  # ✅ Correct
app/user-profile.tsx       # ❌ Wrong
```

### Import Errors
```bash
# Update import paths after renaming
import UserCard from './UserProfileCard'  # Update path
```

### Build Errors
```bash
# Check for TypeScript errors
npm run build
```

## 🤝 Contributing

Enhance the agent by:
- Adding more Next.js specific patterns
- Improving route detection logic
- Adding support for new Next.js features
- Enhancing component categorization

---

**Transform your messy Next.js projects into clean, professional, and SEO-optimized structures! 🎉**
