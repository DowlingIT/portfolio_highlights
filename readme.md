# Jeremy Dowling — Professional Portfolio

Full-stack developer and DevOps engineer with a background in laboratory science. Eighteen years building, deploying, and securing software for regulated industries — clinical labs, pharmaceutical, environmental testing, medical examiners, food safety, and more. This repository collects case studies and project highlights from that work.

---

## Case Studies

| Project | Summary |
|---------|---------|
| [AWS Engineering & Cloud Migration](AWS%20Engineering/) | Migrated 60–80 production servers to AWS in roughly two months with near-zero downtime, then led the security program to NIST 800-53 compliance as CTO and Information Security Officer |
| [SQL Server DBA & Performance](SQL%20Server%20DBA/) | Built monitoring infrastructure and drove performance improvements — thousands of individual fixes — across a fleet of ~50 SQL Server instances hosting 80 client databases |
| [Stateless Session Management](Stateless%20Session%20Management/) | Re-architected ASP Classic session state to survive web server recycles and enable a strangler-fig migration path to .NET |
| [Enterprise Monitoring](Monitoring/) | Deployed Grafana/Prometheus across ~200 servers, driving a 5–10x reduction in customer-facing incidents |
| [Medical Examiner Information System](MEO%20Information%20System/) | Built and delivered a full case management LIMS for the second-largest medical examiner office in the US |
| [Docker Swarm Orchestration](Docker_Swarm_Orchestration/) | Architected a 30+ microservice containerized platform that cut client environment provisioning from 2+ weeks to 15 minutes |
| [GraphQL LIMS Modernization](GraphQL_LIMS_Modernization/) | Replaced legacy SOAP APIs with a self-documenting GraphQL platform, eliminating VPN dependencies and enabling client self-service integration |
| [Multi-Tenant Security Architecture](Multitenant_App_Template/) | Designed a headless, stateless application framework with OAuth 2.0/SAML, multi-tenant isolation, and compliance-ready audit systems |

---

## Git Contribution Scripts

Most of this work is in private repositories, so public contribution graphs don't tell the whole story. The `scripts/` folder includes PowerShell tools for generating contribution metrics from any local git repository.

```powershell
# Run from within the target repository
..\GitMetrics.ps1
..\GitMetricsByDate.ps1 -StartDate "2020-04-01" -EndDate "2021-04-01"
```
