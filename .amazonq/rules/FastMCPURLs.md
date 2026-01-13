# FastMCP Server – Rules and Instructions (FastMCP Website)

## 1. Objective
The purpose of a FastMCP server is to expose well-defined tools, resources, and prompts to MCP-compatible clients (such as Amazon Q) in a secure, predictable, and maintainable manner using the FastMCP framework.

---

## 2. Prerequisites
Before creating a FastMCP server using the FastMCP website, ensure the following:

- A clearly defined business use case
- Identified APIs, services, or data sources to expose
- Authorization to access underlying systems
- Familiarity with Python and MCP concepts
- Required security and compliance approvals (if applicable)

---

## 3. Server Design Rules

### 3.1 Single Responsibility
- Each FastMCP server must serve a single, well-scoped domain.
- Avoid combining unrelated tools or data sources in one server.

### 3.2 Deterministic Behavior
- Tools must return predictable and consistent outputs.
- Avoid randomness unless explicitly documented and required.

### 3.3 Minimal Exposure
- Expose only required tools and resources.
- Do not expose internal APIs directly unless abstraction is intentional.

---

## 4. Tool Definition Guidelines

### 4.1 Tool Naming
- Use lowercase, action-oriented names (e.g., `get_build_status`)
- Avoid ambiguous or abbreviated names

### 4.2 Tool Descriptions
Each tool must include:
- Clear purpose
- Input parameters
- Output format
- Known limitations

### 4.3 Input Validation
- Validate all inputs
- Reject malformed or unexpected data
- Return meaningful error messages

---

## 5. Resource Rules
- Resources must be read-only unless mutation is explicitly required.
- Each resource must have:
  - A stable identifier
  - Clear ownership
  - Defined lifecycle
- Do not expose sensitive or regulated data without approval.

---

## 6. Prompt Design Rules
- Prompts must be task-focused and concise.
- Do not embed business logic in prompts.
- Prompts must not:
  - Include secrets or credentials
  - Override security controls
  - Encourage unsafe or speculative behavior

---

## 7. Security and Access Control

### 7.1 Secrets Management
- Never hardcode secrets in FastMCP code or configuration.
- Use environment variables or approved secrets managers.
- Rotate credentials regularly.

### 7.2 Authorization
- Enforce role-based access where applicable.
- Ensure server permissions never exceed caller permissions.
- Log all privileged operations.

---

## 8. Error Handling and Logging
- Return structured, user-safe error messages.
- Do not expose stack traces or internal system details.
- Log:
  - Tool executions
  - Errors
  - Authorization failures

---

## 9. Performance and Reliability
- Tools should complete quickly (preferably within seconds).
- Long-running operations must be asynchronous or documented.
- Implement timeouts and retries for downstream dependencies.

---

## 10. Testing and Validation
Before publishing the server via the FastMCP website:

- Test each tool independently
- Validate schema compliance
- Confirm compatibility with the target MCP client
- Verify error and failure scenarios

---

## 11. Deployment and Versioning
- Explicitly version the server (e.g., `v1`, `v1.1`)
- Breaking changes require a new version
- Deprecate tools gradually with advance notice

---

## 12. Compliance and Governance
- Follow organizational data classification policies
- Ensure compliance with legal and regulatory requirements
- Human review is mandatory for high-impact decisions

---

## 13. Ownership and Maintenance
- Assign a named owner or team
- Define escalation and support paths
- Review server behavior periodically

---

## 14. Acceptable Use
Use of the FastMCP server implies acceptance of:
- Organizational AI usage policies
- Security and compliance requirements
- Monitoring and audit logging

---

## 15. Acknowledgment
By creating or using this FastMCP server, users acknowledge and agree to adhere to these rules and instructions.
