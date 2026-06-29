# Privacy Policy — Insurance Sales MCP Server (v1.3.0)

**Effective Date**: 2026-07-XX  
**Last Updated**: 2026-06-29  
**Publisher**: AI Insurance Consultant HK  
**Contact**: charlescj79@gmail.com

## 1. Scope

This Privacy Policy applies to the **Insurance Sales MCP Server** (the "Service"), a Model Context Protocol server that provides insurance knowledge, compliance checking, customer needs assessment, and objection handling tools for licensed insurance professionals in Hong Kong.

The Service is provided as a **stateless API toolchain** — it does not operate a website, mobile app, or direct consumer-facing product. All interactions occur through integrated AI agent platforms (Dify, MCP clients, etc.).

## 2. Information We Collect

### 2.1 Data Processed by the Service
Our MCP server processes the following data types **in real-time only**:
- **Input data**: User-provided insurance scenarios, client profiles, compliance queries, objection contexts
- **Context data**: Temporary session context maintained in-memory during active tool calls
- **Compliance metadata**: GL-44/GL34 regulatory markers appended to outputs

### 2.2 Data We Do NOT Collect
- No persistent storage of personal data (names, IDs, contact info)
- No cookies or tracking pixels
- No usage analytics or profiling
- No third-party data sharing

## 3. Data Handling & Retention

| Aspect | Detail |
|--------|--------|
| **Storage** | Stateless — no persistent storage by default |
| **Retention** | Session context exists only during active tool calls, then discarded |
| **Transmission** | Encrypted via HTTPS/Bearer token authentication |
| **CORS/Rate Limiting** | Enabled to prevent unauthorized access |

## 4. AI Transparency (EU AI Act Article 50 Compliance)

- All outputs are **AI-generated** and marked with `__generated_by_ai` metadata
- The Service provides **insurance information only**, not professional financial advice
- Outputs pass through **GL-44/HKSFA compliance engine** before delivery
- Server-card.json includes full EU AI Act Art.50 disclosure statement

## 5. Your Rights (GDPR/PDPO)

Under GDPR and Hong Kong PDPO, you have the right to:
1. **Access**: Request what data we process about you
2. **Rectification**: Correct inaccurate personal data
3. **Erasure**: Request deletion of your data
4. **Portability**: Receive your data in machine-readable format
5. **Object**: Object to processing for legitimate reasons

Contact us at charlescj79@gmail.com to exercise these rights.

## 6. Third-Party Integrations

When the Service is integrated with external platforms (Dify, OpenAI, Claude, etc.):
- Each platform's own Privacy Policy applies to data processed within that platform
- Our server does not independently share data with any third party
- Platform-level data retention is controlled by the platform operator

## 7. Data Transfer & Jurisdiction

- Primary deployment: **Hong Kong** (Cloud Run HK region recommended)
- No intentional cross-border data transfer for insurance-related personal data
- If deployed on non-HK infrastructure, EU AI Act Art.50 disclosure remains applicable

## 8. Children's Privacy

The Service is intended for licensed insurance professionals aged 18+. We do not knowingly collect data from minors.

## 9. Updates to This Policy

We will update this Privacy Policy as required by regulatory changes (including but not limited to EU AI Act implementations). Updates will be posted at the same URL as this document.

## 10. Compliance References

- **EU AI Act Article 50**: Transparency obligations for AI interaction
- **Hong Kong PDPO**: Personal Data (Privacy) Ordinance Cap. 486
- **HKSFA GL-44**: Insurance advertising standards
- **HKSFA GL34**: Intermediary conduct requirements
