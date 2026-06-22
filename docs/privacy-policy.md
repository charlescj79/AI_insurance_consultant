# Privacy Policy & Terms of Service for Insurance Sales MCP Server

## 1. Introduction

This Privacy Policy and Terms of Service ("Agreement") governs your use of the **Insurance Sales MCP Server** (the "Service"), an open-source Model Context Protocol (MCP) server designed for Hong Kong insurance advisory automation.

Provider: CJ Insurance Tech Team
Repository: https://github.com/charlescj79/AI_insurance_consultant
Contact: charlescj79@gmail.com

Effective Date: 2026-06-23

## 2. Data Collection & Processing (GDPR/PDPO Compliance)

### 2.1 Local-First Architecture
Our MCP Server operates as a **local-first** tool. All data processing occurs on your local machine or private infrastructure. We do not collect, store, or transmit any user data to external servers by default.

- **No telemetry**: No usage analytics, crash reports, or telemetry data is collected
- **No cloud dependency**: The server functions fully offline in stdio mode
- **No third-party sharing**: Data stays within your environment unless you explicitly configure external integrations

### 2.2 When External APIs Are Used (Optional)
If you configure the Service to call external APIs (e.g., insurance product databases, CRM systems):

- We do not intercept or log those API requests
- You are responsible for compliance with the third-party's privacy policy
- Data transmission is handled directly between your infrastructure and the third-party API endpoint

### 2.3 HTTP Mode Security
In Streamable HTTP transport mode:

- Bearer token authentication required (no anonymous access)
- CORS restriction configurable (default: localhost only)
- Rate limiting enabled (configurable per-client)
- All connections require TLS/HTTPS in production deployments

## 3. Compliance Frameworks

### 3.1 Hong Kong Insurance Authority Compliance
The Service includes built-in compliance engines for:
- **GL-44**: 14 red-line rules + 4 yellow-line rules for insurance advisory content
- **GL34**: Guidance on cyber risk management and IT controls
- **Personal Data (Privacy) Ordinance (PDPO)**: All tool outputs designed to support PDPO-compliant data handling

### 3.2 EU AI Act Article 50 Compliance
In accordance with EU AI Act Article 50 (effective 2026-08-02):

**AI Interaction Disclosure**: Users are informed they are interacting with an automated system at the point of first interaction. The server-card.json includes the mandatory Art.50 disclosure: *"EU AI Act Art.50: users informed they interact with automated system"*

**Machine-Readable Marking**: HTTP responses include `X-AI-Assistant: insurance-sales-mcp-v1.3.0` header for machine-readable identification.

**No prohibited AI practices**: The Service does not engage in social scoring, real-time remote biometric identification, or emotion recognition as defined in Article 5 of the EU AI Act.

### 3.3 Cross-Border Data Considerations
- **Hong Kong PDPO**: All data processed locally; no cross-border transfer by default
- **EU GDPR**: No personal data leaves your local environment; compliant with Article 44 (transfers to third countries)
- **China PIPL**: For Mainland China deployments, the Service can operate fully air-gapped with no external network dependency

## 4. User Responsibilities

When using the Insurance Sales MCP Server for insurance advisory purposes:

1. **You must verify all compliance output** — The GL-44/GL34 engines are advisory aids, not legal substitutes
2. **No unauthorized insurance solicitation** — You remain responsible for ensuring any insurance-related communications comply with relevant regulatory requirements in your jurisdiction
3. **Data protection obligation** — If you feed customer data into the Service, you must have proper consent under applicable privacy laws
4. **Licensed advisory requirement** — Insurance advice must be provided by or under the supervision of a properly licensed person under Hong Kong's Insurance Authority

## 5. Intellectual Property

- The Service is released under MIT License (per server-card.json)
- All MCP tool definitions, compliance rules, and documentation are open-source
- Users retain ownership of their input data and outputs
- No trademark or branding rights transferred

## 6. Limitation of Liability

To the maximum extent permitted by law:

- The Service is provided "AS IS" without warranty of any kind
- We do not guarantee suitability for any specific insurance advisory use case
- Users assume all risk associated with using compliance outputs for regulatory purposes
- Total liability capped at the greater of HKD 100 or amounts paid (if any)

## 7. Changes to This Policy

We may update this Privacy Policy periodically. Material changes will be communicated via:
1. GitHub repository commits
2. server-card.json description field updates
3. README.md changelog entry

Users are responsible for reviewing this policy before each deployment.

---

# Terms of Service

## 1. Acceptance

By installing, running, or using the Insurance Sales MCP Server (the "Software"), you agree to these Terms of Service. If you do not agree, do not use the Software.

## 2. License Grant

MIT License — free to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the Software. See LICENSE file in repository for full text.

## 3. Permitted Use Cases

- Insurance product research and comparison
- Customer needs assessment automation
- Compliance content checking (GL-44/GL34)
- Sales workflow documentation
- Client relationship management tagging
- Objection handling script generation

## 4. Prohibited Uses

- **Unauthorized insurance solicitation**: Using the Service to solicit insurance without proper licensing
- **Misleading representations**: Generating compliance output that is intentionally misleading or non-compliant with regulatory requirements
- **Regulatory evasion**: Circumventing Hong Kong Insurance Authority, SFC, or Mainland China CBIRC regulations
- **Data fabrication**: Creating false policy comparison data or fake compliance certificates

## 5. Regulatory Disclaimer

The Insurance Sales MCP Server is a **tooling product**, not an insurance advisory service provider. It does not:

- Provide licensed insurance advice
- Replace professional compliance review
- Substitute for regulatory approval processes
- Guarantee compliance with any specific jurisdiction's requirements

Users must consult qualified legal and regulatory professionals before using the Service for commercial insurance advisory purposes in Hong Kong, Mainland China, or any other jurisdiction.

## 6. Support & Maintenance

- Community support via GitHub Issues
- No SLA commitment (open-source project)
- Updates released via GitHub releases and package registries (PyPI, Smithery, etc.)

---

*Last updated: 2026-06-23 | Next review: 2026-08-01 (prior to EU AI Act Art.50 enforcement)*
