# Resources

Routed by what you need, not by what the talk had.

## Learn

- [MongoDB Skill Badges](https://learn.mongodb.com/skills): sixty to ninety minutes each, Credly badge on completion. *Building AI Agents with MongoDB* and *Schema Design Patterns* follow this talk directly; *AI and Innovation: How MongoDB Enables a Resilient AI Strategy* is the strategy-level companion. A one-page study sheet for the first is in [study/](study/ai-agents-skill-badge-study-sheet.md), and [course-on-pi/](course-on-pi/README.md) runs its code on self-managed MongoDB.
- *From Systems of Record to Agentic Systems of Action* (Packt, 2026), written by MongoDB practitioners: agent memory and working state, event-driven sync, controlled writeback, human oversight and auditability at enterprise scale. [mongodb.com/books](https://www.mongodb.com/books)

## The four doc pages behind the talk

- [Data modelling](https://www.mongodb.com/docs/manual/data-modeling/): embed, reference, and the workload-first process the talk's objective 1 follows.
- [Change streams](https://www.mongodb.com/docs/manual/changeStreams/): the doorbell from slide 14, including resume tokens.
- [TTL indexes](https://www.mongodb.com/docs/manual/core/index-ttl/): per-document expiry with `expireAfterSeconds: 0`.
- [Atlas Vector Search overview](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/): the semantic half of slide 17. Self-managed Search and Vector Search for Community/Enterprise are on the [compatibility page](https://mongodb.com/docs/vector-search/deployment/compatibility-limitations/).

## Ask

- [MongoDB Community Forums](https://www.mongodb.com/community/forums/): the engineering team answers.
- The docs assistant on any docs page answers most "how do I" questions directly.

## Build

- [MongoDB Agent Skills](https://www.mongodb.com/docs/agent-skills/) and the source at [github.com/mongodb/agent-skills](https://github.com/mongodb/agent-skills): schema design, query optimizer, natural-language querying, MCP setup. `npx skills add mongodb/agent-skills`, or the Claude, Codex, Cursor and Gemini plugins bundle the skills with the MCP server.
- [MongoDB MCP Server](https://www.mongodb.com/blog/post/announcing-mongodb-mcp-server): gives a coding agent the live database, so it reads real schemas and indexes instead of guessing.
- [Integrate MongoDB with LangGraph](https://www.mongodb.com/docs/atlas/ai-integrations/langgraph/): the checkpointer and store that backup slide 25 describes.
- [Your database just became your AI control point](https://www.mongodb.com/company/blog/news/your-database-just-became-your-ai-control-point): the IDC framing behind slide 18.

## Scale

- Customers and partners: your account team, or [mongodb.com/company/contact](https://www.mongodb.com/company/contact). Bring the run document; it is the conversation starter.

## The talk's own background

- [MongoDBSimCity](https://eoinjordan.github.io/MongoDBSimCity/): an explorable 3D model of a MongoDB server, measured against the same Pi.
- [Lessons learned from building an agentic AI MCP server for Edge Impulse](https://www.edgeimpulse.com/blog/lessons-learned-from-building-an-agentic-ai-mcp-server-for-edge-impulse): the write-up the first half of the talk comes from.
- [GB Studio MCP server](https://github.com/eoinjordan/gb-studio-agent): skills versus tools, in an educational setting.
