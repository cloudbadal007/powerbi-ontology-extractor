# Publish to GitHub - Quick Guide

Follow these steps to publish PowerBI Ontology Extractor to your GitHub account: [cloudbadal007](https://github.com/cloudbadal007)

## Step 1: Create Repository on GitHub (2 minutes)

1. Go to: **https://github.com/new**
2. **Repository name**: `powerbi-ontology-extractor`
3. **Description**: `Transform 20 million Power BI dashboards into AI-ready ontologies`
4. **Visibility**: Public
5. **Do NOT** check "Add a README file" (you already have one)
6. Click **Create repository**

## Step 2: Open Terminal in Project Folder

Open PowerShell or Command Prompt and run:

```powershell
cd D:\AIPoCFreshApproach\powerbi-ontology-extractor
```

## Step 3: Initialize Git and Push (Copy & Paste)

Run these commands one by one:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial release: PowerBI Ontology Extractor v0.1.0"

# Add your GitHub repository as remote
git remote add origin https://github.com/cloudbadal007/powerbi-ontology-extractor.git

# Set main branch and push
git branch -M main
git push -u origin main

# Create release tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial release"
git push origin v0.1.0
```

## Step 4: Configure Repository (Optional)

After pushing, on GitHub:

1. **Settings** → **General** → Set default branch to `main`
2. **About** section → Add topics: `python`, `ontology`, `powerbi`, `ai`, `fabric-iq`
3. **Releases** → Create release from v0.1.0 tag

## Troubleshooting

### "Permission denied" or "Authentication failed"
- Use GitHub Personal Access Token instead of password
- Create token at: https://github.com/settings/tokens
- Use token as password when git asks

### "Repository already exists"
- The repo might already exist. Try: `git remote add origin https://github.com/cloudbadal007/powerbi-ontology-extractor.git`
- If it says "remote already exists": `git remote set-url origin https://github.com/cloudbadal007/powerbi-ontology-extractor.git`

### "Nothing to commit"
- Run `git status` to see file status
- Some files may be in `.gitignore` - that's expected

## Done!

Your project will be live at: **https://github.com/cloudbadal007/powerbi-ontology-extractor**
