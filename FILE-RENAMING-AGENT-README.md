# 🗂️ File & Folder Renaming Agent

An intelligent Cursor AI agent designed to clean up messy file and folder structures by applying industry-standard naming conventions automatically.

## 🎯 Purpose

Transform chaotic file/folder names into clean, consistent, and professional structures that follow best practices for different programming languages and project types.

## ✨ Features

- **Smart Analysis**: Automatically detects project type and current naming patterns
- **Multi-Language Support**: Applies appropriate conventions for Python, JavaScript, TypeScript, etc.
- **Safe Operations**: Generates backup and rollback commands
- **Batch Processing**: Handles multiple files/folders efficiently
- **Conflict Detection**: Identifies potential naming conflicts before execution
- **Best Practices**: Follows industry standards for naming conventions

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
"My folders are named 'My Project Files', 'Utils & Helpers', 'API_STUFF' and I have files like 'myComponent.JS', 'config file.json', 'Test File 1.py'"
```

The agent will provide:
- Analysis of current issues
- Recommended naming conventions
- Safe rename commands
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
| Python | snake_case.py | `my_module.py` |
| JavaScript | camelCase.js | `myScript.js` |
| TypeScript | camelCase.ts | `myModule.ts` |
| React Components | PascalCase.tsx | `MyComponent.tsx` |
| Config Files | kebab-case.ext | `app-config.json` |
| Test Files | test_name.test.ext | `component.test.js` |

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
# Rename folders
mv "My Python Project" "my_python_project"
mv "Utils & Helpers" "utils_helpers"
mv "API Calls" "api_calls"

# Rename files
mv "myModule.PY" "my_module.py"
mv "Config File.json" "config.json"
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
# Rename folders
mv "my react app" "my-react-app"
mv "components & stuff" "components"

# Rename files
mv "myComponent.JS" "MyComponent.js"
mv "another component.tsx" "AnotherComponent.tsx"
mv "app config.json" "app-config.json"
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
- [ ] **Descriptive names** that indicate purpose
- [ ] **Proper extensions** for all files
- [ ] **Language-specific** conventions followed
- [ ] **No special characters** except `-` and `_`
- [ ] **Reasonable length** (not too long/short)
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
