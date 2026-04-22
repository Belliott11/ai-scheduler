# GitHub Actions Workflows

This folder contains automated deployment workflows.

## deploy.yml

**Purpose**: Automatically build and deploy the frontend to GitHub Pages

**Triggers**:

- Any push to `main` branch
- Pull requests to `main` branch

**What it does**:

1. Sets up Node.js environment
2. Installs npm dependencies
3. Builds the React app with Vite
4. Deploys to GitHub Pages (on main branch pushes only)

**Status**: Check the Actions tab in your GitHub repository to see workflow runs

**Deployment time**: ~2-3 minutes

**Requirements**:

- GitHub Actions must be enabled (default)
- GitHub Pages must be configured to deploy from `gh-pages` branch
- Repository must be public (for free GitHub Pages)

## Customization

### Change base path for GitHub Pages

If your repository name is different from `ai-scheduler`, update in `deploy.yml`:

```yaml
env:
  VITE_BASE_PATH: /your-repo-name/
```

### Add backend deployment

To also deploy backend from this workflow:

1. Add a job for backend deployment
2. Add Python setup step
3. Deploy to Heroku, Railway, etc.

See DEPLOYMENT.md for manual backend deployment instructions.
