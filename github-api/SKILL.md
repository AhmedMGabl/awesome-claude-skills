---
name: github-api
description: GitHub API integration covering REST and GraphQL APIs, Octokit client, repository management, pull request automation, issue workflows, GitHub Apps authentication, webhook handling, Actions API, release management, and code search with the GitHub API.
---

# GitHub API

This skill should be used when integrating with the GitHub API. It covers REST/GraphQL APIs, Octokit, webhooks, GitHub Apps, and automation workflows.

## When to Use This Skill

Use this skill when you need to:

- Automate repository and PR workflows
- Build GitHub Apps or integrations
- Handle GitHub webhooks
- Query repositories with the GraphQL API
- Manage releases and deployments programmatically

## Octokit REST Client

```typescript
import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

// List repositories
const { data: repos } = await octokit.repos.listForAuthenticatedUser({
  sort: "updated",
  per_page: 30,
});

// Create a pull request
const { data: pr } = await octokit.pulls.create({
  owner: "org",
  repo: "repo",
  title: "feat: add new feature",
  body: "## Summary\n\nAdds the new feature.",
  head: "feature-branch",
  base: "main",
});

// Add reviewers
await octokit.pulls.requestReviewers({
  owner: "org",
  repo: "repo",
  pull_number: pr.number,
  reviewers: ["reviewer1"],
});

// Create an issue
const { data: issue } = await octokit.issues.create({
  owner: "org",
  repo: "repo",
  title: "Bug: login fails on mobile",
  body: "Steps to reproduce...",
  labels: ["bug", "priority:high"],
  assignees: ["developer1"],
});
```

## GraphQL API

```typescript
import { graphql } from "@octokit/graphql";

const graphqlWithAuth = graphql.defaults({
  headers: { authorization: `token ${process.env.GITHUB_TOKEN}` },
});

const { repository } = await graphqlWithAuth(`
  query ($owner: String!, $repo: String!, $number: Int!) {
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
            commit { statusCheckRollup { state } }
          }
        }
      }
    }
  }
`, { owner: "org", repo: "repo", number: 123 });
```

## GitHub App Authentication

```typescript
import { createAppAuth } from "@octokit/auth-app";

const auth = createAppAuth({
  appId: process.env.GITHUB_APP_ID!,
  privateKey: process.env.GITHUB_APP_PRIVATE_KEY!,
  installationId: Number(process.env.GITHUB_INSTALLATION_ID),
});

const { token } = await auth({ type: "installation" });
const octokit = new Octokit({ auth: token });
```

## Webhook Handler

```typescript
import { Webhooks } from "@octokit/webhooks";

const webhooks = new Webhooks({ secret: process.env.WEBHOOK_SECRET! });

webhooks.on("pull_request.opened", async ({ payload }) => {
  const { pull_request, repository } = payload;
  await octokit.pulls.requestReviewers({
    owner: repository.owner.login,
    repo: repository.name,
    pull_number: pull_request.number,
    reviewers: ["lead-dev"],
  });
});

webhooks.on("issues.opened", async ({ payload }) => {
  const labels: string[] = [];
  if (payload.issue.title.toLowerCase().includes("bug")) labels.push("bug");
  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      issue_number: payload.issue.number,
      labels,
    });
  }
});
```

## Release Management

```typescript
const { data: release } = await octokit.repos.createRelease({
  owner: "org",
  repo: "repo",
  tag_name: "v1.2.0",
  name: "Release v1.2.0",
  body: "## What's Changed\n\n- Feature A\n- Bug fix B",
  generate_release_notes: true,
});
```

## Additional Resources

- GitHub REST API: https://docs.github.com/en/rest
- GitHub GraphQL: https://docs.github.com/en/graphql
- Octokit: https://github.com/octokit/octokit.js
