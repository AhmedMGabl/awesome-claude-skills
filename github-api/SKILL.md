---
name: github-api
description: GitHub API integration covering Octokit client, REST and GraphQL APIs, repository management, pull request automation, GitHub Actions workflow dispatch, webhook handling, GitHub Apps authentication, release management, and issue/project board automation patterns.
---

# GitHub API Integration

This skill should be used when automating GitHub workflows, building GitHub integrations, or interacting with the GitHub API programmatically. It covers Octokit, webhooks, GitHub Apps, and CI automation.

## When to Use This Skill

Use this skill when you need to:

- Automate pull request workflows
- Build GitHub integrations or bots
- Manage repositories programmatically
- Handle GitHub webhooks
- Create GitHub Actions with API calls
- Automate release management

## Octokit REST API

```typescript
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const owner = "myorg";
const repo = "myrepo";

// List pull requests
const { data: pulls } = await octokit.rest.pulls.list({
  owner, repo, state: "open", sort: "updated", direction: "desc", per_page: 30,
});

// Create a pull request
const { data: pr } = await octokit.rest.pulls.create({
  owner, repo,
  title: "feat: Add new feature",
  body: "## Summary\n\n- Added feature X\n- Updated docs",
  head: "feature/new-feature",
  base: "main",
});

// Add labels and reviewers
await octokit.rest.issues.addLabels({ owner, repo, issue_number: pr.number, labels: ["enhancement"] });
await octokit.rest.pulls.requestReviewers({ owner, repo, pull_number: pr.number, reviewers: ["teammate"] });

// Create a comment on a PR
await octokit.rest.issues.createComment({
  owner, repo, issue_number: pr.number,
  body: "Automated check passed. Ready for review.",
});

// Merge a pull request
await octokit.rest.pulls.merge({
  owner, repo, pull_number: pr.number, merge_method: "squash",
});
```

## GraphQL API

```typescript
import { graphql } from "@octokit/graphql";

const gql = graphql.defaults({ headers: { authorization: `token ${process.env.GITHUB_TOKEN}` } });

// Get PR with reviews and checks
const { repository } = await gql(`
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        title
        state
        mergeable
        reviews(last: 10) {
          nodes { author { login } state body }
        }
        commits(last: 1) {
          nodes {
            commit {
              statusCheckRollup {
                state
                contexts(first: 20) {
                  nodes {
                    ... on CheckRun { name conclusion }
                    ... on StatusContext { context state }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
`, { owner, repo, number: 42 });
```

## Webhook Handler

```typescript
import { Webhooks, createNodeMiddleware } from "@octokit/webhooks";

const webhooks = new Webhooks({ secret: process.env.GITHUB_WEBHOOK_SECRET! });

// Pull request opened
webhooks.on("pull_request.opened", async ({ payload }) => {
  const { pull_request: pr, repository } = payload;

  // Auto-assign reviewer based on files changed
  if (pr.changed_files > 0) {
    await octokit.rest.pulls.requestReviewers({
      owner: repository.owner.login,
      repo: repository.name,
      pull_number: pr.number,
      reviewers: getReviewersForPR(pr),
    });
  }

  // Add size label
  const sizeLabel = pr.additions + pr.deletions < 50 ? "size/S"
    : pr.additions + pr.deletions < 200 ? "size/M" : "size/L";
  await octokit.rest.issues.addLabels({
    owner: repository.owner.login,
    repo: repository.name,
    issue_number: pr.number,
    labels: [sizeLabel],
  });
});

// Issue commented
webhooks.on("issue_comment.created", async ({ payload }) => {
  const { comment, issue } = payload;
  if (comment.body.includes("/deploy") && issue.pull_request) {
    await triggerDeployment(payload);
  }
});

// Check run completed
webhooks.on("check_run.completed", async ({ payload }) => {
  if (payload.check_run.conclusion === "failure") {
    await notifyTeam(payload);
  }
});

// Express middleware
app.use("/api/webhooks/github", createNodeMiddleware(webhooks));
```

## Release Automation

```typescript
// Create a release with auto-generated notes
async function createRelease(tag: string) {
  const { data: release } = await octokit.rest.repos.createRelease({
    owner, repo,
    tag_name: tag,
    name: tag,
    generate_release_notes: true,
    draft: false,
    prerelease: tag.includes("-rc") || tag.includes("-beta"),
  });

  return release;
}

// Upload release assets
async function uploadAsset(releaseId: number, filePath: string) {
  const fs = await import("fs");
  const path = await import("path");

  const data = fs.readFileSync(filePath);
  await octokit.rest.repos.uploadReleaseAsset({
    owner, repo, release_id: releaseId,
    name: path.basename(filePath),
    data: data as unknown as string,
  });
}
```

## GitHub Actions Workflow Dispatch

```typescript
// Trigger a workflow from code
await octokit.rest.actions.createWorkflowDispatch({
  owner, repo,
  workflow_id: "deploy.yml",
  ref: "main",
  inputs: {
    environment: "production",
    version: "1.2.3",
  },
});

// List workflow runs
const { data: runs } = await octokit.rest.actions.listWorkflowRuns({
  owner, repo, workflow_id: "ci.yml", branch: "main", status: "completed", per_page: 5,
});
```

## GitHub App Authentication

```typescript
import { createAppAuth } from "@octokit/auth-app";

const appOctokit = new Octokit({
  authStrategy: createAppAuth,
  auth: {
    appId: process.env.GITHUB_APP_ID!,
    privateKey: process.env.GITHUB_APP_PRIVATE_KEY!,
    installationId: process.env.GITHUB_INSTALLATION_ID!,
  },
});

// Now use appOctokit for API calls with app permissions
const { data: repos } = await appOctokit.rest.apps.listReposAccessibleToInstallation();
```

## Additional Resources

- Octokit.js: https://github.com/octokit/octokit.js
- GitHub REST API: https://docs.github.com/en/rest
- GitHub GraphQL API: https://docs.github.com/en/graphql
- GitHub Apps: https://docs.github.com/en/apps
- Webhooks events: https://docs.github.com/en/webhooks/webhook-events-and-payloads
