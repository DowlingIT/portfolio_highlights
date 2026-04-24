AWS Migration & Security Program for Multi-Tenant SaaS

Migrated 60–80 production servers from a traditional data center to AWS over roughly two months — with nearly zero downtime across the entire client base. Each environment had unique database versions, application configs, and compliance requirements. Every server got its own cutover plan. File sync tools kept data live during transitions.

The migration became an opportunity to harden the environment: TLS 1.2 enforced across the board, security groups rebuilt from scratch.

After the migration, I took on the role of CTO and Information Security Officer. I designed and implemented a full security program to pass a NIST 800-53 v4 audit — covering SOPs, access policies, environment hardening, and incident response. Third-party auditors found us in compliance every time.

I also contributed to a Python/Vue.js internal platform that gave the ops team the ability to provision servers, manage DNS (Route 53), coordinate deployments, and rotate credentials — without direct AWS console access.

On cost management: replaced R1Soft backups with AWS-native solutions, reducing total AWS spend by 20% while improving disaster recovery from months to hours.

Stack: AWS (EC2, VPC, Route 53, CloudWatch, S3), Grafana, Prometheus, OpenSearch, AlienVault SIEM, Ansible, Python, Vue.js, SAML/LDAP, Docker, SQL Server
