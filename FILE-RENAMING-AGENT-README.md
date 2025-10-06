# 🗂️ File & Folder Renaming Agent

An intelligent Cursor AI agent designed to clean up messy file and folder structures by applying industry-standard naming conventions automatically.

## 🎯 Purpose

Transform chaotic file/folder names into clean, consistent, and professional structures that follow best practices for different programming languages and project types.

## ✨ Features

- **Smart Analysis**: Automatically detects project type and current naming patterns
- **Descriptive Naming**: Transforms generic names into self-documenting, purpose-driven names
- **Multi-Language Support**: Applies appropriate conventions for Python, JavaScript, TypeScript, etc.
- **Safe Operations**: Generates backup and rollback commands
- **Batch Processing**: Handles multiple files/folders efficiently
- **Conflict Detection**: Identifies potential naming conflicts before execution
- **Best Practices**: Follows industry standards for naming conventions
- **Self-Documenting**: Creates names that explain functionality without needing comments

## 🚀 Quick Start

### 1. Setup in Cursor

1. Copy the system prompt from `cursor-file-renaming-agent-prompt.md`
2. Open Cursor IDE
3. Go to Settings → AI → Custom Instructions
4. Paste the system prompt
5. Save and restart Cursor

### 2. Basic Usage

Simply describe your messy file structure to the agent:

```
"My folders are named 'My Project Files', 'Utils & Helpers', 'API_STUFF' and I have files like 'myComponent.JS', 'config file.json', 'handler.py'"
```

The agent will provide:
- Analysis of current issues and vague naming
- Descriptive naming recommendations based on file content/purpose
- Safe rename commands with clear functionality names
- Rollback instructions

## 📋 Naming Conventions Supported

### Folder Naming

| Project Type | Convention | Example |
|--------------|------------|---------|
| General | kebab-case | `my-project-folder` |
| Python | snake_case | `my_python_module` |
| React/Components | PascalCase | `MyReactComponent` |
| System/Config | lowercase | `config`, `utils`, `assets` |

### File Naming

| File Type | Convention | Example |
|-----------|------------|---------|
| Python | snake_case.py | `user_authentication_service.py` |
| JavaScript | camelCase.js | `emailValidationUtils.js` |
| TypeScript | camelCase.ts | `paymentProcessingService.ts` |
| React Components | PascalCase.tsx | `UserProfileCard.tsx` |
| Config Files | kebab-case.ext | `database-connection-config.json` |
| Test Files | descriptive.test.ext | `userAuthentication.test.js` |

## 🎯 Descriptive Naming Philosophy

### ❌ Avoid Generic Names
```
utils/           → data-processing-utilities/
helpers/         → form-validation-helpers/
components/      → user-interface-components/
file.js         → userRegistrationService.js
handler.py      → videoUploadHandler.py
config.json     → api-endpoint-config.json
```

### ✅ Use Purpose-Driven Names
```
user-authentication-system/     # Handles login/signup
video-processing-engine/        # Processes uploaded videos
email-notification-service/     # Sends automated emails
payment-gateway-integration/    # Handles payment processing

calculateMonthlyRevenue.js      # Calculates monthly revenue
validateEmailAddress.py         # Validates email format
generatePdfReport.js           # Generates PDF reports
processVideoUpload.py          # Handles video uploads
```

## 🛡️ Safety Features

### Backup Strategy
```bash
# Automatic backup creation
cp -r . ../backup-$(date +%Y%m%d-%H%M%S)
```

### Conflict Prevention
- Checks for existing files before renaming
- Warns about potential overwrites
- Suggests alternative names for conflicts

### Rollback Support
```bash
# Example rollback commands provided
mv "new-name" "old name"  # Restore original names
```

## 📖 Usage Examples

### Example 1: Python Project Cleanup

**Input Structure:**
```
My Python Project/
├── Utils & Helpers/
├── API Calls/
├── myModule.PY
└── Config File.json
```

**Agent Response:**
```bash
# Rename folders with descriptive purposes
mv "My Python Project" "video_processing_system"
mv "Utils & Helpers" "data_validation_utilities"
mv "API Calls" "external_api_services"

# Rename files with clear functionality
mv "myModule.PY" "video_compression_handler.py"
mv "Config File.json" "database_connection_config.json"
```

### Example 2: React Project Cleanup

**Input Structure:**
```
my react app/
├── components & stuff/
├── myComponent.JS
├── another component.tsx
└── app config.json
```

**Agent Response:**
```bash
# Rename folders with descriptive purposes
mv "my react app" "user-management-dashboard"
mv "components & stuff" "user-interface-components"

# Rename files with clear functionality
mv "myComponent.JS" "UserProfileCard.js"
mv "another component.tsx" "EmailNotificationPanel.tsx"
mv "app config.json" "api-endpoint-configuration.json"
```

## 🔧 Advanced Features

### Batch Operations
```bash
# Process multiple files at once
for file in *.JS; do
  mv "$file" "${file%.JS}.js"
done
```

### Pattern Recognition
- Detects camelCase, PascalCase, snake_case, kebab-case
- Identifies file types and purposes
- Suggests appropriate conventions

### Dependency Checking
- Warns about import statements that may break
- Identifies configuration files that reference renamed items
- Suggests post-rename verification steps

## 🎨 Customization

### Custom Naming Rules

You can extend the agent with custom rules:

```markdown
## Custom Rules for My Project
- Database files: `db_*.sql`
- Migration files: `YYYY_MM_DD_description.sql`
- Component tests: `ComponentName.spec.tsx`
```

### Project-Specific Conventions

```markdown
## Project: E-commerce Platform
- API routes: `api-route-name.js`
- Database models: `ModelName.model.js`
- Middleware: `middleware-name.middleware.js`
```

## 🚨 Common Issues & Solutions

### Issue: Special Characters in Names
```bash
# Problem: "File & Folder"
# Solution: "file-folder"
mv "File & Folder" "file-folder"
```

### Issue: Mixed Case Extensions
```bash
# Problem: "script.JS"
# Solution: "script.js"
mv "script.JS" "script.js"
```

### Issue: Spaces in Names
```bash
# Problem: "My File Name.txt"
# Solution: "my-file-name.txt"
mv "My File Name.txt" "my-file-name.txt"
```

## 📊 Best Practices Checklist

- [ ] **No spaces** in file/folder names
- [ ] **Consistent case** throughout project
- [ ] **Descriptive names** that clearly explain functionality
- [ ] **Self-documenting** - purpose obvious from name alone
- [ ] **Avoid generic terms** like "utils", "helpers", "stuff"
- [ ] **Include action/purpose** in names when applicable
- [ ] **Proper extensions** for all files
- [ ] **Language-specific** conventions followed
- [ ] **No special characters** except `-` and `_`
- [ ] **Reasonable length** (descriptive but not excessive)
- [ ] **Context-aware** naming with domain relevance
- [ ] **Version control** friendly names

## 🔄 Workflow Integration

### Git Integration
```bash
# Before renaming
git add .
git commit -m "Backup before file renaming"

# After renaming
git add .
git commit -m "Apply consistent naming conventions"
```

### CI/CD Considerations
- Update build scripts after renaming
- Check deployment configurations
- Verify import paths in code

## 🆘 Troubleshooting

### Common Problems

1. **Permission Denied**
   ```bash
   sudo mv "old name" "new-name"  # Use with caution
   ```

2. **File in Use**
   ```bash
   # Close applications using the file first
   lsof "filename"  # Check what's using the file
   ```

3. **Path Too Long**
   ```bash
   # Shorten intermediate folder names first
   mv "very-long-folder-name" "short-name"
   ```

## 📈 Performance Tips

- **Process in batches** for large directories
- **Use wildcards** for similar files
- **Test on small sets** first
- **Monitor system resources** during bulk operations

## 🤝 Contributing

To improve the agent:

1. Add new naming conventions
2. Enhance language-specific rules
3. Improve safety checks
4. Add more file type recognition

## 📄 License

This agent configuration is open source and can be modified for your specific needs.

---

**Happy Organizing! 🎉**

Transform your messy file structures into clean, professional, and maintainable codebases with this intelligent renaming agent.
