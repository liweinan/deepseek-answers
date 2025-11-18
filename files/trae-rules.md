# Yes, **Cursor** Supports Rules Functionality Similar to **Trae**

**Cursor** supports rules (Rules) functionality similar to **Trae**, used to provide project-specific context and guidance for AI, ensuring generated code conforms to project standards and developer preferences. Below is a detailed explanation of Cursor's Rules functionality compared to Trae, and how Cursor implements similar features:

### 1. **Overview of Cursor's Rules Functionality**
Cursor's Rules functionality allows developers to set global or project-specific guidance rules for AI through configuration files. These rules can define coding styles, framework preferences, file references, behavior patterns, etc., making AI code generation and suggestions more aligned with project needs. Cursor's Rules are divided into two main types:

- **User Rules**:
    - Configuration Path: Set via **Cursor Settings > General > Rules for AI**.
    - Scope: Global rules applicable to all projects, suitable for setting personal preferences (e.g., always use TypeScript, concise replies, etc.).
    - Format: Plain text (MDC format not supported).
    - Example: Require AI to always use functional components instead of class components, or always use `async/await` instead of callbacks.

- **Project Rules**:
    - Configuration Path: Stored in the `.cursor/rules` folder in the project root directory, files written in `.mdc` (Markdown Components) format.
    - Scope: Project-specific, suitable for defining project architecture, coding standards, file references, etc.
    - Features: Supports automatic rule application through `globs` (file pattern matching), supports file references (such as `@filename.ts`), and can provide detailed context for Agent mode.
    - Example: Set Rails controller standards for `app/controllers/**/*.rb` files, or define Tailwind CSS style guidelines for React projects.
    - Backward Compatibility: Old `.cursorrules` files (located in project root) are still supported, but migration to `.cursor/rules` structure is recommended as it's more flexible.

**Key Features**:
- **Automatic Application**: Rules are automatically attached to AI context through `globs` (e.g., `*.tsx`) matching files.
- **File References**: Supports referencing other files (such as `tsconfig.json` or template files) as context through `@file` directives.
- **Agent Mode Support**: In Agent mode, AI automatically selects applicable rules based on rule descriptions and `globs`.
- **Version Control**: The `.cursor/rules` directory can be included in Git version control, facilitating team collaboration and rule sharing.

**Creation Method**:
- Quickly create rule files via **Cmd + Shift + P > "New Cursor Rule"**.
- Rule files support MDC format, containing metadata (such as description, file patterns) and specific guidance content.

**Example Project Rule** (`.cursor/rules/react-guidelines.mdc`):
```mdc
---
description: React Component Guidelines
globs: **/*.tsx
alwaysApply: true
---
# React Guidelines
- Use functional components with Hooks.
- Define prop types using TypeScript interfaces.
- Follow Tailwind CSS for styling.
@file ../tsconfig.json
@file ../tailwind.config.js
```

**Official Documentation**: For more details, refer to Cursor official documentation [docs.cursor.com](https://docs.cursor.com/context/rules).[](https://docs.cursor.com/context/rules)

---

### 2. **Trae's Rules Functionality**
Trae (developed by ByteDance) currently **does not have a rule file system directly equivalent to Cursor's `.cursor/rules` or `.cursorrules`**, but it implements similar functionality through other means:

- **Requirements Document and Changelog**:
    - Trae relies on developers manually creating **Requirements Document** (requirements document) or **Changelog** files, using them as AI context.
    - Developers can write project requirements in phases to Markdown files (such as `requirements.md`), and bind these files as context through the chat interface or Builder mode.
    - Example: Developers can instruct Trae "Review the whole requirement file and update the changelog for phase 1".[](https://www.reddit.com/r/TraeIDE/comments/1ilaeqh/am_i_missing_something_rules_file_support/)
    - This approach is more flexible but lacks automated rule application mechanisms, relying on manual context specification.

- **Builder Mode**:
    - Trae's Builder mode allows AI to actively read project file content, decompose tasks and execute step by step, similar to Cursor's Agent mode.
    - Developers can guide AI behavior through natural language prompts or bound context files.

- **Limitations**:
    - Trae currently does not have structured rule files like Cursor (such as `.cursor/rules`), and cannot automatically apply rules through file patterns.
    - Context management relies on manual operations, lacking Cursor's `globs` or `@file` reference functionality.
    - Some users on Reddit have mentioned that Trae lacks rule file support similar to `.cursorrules` and hope this feature will be added in the future.[](https://www.reddit.com/r/TraeIDE/comments/1ilaeqh/am_i_missing_something_rules_file_support/)

**Community Feedback**:
- Some developers have expressed hope that Trae will support rule files similar to Cursor (such as `.cursorrules` or `.clinerules`) to provide project-specific context through configuration files.[](https://github.com/Trae-AI/Trae/issues/927)[](https://www.reddit.com/r/TraeIDE/comments/1ilaeqh/am_i_missing_something_rules_file_support/)
- Trae's official documentation or changelog has not mentioned plans to support structured rule files, but its free mode and multimodal features (such as processing image context) still make it attractive in certain scenarios.[](https://prototypr.io/toolbox/trae)

---

### 3. **Comparison of Cursor and Trae Rules Functionality**

| **Feature**                     | **Cursor**                                                                 | **Trae**                                                                 |
|-----------------------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Rule Storage Method**            | `.cursor/rules` directory (`.mdc` files) or `.cursorrules` (legacy, plain text)        | No dedicated rule files, relies on requirements documents or Changelog (such as `.md` files)                |
| **Rule Format**                | MDC (supports metadata) or plain text (User Rules)                                    | Plain Markdown or other text formats, requires manual binding                                  |
| **Automatic Application**                | Supports automatic file pattern matching through `globs` (e.g., `*.tsx`)                            | Does not support automatic application, requires manual context file specification                                    |
| **File References**                | Supports `@file` references (e.g., `@tsconfig.json`)                                   | Requires manual file specification in prompts or upload through chat interface                                |
| **Global Rules**                | Supports User Rules (global settings)                                               | No global rules, requires separate context specification for each project                                  |
| **Version Control**                | `.cursor/rules` can be included in Git, suitable for team collaboration                                   | Requirements documents can be included in Git, but no structured rule system                                  |
| **Agent/Builder Mode Support**  | Agent mode automatically selects applicable rules                                                | Builder mode relies on manually bound context files                                    |
| **Community Support**                | Has community-shared rule libraries (such as [cursor.directory](https://cursor.directory/))      | Less community discussion, no dedicated rule sharing platform                                        |
| **Official Support**                | Detailed official documentation, continuously updated (e.g., v0.45 introduced `.cursor/rules`)                   | No rule file support currently, may be added in the future (based on community feedback)                          |

**Summary**:
- **Cursor's** Rules functionality is more structured and automated, suitable for developers who need fine-grained control over AI behavior, especially in large projects or team collaboration. The MDC format and `globs` mechanism of `.cursor/rules` make it easy to maintain and extend.
- **Trae's** context management is more flexible but more manual, suitable for rapid prototyping or small projects. Trae's Builder mode somewhat simulates the effect of rule guidance, but lacks Cursor's automation and standardization.

---

### 4. **Does Cursor Fully Support Trae-like Rules Functionality?**
Cursor's Rules functionality not only supports Trae-like context guidance but goes further in the following aspects:
- **Automation**: Cursor's `globs` and automatic rule selection reduce the workload of manually specifying context, while Trae relies on developers actively binding files.
- **Structure**: Cursor's MDC format supports metadata (such as description, file patterns), making it more suitable for complex projects than Trae's plain text requirements documents.
- **Team Collaboration**: Cursor's `.cursor/rules` directory can be included in version control, facilitating team sharing and maintenance, while Trae's context file management is more scattered.

**Trae's Unique Features**:
- Trae's Builder mode emphasizes phased task decomposition, which may be more suitable for projects requiring highly interactive development workflows.
- Trae's multimodal support (such as processing image context) is an area where Cursor is currently weaker, although Cursor also supports some image input.[](https://www.builder.io/blog/cursor-vs-trae)

**Shortcomings**:
- Cursor's Rules system in earlier versions (such as before v0.45) mainly relied on `.cursorrules`, with relatively simple functionality, but has now been upgraded to a more powerful `.cursor/rules` structure.[](https://forum.cursor.com/t/can-anyone-help-me-use-this-new-cursor-rules-functionality/45692)
- Trae's free mode (still free as of June 2025) may attract developers with limited budgets, while Cursor's advanced features require subscription (such as Pro plan, $20/month).[](https://www.builder.io/blog/cursor-vs-trae)

---

### 5. **How to Achieve Trae-like Rules Effects in Cursor?**
If you want to simulate Trae's requirements document or Changelog context management in Cursor, you can follow these steps:

1. **Create Project Rules**:
    - Create a `.cursor/rules` folder in the project root directory.
    - Add an `.mdc` file (such as `requirements.mdc`), with content mimicking Trae's requirements document.
    - Example:
      ```mdc
      ---
      description: Project Requirements for Phase 1
      globs: **/*.ts, **/*.tsx
      alwaysApply: true
      ---
      # Phase 1 Requirements
      - Implement user authentication with Supabase.
      - Follow RESTful API conventions.
      - Use TypeScript for all backend services.
      @file ../package.json
      @file ../supabase-config.ts
      ```

2. **Simulate Changelog**:
    - Create another rule file (such as `changelog.mdc`), recording project progress:
      ```mdc
      ---
      description: Project Changelog
      globs: alwaysApply: true
      ---
      # Changelog
      - 2025-06-10: Completed user login endpoint.
      - 2025-06-12: Added role-based access control.
      ```

3. **Combine with Agent Mode**:
    - In Agent mode, Cursor will automatically apply the above rules based on file patterns and descriptions.
    - You can further refine instructions through the chat interface (`Cmd + L`) or Inline Chat (`Cmd + I`), for example: "Review the requirements in `requirements.mdc` and update the changelog in `changelog.mdc` for phase 2."

4. **Reference Existing Files**:
    - Like Trae, you can reference requirements documents or configuration files in the project through `@file` directives to ensure AI understands project context.

5. **Team Sharing**:
    - Commit the `.cursor/rules` directory to the Git repository to ensure team members use the same rules.

**Tips**:
- Keep rules concise (recommended within 500 lines) and decompose complex rules into multiple small files.[](https://docs.cursor.com/context/rules)
- Regularly test rule effectiveness, checking if AI correctly applies them (e.g., confirm whether rules are triggered due to `globs` matching).[](https://trigger.dev/blog/cursor-rules)
- Refer to community resources, such as [cursor.directory](https://cursor.directory/), to get ready-made rule templates.[](https://workos.com/blog/what-are-cursor-rules)

---

### 6. **Does Trae Plan to Support Cursor-like Rules?**
Based on community discussions and online information:
- Trae users have expressed hope on Reddit and GitHub to add rule file support similar to `.cursorrules`, but Trae official has not confirmed whether this will be implemented.[](https://github.com/Trae-AI/Trae/issues/927)[](https://www.reddit.com/r/TraeIDE/comments/1ilaeqh/am_i_missing_something_rules_file_support/)
- Trae's development team may introduce more structured context management mechanisms in future updates, especially after its free mode attracts more users, potentially referencing Cursor's rules system.[](https://medium.com/ai-software-engineer/trae-new-upgrade-levels-up-with-cursor-free-trae-just-got-better-ff0f013f2fb4)

---

### 7. **Conclusion**
**Cursor fully supports Trae-like Rules functionality** and provides a more structured, automated solution through the `.cursor/rules` directory and MDC format. Compared to Trae's manual context management (such as requirements documents and Changelog), Cursor's Rules system has advantages in large projects, team collaboration, and rule maintenance. If you're used to Trae's workflow, you can achieve similar effects by creating similar requirements and Changelog rule files in Cursor, while enjoying Cursor's automation and community support.

**Recommendations**:
- If you need highly automated rule application and team collaboration, recommend using **Cursor's** `.cursor/rules` system.
- If you value free mode and multimodal support more, you can continue using **Trae** and simulate rule effects through requirements documents, while keeping an eye on Trae's subsequent updates.

**Further Help**:
- If you need specific Cursor Rules configuration examples or Trae context management optimization suggestions, please provide more project details (such as programming language, framework, or project scale), and I can customize more detailed guidance for you!
- Refer to Cursor official documentation [docs.cursor.com](https://docs.cursor.com/context/rules) or Trae's community discussions (such as Reddit or GitHub) for the latest information.

Hope this answers your question! 😊
