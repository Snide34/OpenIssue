# GitHub Webhooks User Guide

## Overview

GitHub Webhooks enable OpenIssue to automatically analyze your issues and pull requests in real-time. When you create or update an issue on GitHub, OpenIssue instantly analyzes it and adds labels, priority scores, and security insights.

## Getting Started

### Step 1: Navigate to Webhook Settings

1. Log in to OpenIssue
2. Click **Settings** in the navigation bar
3. Click **Webhooks** in the navigation bar
4. You'll see the Webhook Settings page

### Step 2: Register a Webhook

1. In the "Register New Webhook" section, enter your repository name in the format: `owner/repository`
   - Example: `openissue/core`
   - Example: `facebook/react`

2. Select which events you want to monitor:
   - **Issues** - Analyze when issues are opened, edited, or reopened
   - **Pull Requests** - Analyze when PRs are opened or edited
   - **Push Events** - Monitor code pushes (optional)

3. Click **Register Webhook**

4. You'll see a success message confirming the webhook is registered

### Step 3: Verify the Webhook

1. Go to your GitHub repository settings
2. Navigate to **Settings → Webhooks**
3. You should see a webhook pointing to `https://openissue.app/webhooks/github`
4. The webhook should show a green checkmark indicating it's active

## How It Works

### Real-Time Analysis

When you create or update an issue on GitHub:

1. GitHub sends a webhook event to OpenIssue
2. OpenIssue validates the webhook signature (security)
3. OpenIssue extracts issue information
4. OpenIssue runs analysis pipeline:
   - **Classification** - Determines issue type (bug, feature, documentation, etc.)
   - **Priority Scoring** - Assigns priority level (1-10)
   - **Duplicate Detection** - Identifies similar issues
   - **Security Scanning** - Detects security vulnerabilities

5. OpenIssue applies auto-actions:
   - Adds labels (type, priority, security status)
   - Posts analysis comment with findings
   - Creates notifications for critical issues

### Example Workflow

**You create an issue on GitHub:**
```
Title: "SQL injection vulnerability in login form"
Description: "The login form doesn't sanitize user input..."
```

**OpenIssue automatically:**
1. Adds labels: `bug`, `security`, `critical`
2. Posts a comment:
   ```
   🔍 OpenIssue Analysis
   
   Type: Bug
   Priority: 9/10 (Critical)
   Security Risk: High
   
   Potential duplicates:
   - #234: SQL injection in auth module
   - #156: Input validation issues
   
   Recommended actions:
   - Review authentication module
   - Add input sanitization
   - Run security audit
   ```
3. Notifies team members about the critical issue

## Managing Webhooks

### View Active Webhooks

The "Active Webhooks" section shows all registered webhooks:
- Repository name
- Number of events processed
- Last event timestamp
- Current status

### Delete a Webhook

1. Find the webhook in the "Active Webhooks" section
2. Click the **Delete** button
3. Confirm the deletion

The webhook will be removed from both OpenIssue and GitHub.

### Refresh Webhooks

Click the **Refresh** button to reload the webhook list and see the latest status.

## Recent Events

The "Recent Events" section shows the last 10 webhook events:
- Event type (issues, pull_request, push)
- Action (opened, edited, reopened)
- Repository
- Timestamp
- Processing status (processed, failed, pending)

This helps you verify that webhooks are working correctly.

## Troubleshooting

### Webhook Not Registering

**Problem:** "Failed to register webhook" error

**Solutions:**
1. Verify repository name format: `owner/repository`
2. Check that you have admin access to the repository
3. Ensure your GitHub token has the required permissions
4. Try refreshing the page and registering again

### Events Not Being Processed

**Problem:** Webhook registered but no events appearing

**Solutions:**
1. Create a new issue on GitHub to trigger a webhook event
2. Check the "Recent Events" section to see if events are being received
3. Verify the webhook is active in GitHub repository settings
4. Check browser console for any JavaScript errors

### Webhook Signature Validation Failed

**Problem:** Webhook events are failing with signature validation error

**Solutions:**
1. Verify the webhook secret is correctly configured
2. Ensure the webhook URL is correct
3. Check that the webhook is using HTTPS
4. Contact support if the issue persists

### Analysis Not Appearing

**Problem:** Webhook events are processed but no labels/comments added

**Solutions:**
1. Verify your GitHub token has write permissions
2. Check that the repository is properly connected
3. Ensure the analysis services are running
4. Check the backend logs for errors

## Best Practices

### 1. Monitor Critical Repositories First

Start by registering webhooks for your most important repositories:
- Core application repositories
- Security-sensitive projects
- High-traffic repositories

### 2. Select Appropriate Events

Choose events that matter for your workflow:
- **Issues only** - For issue tracking
- **Issues + PRs** - For full development workflow
- **All events** - For comprehensive monitoring

### 3. Review Analysis Comments

OpenIssue's analysis comments provide valuable insights:
- Read the priority score and reasoning
- Check for identified duplicates
- Review security warnings
- Use recommendations for issue resolution

### 4. Adjust Labels

If OpenIssue's labels don't match your workflow:
1. Edit the issue on GitHub
2. Adjust labels as needed
3. OpenIssue will learn from your adjustments

### 5. Monitor Recent Events

Regularly check the "Recent Events" section to:
- Verify webhooks are working
- Identify any processing failures
- Monitor event volume
- Detect unusual patterns

## Advanced Configuration

### Custom Webhook Secret

For enhanced security, you can configure a custom webhook secret:

1. Generate a random secret:
   ```bash
   openssl rand -hex 32
   ```

2. Add to your OpenIssue configuration:
   ```
   GITHUB_WEBHOOK_SECRET=your-generated-secret
   ```

3. Update the webhook in GitHub with the same secret

### Webhook Filtering

You can filter which events trigger analysis:

1. In the webhook registration form, select specific events
2. OpenIssue will only process selected event types
3. Reduces unnecessary processing and improves performance

### Event Replay

If you need to reprocess past events:

1. Go to the "Recent Events" section
2. Find the event you want to replay
3. Click the replay button (if available)
4. OpenIssue will reprocess the event

## Performance Considerations

### Event Processing Time

- **Webhook Response:** < 200ms (returns immediately)
- **Analysis Pipeline:** 2-5 seconds (runs in background)
- **Label Application:** < 1 second
- **Comment Posting:** < 2 seconds
- **Total Time:** 5-10 seconds

### Scalability

OpenIssue can handle:
- 1000+ webhook events per day
- Multiple repositories
- Concurrent event processing
- High-volume repositories

## Security

### Webhook Signature Validation

All webhooks are validated using HMAC-SHA256:
- GitHub signs each webhook with your secret
- OpenIssue verifies the signature
- Invalid signatures are rejected
- Prevents unauthorized webhook events

### Token Security

Your GitHub token is:
- Never stored locally
- Encrypted server-side
- Used only for authorized operations
- Rotated regularly for security

### Data Privacy

OpenIssue:
- Only accesses repositories you authorize
- Never stores issue content permanently
- Complies with GitHub's data policies
- Respects repository privacy settings

## FAQ

### Q: Can I use webhooks with private repositories?

**A:** Yes! Webhooks work with both public and private repositories. You need admin access to the repository to register webhooks.

### Q: How many webhooks can I register?

**A:** You can register webhooks for as many repositories as you want. There's no limit.

### Q: What happens if a webhook fails?

**A:** OpenIssue will:
1. Log the failure
2. Retry the event processing
3. Notify you of persistent failures
4. Provide debugging information

### Q: Can I modify webhook events after registration?

**A:** Yes! You can:
1. Delete the webhook
2. Register a new webhook with different events
3. Or contact support to modify existing webhooks

### Q: Do webhooks work with GitHub Enterprise?

**A:** Yes! Webhooks work with GitHub Enterprise Server. Contact support for setup instructions.

### Q: How do I test if my webhook is working?

**A:** 
1. Create a new issue on GitHub
2. Check the "Recent Events" section in OpenIssue
3. Verify the event appears within 10 seconds
4. Check that labels and comments are added

### Q: Can I disable webhooks temporarily?

**A:** Yes! You can:
1. Delete the webhook from OpenIssue
2. Or disable it in GitHub repository settings
3. Re-enable it anytime by registering again

## Support

If you encounter issues with webhooks:

1. Check the troubleshooting section above
2. Review the "Recent Events" for error messages
3. Check GitHub repository webhook logs
4. Contact OpenIssue support with:
   - Repository name
   - Error message
   - Recent event logs
   - Steps to reproduce

## Next Steps

- [View Webhook Documentation](./webhooks.md)
- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [OpenIssue API Documentation](./api_documentation.md)

---

**Last Updated:** April 14, 2026
**Version:** 1.0.0
