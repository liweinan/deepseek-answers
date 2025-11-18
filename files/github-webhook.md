# GitHub Webhook is a mechanism that allows GitHub to send HTTP requests (usually POST requests) to external services when specific events occur, to achieve automated workflows or integration with third-party tools. Prow uses GitHub Webhook to listen for GitHub events (such as Pull Request creation, Issue Comment, etc.), thereby triggering CI/CD tasks. Here's a detailed introduction to GitHub Webhook, combined with Prow's usage scenarios.

---

### 1. **What is GitHub Webhook?**
- **Definition**: GitHub Webhook is an event-driven mechanism where, when specific events occur in a GitHub repository, GitHub sends an HTTP POST request to a pre-configured URL (called Webhook URL) containing relevant data about the event.
- **Uses**: Webhook allows external systems (like Prow, Jenkins, Slack, etc.) to respond to GitHub events in real-time, achieving automation, such as:
    - Triggering CI/CD pipelines (Prow listens for Pull Request events and runs tests).
    - Notifying teams (e.g., sending Issue creation events to Slack).
    - Synchronizing data (e.g., synchronizing code push events to external backup systems).

---

### 2. **GitHub Webhook Core Concepts**
#### 2.1 **Events**
- Webhook can listen for various GitHub events, common events include:
    - `push`: Code is pushed to repository (e.g., pushing new commits).
    - `pull_request`: Pull Request is created, updated, merged, or closed.
    - `issue_comment`: New comments on Issue or Pull Request.
    - `issues`: Issue is created, updated, or closed.
    - `status`: Repository status checks (like CI status) change.
- In Prow's scenario, the tutorial selected these events:
    - `Push`: Listen for code pushes.
    - `Pull Request`: Listen for Pull Request creation, updates, etc.
    - `Issue Comment`: Listen for comments on Issues or Pull Requests (e.g., users might trigger Prow commands through comments like `/retest`).

#### 2.2 **Webhook URL**
- Webhook URL is the target address where GitHub sends event data, must be a publicly accessible HTTP/HTTPS endpoint.
- In Prow's tutorial:
    - Webhook URL is configured as `https://hook.prow.yourdomain.com/hook` (using Nginx Ingress and HTTPS).
    - Prow's Hook service listens on this URL, receives GitHub events and distributes them to other components (like Plank).

#### 2.3 **Payload (Event Data)**
- When GitHub sends Webhook requests, it includes a JSON-formatted Payload containing specific information about the event.
- For example, `pull_request` event Payload might contain:
    - Repository name (`repository.full_name`: like `my-org/my-repo`).
    - Pull Request number (`pull_request.number`).
    - Event type (`action`: like `opened`, `closed`).
    - Commit SHA (`pull_request.head.sha`).
- Prow's Hook service parses this Payload, extracts necessary information (e.g., repository name and PR number) to decide whether to trigger jobs.

#### 2.4 **Webhook Secret (Optional)**
- Webhook Secret is an optional key used to verify the legitimacy of Webhook requests.
- Configuration method:
    - Specify a Secret in GitHub Webhook settings (e.g., `/path/to/hook/secret` in the tutorial).
    - When GitHub sends Webhook requests, it uses this Secret to generate an HMAC-SHA256 signature, placed in the request header's `X-Hub-Signature-256` field.
- The receiving end (e.g., Prow) uses the same Secret to verify the signature, ensuring the request comes from GitHub rather than being forged.
- In Prow:
    - `hmac-token` Secret stores the Webhook Secret for verifying GitHub Webhook requests:
      ```bash
      kubectl create secret -n prow generic hmac-token --from-file=hmac=/path/to/hook/secret
      ```

#### 2.5 **Request Headers**
- GitHub Webhook requests include some important HTTP headers:
    - **`X-GitHub-Event`**: Event type (e.g., `pull_request`, `push`).
    - **`X-Hub-Signature-256`**: HMAC-SHA256 signature for request verification (if Webhook Secret is configured).
    - **`X-GitHub-Delivery`**: Unique event ID for debugging or deduplication.

---

### 3. **GitHub Webhook Configuration**
GitHub Webhook can be configured at two levels: **Repository level** and **GitHub App level**. Prow uses GitHub App level Webhook.

#### 3.1 **Repository Level Webhook**
- Configuration location: Individual GitHub repository settings page (`https://github.com/<org>/<repo>/settings/hooks`).
- Configuration content:
    - **Payload URL**: Target URL (e.g., `https://hook.prow.yourdomain.com/hook`).
    - **Content type**: Usually select `application/json`.
    - **Secret**: Optional, for request verification.
    - **Events**: Select events to listen for (e.g., `Push`, `Pull Request`).
- Use case: Suitable for simple integration of single repositories, but not suitable for managing multiple repositories.

#### 3.2 **GitHub App Level Webhook (Method Used by Prow)**
- Configuration location: GitHub App settings page (`https://github.com/settings/apps/<your-app-name>`).
- Configuration content:
    - **Webhook URL**: Global Webhook URL (e.g., `https://hook.prow.yourdomain.com/hook`).
    - **Webhook Secret**: For request verification (e.g., `/path/to/hook/secret`).
    - **Events**: Select events for GitHub App to listen to (tutorial selected `Push`, `Pull Request`, `Issue Comment`).
- Advantages:
    - One GitHub App can manage multiple repositories, suitable for Prow's multi-repository CI/CD system.
    - Through GitHub App's permission control, Prow can operate repositories as the App (e.g., setting status, commenting on PRs).
- In Prow's tutorial:
    - Step 1 created the GitHub App.
    - Step 9 configured Webhook URL and Secret:
      ```
      1. Return to GitHub App settings page (`https://github.com/settings/apps/<your-app-name>`), in **Webhook** section, update Webhook URL to `https://hook.prow.yourdomain.com/hook`.
      2. Set Webhook Secret to the value in `/path/to/hook/secret`.
      3. Select events: Push, Pull Request, Issue Comment.
      ```

---

### 4. **GitHub Webhook Workflow in Prow**
Combined with Prow's usage scenario, GitHub Webhook's workflow is as follows:

1. **Event Trigger**:
    - User creates a Pull Request in `my-org/my-repo` repository.
    - GitHub App listens for `pull_request` event (because it's authorized to access the repository).

2. **Send Webhook Request**:
    - GitHub sends POST request to GitHub App's configured Webhook URL (`https://hook.prow.yourdomain.com/hook`).
    - Request contains:
        - Payload: Pull Request detailed information (JSON format).
        - Header info: `X-GitHub-Event: pull_request`, `X-Hub-Signature-256` (signature).

3. **Prow Processes Request**:
    - Prow's Hook service receives the Webhook request.
    - Uses `hmac-token` Secret to verify signature (ensures request comes from GitHub).
    - Parses Payload, extracts event information (e.g., repository name `my-org/my-repo`, PR number, event type `opened`).

4. **Trigger Jobs**:
    - Hook distributes event to Plank component.
    - Plank checks `prow-jobs.yaml` (stored in `my-org/my-repo` repository), finds `unit-test` job:
      ```yaml
      presubmits:
        my-org/my-repo:
        - name: unit-test
          always_run: true
          decorate: true
          spec:
            containers:
            - image: golang:1.18
              command:
              - go
              args:
              - test
      ```
    - Since `always_run: true`, Plank triggers `unit-test` job, runs `go test`.

5. **Report Results**:
    - After job completion, Prow uses `github-token` Secret to generate GitHub API access token.
    - Updates test results (e.g., `PASS` or `FAIL`) to Pull Request status checks via GitHub API.

---

### 5. **GitHub Webhook Advantages and Notes**
#### Advantages:
- **Real-time**: Immediately notifies external services when events occur, supporting real-time automation.
- **Flexibility**: Supports multiple events, suitable for various integration scenarios.
- **Security**: Verifies request source through Webhook Secret, prevents forgery.

#### Notes:
- **Network Reachability**:
    - Webhook URL must be publicly accessible (tutorial implements through public IP and Nginx Ingress).
    - If deployed on local host (like Minikube), needs port forwarding or tools (like UltraHook) to expose service.
- **Security**:
    - Always configure Webhook Secret to prevent malicious requests.
    - Use HTTPS endpoints (tutorial implements through cert-manager), ensure data encryption.
- **Error Handling**:
    - GitHub Webhook will retry several times on failure, but if consistently fails (e.g., URL unreachable), events may be lost.
    - In Prow, can debug Webhook failures through Hook logs (`kubectl logs -n prow -l app=hook`).

---

### 6. **Summary**
- **GitHub Webhook** is an event notification mechanism where GitHub sends HTTP requests to specified URLs when events occur.
- **Prow's Usage**:
    - Prow listens for events through GitHub App level Webhook (`Push`, `Pull Request`, `Issue Comment`).
    - Webhook URL (`https://hook.prow.yourdomain.com/hook`) points to Prow's Hook service.
    - Hook service receives events, triggers jobs, and reports results via GitHub API.
- **Key Points**:
    - Configure Webhook Secret for security.
    - Webhook URL must be publicly reachable.
    - Prow uses Secrets (`hmac-token` and `github-token`) to verify and operate GitHub.

Let me know if you want to learn more about Webhook Payload format or debugging methods!