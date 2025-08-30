# PROJECT_BRIEF.md

## 1. Problem Statement  
Market research and competitive analysis are often **time-consuming, fragmented, and repetitive**. Analysts must sift through large volumes of data (financial reports, stock charts, news headlines, market sentiment) before producing actionable insights. This is a **cumbersome and resource-intensive process**.  

The challenge I focused on is:  
- How can we **automate and streamline market analysis** using a multi-agent orchestration framework?  
- How can agents collaborate to provide market analysts with **timely, structured, and comprehensive insights** rather than raw, unstructured data?  

By addressing this, the system reduces manual effort, increases consistency, and allows decision-makers and users to focus on **interpreting the data and strategizing**, rather than data collection.  

---

## 2. Solution Overview  
I built the **Market Analysis Command Center** using a **multi-agent orchestration pattern**. The system is designed to simulate how a research team might divide and conquer different aspects of market analysis.  

- **Ticker Collect**  
  - First step in the pipeline.  
  - Infers the correct stock ticker symbol from a company name or topic.  
  - Ensures the workflow is always grounded in the right financial entity.  

- **Data Collector**  
  - Gathers fresh, reputable sources (financial data, news, market updates).  
  - Prioritizes recency, credibility, and citations.  
  - Provides raw material for downstream analysis.  

- **Trend Analyzer**  
  - Interprets the collected material to detect patterns, signals, and contradictions.  
  - Highlights uncertainty or missing data.  
  - Functions as the “analyst” who connects the dots across multiple inputs.  

- **Report Generator**  
  - Transforms findings into a clean, well-structured Markdown report.  
  - Uses clear formatting (headings, bullet points, source references) so stakeholders can quickly absorb details.  

- **Insight Synthesizer**  
  - Produces a concise, executive-ready summary.  
  - Distills the report into key takeaways, risks, opportunities, and recommended next steps.  
  - Balances detail with clarity, ensuring decision-makers get **actionable insights without information overload**.  

**Workflow Summary**  
1. A user provides a topic or company name.  
2. Ticker Collect infers the stock ticker.  
3. Data Collector gathers fresh, reliable information.  
4. Trend Analyzer processes and extracts trends and signals.  
5. Report Generator compiles structured findings.  
6. Insight Synthesizer distills the final executive summary.  

This orchestration ensures the system moves seamlessly from **unstructured inputs → structured analysis → decision-ready insights**.  

---

## 3. Technical Choices  
To balance **clarity, modularity, and time constraints**, I made the following design choices:  

- **Framework**  
  - **CrewAI** → chosen for its simple agent/task orchestration and strong integration with structured outputs.  
  - Initial implementations used LangChain; however, CrewAI provided a more robust framework with YAML-based agent and task definitions.  

- **LLMs**  
  - **OpenAI GPT-4o-mini** → cost-efficient and reliable for structured responses (approx. $0.15 per 1M input tokens and $0.60 per 1M output tokens, roughly equivalent to processing 2,500 pages of text).  
  - Local experimentation with **Ollama models** for offline flexibility, though these underperformed in analysis and were less efficient in generation. Additionally, Ollama models require substantial GPU hardware for desirable results.  

- **Tool Integrations**  
  - **Yahoo Finance (`yfinance`)** for stock and financial data.  
  - **TA-Lib / custom indicators** for technical analysis.  
  - **SerperDevTool** for web searching.  

- **Architecture**  
  - Modular folder structure (`src/research_crew/config`, `src/research_crew/tools`, `src/research_crew/output`).  
  - **Streamlit frontend** for lightweight UI and visualization.  

---

## 4. Future Roadmap  
If extended beyond the 5-day prototype, I would expand in three directions:  

1. **Data Scale** → Enrich tools using MCP; add APIs such as Google News, SEC filings, Reddit/Twitter sentiment for richer signals.  
2. **Agent Intelligence** → Introduce a front-end conversational LLM for interactive chat and dynamic task routing so agents decide when/if they’re needed.  
3. **Deployment** → Containerize and deploy as a lightweight service/API to integrate with enterprise workflows.  

---

## 5. Lessons Learned  
This project highlighted both opportunities and pain points of working with multi-agent GenAI:  

- **Challenges**  
  - Getting up to speed with a variety of orchestration frameworks and understanding which was the best fit.  
  - Enforcing consistency in outputs → LLMs sometimes hallucinate or drift from schema.  
  - Keeping responses fresh and relevant → some APIs provided outdated or incomplete data.  
  - Balancing complexity vs. clarity → easy to over-engineer when multiple agents are involved.  

- **How I Overcame Them**  
  - Spent the first half of the project researching orchestration frameworks and tutorials, deepening my understanding of multi-agent systems and Retrieval-Augmented Generation (RAG).  
  - Prompted agents with explicit **time/context constraints** (e.g., “as of 2025”).  
  - Iterated on modular design → each agent does one job well, and the Report Generator ties them together.  

- **Takeaway**  
  Building this project reinforced my understanding that **agentic AI systems are strongest when designed like real teams**: clear roles, validated handoffs, and mechanisms for resolving failure.  
