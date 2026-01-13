# Guide: Importing Code from Your Server to GitHub

This guide will help you import your existing code from your server into this GitHub repository.

## Prerequisites

- Git installed on your server
- Access to your server (SSH or direct access)
- Your code files on the server

## Method 1: Direct Git Push (Recommended)

If you have direct access to your server and want to maintain git history:

### Step 1: Navigate to Your Code Directory on the Server

```bash
cd /path/to/your/code
```

### Step 2: Initialize Git (if not already a git repository)

```bash
git init
```

### Step 3: Add All Your Files

```bash
git add .
```

### Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Import existing code from server"
```

### Step 5: Add GitHub Remote

```bash
git remote add origin https://github.com/ReinVelt/velt.org.git
```

### Step 6: Pull Existing Files (README, LICENSE)

⚠️ **Warning**: This step may create merge conflicts if you have files with the same names (e.g., README.md). Consider backing up your files before proceeding.

```bash
git pull origin main --allow-unrelated-histories
```

Or if you're on a different branch (replace `<branch-name>` with your actual branch name, e.g., `develop` or `staging`):

```bash
git pull origin <branch-name> --allow-unrelated-histories
```

### Step 7: Resolve Any Conflicts

If there are conflicts (e.g., with README.md), resolve them and commit:

```bash
git add .
git commit -m "Merge server code with GitHub repository"
```

### Step 8: Push Your Code

```bash
git push origin main
```

Or push to your current branch (replace `<branch-name>` with your actual branch name):

```bash
git push origin <branch-name>
```

## Method 2: Download and Upload

If you don't have git on your server or prefer a simpler approach:

### Step 1: Download Your Code from the Server

Using SCP:
```bash
scp -r username@your-server:/path/to/your/code /local/destination
```

Or using SFTP, rsync, or your hosting provider's file manager.

### Step 2: Clone This Repository Locally

```bash
git clone https://github.com/ReinVelt/velt.org.git
cd velt.org
```

### Step 3: Copy Your Code Files

```bash
cp -r /local/destination/* .
```

Make sure not to overwrite important files like LICENSE if you want to keep them.

### Step 4: Add and Commit

```bash
git add .
git commit -m "Import code from server"
```

### Step 5: Push to GitHub

```bash
git push origin main
```

## Method 3: Using GitHub Web Interface

For small projects with few files:

1. Navigate to your repository on GitHub: https://github.com/ReinVelt/velt.org
2. Click "Add file" → "Upload files"
3. Drag and drop your files or folders
4. Add a commit message: "Import code from server"
5. Click "Commit changes"

## Method 4: Using GitHub Desktop

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Clone this repository using GitHub Desktop
3. Copy your code files into the cloned repository folder
4. GitHub Desktop will automatically detect the changes
5. Add a commit message and commit
6. Click "Push origin" to upload to GitHub

## Post-Import Checklist

After importing your code, consider:

- [ ] Add/update `.gitignore` file for your project type
- [ ] Update `README.md` with project description, setup instructions, etc.
- [ ] Add documentation for your code
- [ ] Set up CI/CD if needed
- [ ] Review and remove any sensitive data (passwords, API keys, etc.)
- [ ] Add appropriate license information if needed

## Common Issues

### "Permission denied" when pushing

Make sure you have:
- Correct repository permissions
- Properly configured SSH keys or personal access token
- Correct remote URL

### "Nothing to commit" message

Make sure your files aren't being ignored by a `.gitignore` file. Check with:
```bash
git status --ignored
```

### Large files (>100MB)

GitHub has a file size limit. For large files, consider:
- Using [Git LFS](https://git-lfs.github.com/)
- Storing large files elsewhere (cloud storage, CDN)
- Compressing or optimizing the files

## Need Help?

If you encounter issues:
1. Check GitHub's official documentation: https://docs.github.com
2. Open an issue in this repository
3. Check your git configuration: `git config --list`

## Security Reminder

⚠️ **Important**: Before pushing, make sure you:
- Remove any passwords, API keys, or sensitive credentials
- Add sensitive files to `.gitignore`
- Don't commit environment files with secrets (`.env` files)
- Review your commit history for accidentally committed secrets
