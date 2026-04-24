# Case Study: Docker Swarm Orchestration for LIMS Augmentation Platform

## Executive Summary

Architected and implemented a containerized platform using Docker Swarm to augment core LIMS functionality with 30+ microservices providing APIs, integration services, configurable portals, SSO management, and cloud file storage. The platform enabled flexible client customization without modifying the core LIMS system, reducing custom development time and supporting varied client needs through standardized, reusable components.

---

## The Challenge

### Business Context
- **Client:** LabLynx enterprise laboratory platform serving a large laboratory client base
- **Goal:** Create flexible technology platform to augment LIMS capabilities while maintaining system stability
- **Stakeholders:** Development team, DevOps engineers, client operations teams
- **Scale:** Supporting multiple client environments with varying integration and portal requirements

### Technical Challenges
- **LIMS Limitations:** Core laboratory software could not, on its own, meet diverse client requirements. Features such as APIs for BI or external data warehousing, automation for samples or instrument data, or portals for their customers to interact with reports were better handled by dedicated software.
- **Custom Development Overhead:** Each client has unique and different needs, including lab workflows, integrations, portals, and SSO configurations.
- **Technology Sprawl:** Risk of maintaining wide arrays of different software stacks for different client needs
- **Deployment Complexity:** Manual deployment and maintenance of varied services would be time-consuming and error-prone
- **Client Isolation:** Each client needed secure, isolated environments while sharing common platform components
- **Integration Requirements:** Need for flexible APIs, file storage, workflow automation, and custom portals to augment core LIMS functionality

---

## The Solution

### Architecture Overview
**Containerized augmentation platform** using Docker Swarm to extend core LIMS functionality with APIs, integration services, configurable client portals, SSO management, and cloud file storage. The platform enabled flexible client configuration, while minimizing development time and costs.

**Platform Capabilities:**
- **GraphQL API:** Flexible data access layer for LIMS integration and custom applications
- **Integration Services:** Node-RED based workflow automation and system connectivity  
- **Client Portals:** Configurable WordPress-based customer portals (MyLabCare, GetTested)
- **Cloud File Storage:** NextCloud-based secure document and file management (LabDrive)
- **SSO Management:** Centralized authentication and user management across platform services
- **Custom Applications:** Electronic Lab Notebook (ELN) and specialized client applications

**Core Technology Stack:**
- **Docker Swarm:** Container orchestration for service isolation and scalability
- **Traefik:** Reverse proxy with automatic SSL and service discovery
- **Bash Scripting:** Automated deployment and management scripts
- **Node.js/GraphQL:** API services for LIMS integration
- **Node-RED:** Visual workflow automation for integrations
- **WordPress:** Configurable client portal framework
- **NextCloud:** Cloud file storage and collaboration platform
- **MariaDB/Redis:** Database and caching infrastructure

### Implementation Approach

#### Service Architecture & Containerization

**Platform Service Categories:**
- **API Layer:** GraphQL services providing flexible data access to core LIMS functionality
- **Integration Services:** Node-RED workflow automation for connecting LIMS with external systems
- **Client Portals:** WordPress-based customizable portals for different market segments
- **File Management:** NextCloud instances for secure document storage and collaboration
- **Supporting Infrastructure:** Databases, caching, authentication, and administrative tools

**Service Isolation Strategy:**
- Each client deployed as separate Docker stack with isolated networking and storage
- Shared platform images with client-specific configuration and customization
- Standardized deployment patterns enabling consistent service delivery across varied client needs

**Load Balancing & Security Infrastructure:**
Implemented Traefik as the central reverse proxy to provide secure, automated routing and SSL certificate management across all platform services.

```yaml
# Traefik service with automatic SSL and service discovery
traefik:
  image: traefik:v2.9
  command:
    - "--providers.docker.swarmMode=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
    - "--certificatesresolvers.letsencrypt.acme.storage=/acme.json"
    - "--api.dashboard=true"
    - "--api.insecure=true"
  ports:
    - "80:80"
    - "443:443"
    - "8080:8080"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - traefik-acme:/acme.json
  deploy:
    replicas: 1
    placement:
      constraints:
        - node.role == manager
  networks:
    - traefik-public

volumes:
  traefik-acme:

networks:
  traefik-public:
    external: true
```

**Key Security & Automation Features:**
- **Automatic SSL Certificates:** Let's Encrypt integration with automated certificate renewal
- **Service Discovery:** Automatic routing based on Docker Swarm service labels
- **Security Headers:** HSTS, security headers configured per service requirements
- **Path-based Routing:** Support for complex routing rules including path stripping for admin interfaces
- **Load Balancing:** Built-in load balancing across service replicas

**Example Service Configuration Patterns:**
- Examples are slightly altered to generify.  Code examples are from a slightly older version of the platform.  

```yaml
services:
  # API service with Traefik routing and plugin volume mounting
  app:
    image: lablynx/${app_IMAGE}:latest
    environment:
      SITE: ${SITE}
    env_file:
      - ../.env
    volumes:
      - /opt/scicloud/${INSTANCE}-data/app/plugin:/usr/src/app/src/plugin
      - /opt/scicloud/${INSTANCE}-data/app/logs:/usr/src/app/src/logger/logs
    networks:
      - net
      - swarm-web
    deploy:
      labels:
        traefik.backend.loadbalancer.swarm: 'true'
        traefik.docker.network: swarm-web
        traefik.enable: 'true'
        traefik.frontend.rule: Host:${SITE}.${DOMAIN}
        traefik.port: '4000'
      resources:
        reservations:
          cpus: '0.05'
          memory: ${APP_API_MEM}
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure

  # Redis cache service with persistent storage
  redis:
    image: redis:6.2
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - /opt/scicloud/${INSTANCE}-data/app/redis:/data
    networks:
      net:
        aliases:
          - app-prod_elabapi-redis
    deploy:
      resources:
        reservations:
          cpus: '0.05'
          memory: ${APP_REDIS_MEM}
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure

networks:
  swarm-web:
    external: true
  net:
    driver: overlay
    attachable: true
    driver_opts:
      encrypted: 'true'
```

```yaml
services:
  # NextCloud application with comprehensive environment configuration
  app:
    image: nextcloud:31.0
    environment:
      MYSQL_HOST: labdrive-${INSTANCE}_db
      MYSQL_DATABASE: ${LD_MYSQL_DATABASE}
      MYSQL_USER: ${LD_MYSQL_USER}
      MYSQL_PASSWORD: ${LD_MYSQL_PASSWORD}
      NEXTCLOUD_ADMIN_USER: ${LD_NCADMIN_USER}
      NEXTCLOUD_ADMIN_PASSWORD: ${LD_NCADMIN_PASSWORD}
      NEXTCLOUD_TRUSTED_DOMAINS: ${LD_TRUSTED_DOMAINS}
      OVERWRITEHOST: ${SITE}.${DOMAIN}
      OVERWRITEPROTOCOL: https
      OVERWRITECLIURL: https://${SITE}.${DOMAIN}
      TRUSTED_DOMAINS: '*.${DOMAIN}'
      REDIS_HOST: redis
      REDIS_HOST_PORT: '6379'
    volumes:
      - /var/www/html/${SITE}.labdrive.net:/var/www/html
    networks:
      - net
      - swarm-web
    deploy:
      labels:
        traefik.backend.loadbalancer.swarm: 'true'
        traefik.docker.network: swarm-web
        traefik.enable: 'true'
        traefik.frontend.redirect.regex: https://(.*)/.well-known/(card|cal)dav
        traefik.frontend.redirect.replacement: https://$$1/remote.php/dav/
        traefik.frontend.rule: Host:${SITE}.${DOMAIN}
        traefik.frontend.headers.forceSTSHeader: 'true'
        traefik.frontend.headers.STSSeconds: 315360000
        traefik.frontend.headers.STSIncludeSubdomains: 'true'
        traefik.frontend.headers.STSPreload: 'true'
        traefik.frontend.passHostHeader: 'true'
        traefik.port: '80'
      resources:
        reservations:
          cpus: '0.05'
          memory: ${LABDRIVE_APP_MEM}
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure

  # MariaDB database with automated backup service
  db:
    image: mariadb:10.6
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    environment:
      MYSQL_ROOT_PASSWORD: ${LD_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${LD_MYSQL_DATABASE}
      MYSQL_USER: ${LD_MYSQL_USER}
      MYSQL_PASSWORD: ${LD_MYSQL_PASSWORD}
    volumes:
      - /opt/scicloud/${INSTANCE}-data/labdrive/mysql:/var/lib/mysql
      - /home/db_backups/labdrive:/backups
    networks:
      - net
    deploy:
      resources:
        reservations:
          cpus: '0.05'
          memory: ${LABDRIVE_DB_MEM}
      update_config:
        parallelism: 2
        delay: 10s
      restart_policy:
        condition: on-failure

  # Automated database backup service
  backup:
    image: databack/mysql-backup:latest
    volumes:
     - /home/db_backups/labdrive:/db
    user: root
    environment:
      DB_SERVER: db
      DB_PORT: 3306
      DB_USER: root
      DB_PASS: ${LD_MYSQL_ROOT_PASSWORD}
      DB_DUMP_FREQ: 60
      DB_DUMP_TARGET: /db
      SINGLE_DATABASE: 'true'
      DB_NAMES: ${LD_MYSQL_DATABASE}
    networks:
      - net
    deploy:
      resources:
        reservations:
          cpus: '0.05'
          memory: ${LABDRIVE_DB_MEM}

  # Administrative access via phpMyAdmin
  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    environment:
      MYSQL_ROOT_PASSWORD: ${LD_MYSQL_ROOT_PASSWORD}
      PMA_ABSOLUTE_URI: /mysdbadmin/
      PMA_HOST: db
    networks:
      - swarm-web
      - net
    deploy:
      labels:
        traefik.backend.loadbalancer.swarm: 'true'
        traefik.docker.network: swarm-web
        traefik.enable: 'true'
        traefik.frontend.rule: Host:${SITE}.${DOMAIN}; PathPrefixStrip:/mysdbadmin/
        traefik.port: '80'
      resources:
        reservations:
          cpus: '0.05'
          memory: ${LABDRIVE_PHPMYADMIN_MEM}
```

#### Automated Deployment Pipeline

**Deployment Pipeline:**
- Built comprehensive deployment automation with validation and rollback capabilities
- Implemented pre-deployment environment checks and service dependency validation
- Created rolling deployment process using Docker Swarm's built-in zero-downtime updates
- Established automated rollback triggers for failed deployments

**Real Deployment Script Patterns:**
```bash
#!/bin/bash
# Actual patterns from scicloud-stack-cmd.sh

# Memory validation before deployment
total_avail_mem=$(memCalc)
remaining_mem=$(subMinMemReq $total_avail_mem)
if [ "$remaining_mem" -lt "0" ]; then
    echo "Server does not have the memory requirements to run all these enabled applications"
    exit 1
fi

# Core deployment function used for all services
doDockerStuff() {
    local lclACTION=$1
    local lclINSTANCE=$2
    local lclCOMPOSE_PATH=$3
    local lclMAIN_SERVICE=$4

    export ROOT_DIR=$(pwd)
    export lclCOMPOSE_FILE="${lclCOMPOSE_PATH}/docker-compose.yml"
    
    if [ "$lclACTION" == "down" ]; then
        echo "Bring it down"
        docker stack rm $lclMAIN_SERVICE
    fi
    
    if [ "$lclACTION" == "up" ]; then
        echo "cd"
        cd $lclCOMPOSE_PATH
        
        # Use YamlParser to build volumes
        build_volumes $CLIENT_CODE $INSTANCE $SITE
        
        # Deploy the stack
        docker stack deploy --with-registry-auth -c docker-compose.yml $lclMAIN_SERVICE
    fi
    
    cd $ROOT_DIR
}

# Git repository management for plugin updates
doGitStuff() {
    local REPOSRC=$1
    local LOCALREPO=$2
    local LOCALREPO_VC_DIR=$LOCALREPO/.git
    
    if [ ! -d $LOCALREPO_VC_DIR ]; then
        if [ -z "$3" ]; then
            git clone $REPOSRC $LOCALREPO
        else
            git clone --branch $3 $REPOSRC $LOCALREPO
        fi
    else
        if [ -z "$3" ]; then
            git -C $LOCALREPO pull
        else
            git -C $LOCALREPO pull origin $3
        fi
    fi
}

# Swarm initialization and validation
swarmSetup() {
    { read dockerType; } < <(sudo docker info --format '{{.Swarm.LocalNodeState}}')
    case "${dockerType}" in
    inactive|pending)
        echo "Node is not in a swarm cluster: initializing swarm"
        docker swarm init;;
    active)
        echo "Node is in a swarm cluster";;
    *)
        echo "Unknown state $(docker info --format '{{.Swarm.LocalNodeState}}')";;
    esac
}

# Network setup for multi-service communication
# VERIFY CLOUD-EDGE NETWORK IS PRESENT
if [ -z "$(docker network ls -q -f name=cloud-edge)" ]; then
    echo "Creating cloud-edge network"
    docker network create --subnet 10.11.0.0/16 --driver overlay --scope swarm --opt encrypted --attachable cloud-edge
else
    echo "Cloud-edge bridge network already exists"
fi
```

**Real Service Deployment Examples:**
```bash
# Actual service deployment patterns from the script

# ELN (Electronic Lab Notebook) deployment
deployELN() {
    # Create client environment file
    touch ./elabnotes/client.env
    > ./elabnotes/client.env
    
    printf "REACT_APP_HOSTNAME=https://${SITE}.elabnotes.com\n" >> ./elabnotes/client.env
    printf "REACT_APP_CLIENT_PORT=443\n" >> ./elabnotes/client.env
    printf "REACT_APP_NODE_SERVER_HOSTNAME=https://${SITE}-api.elabnotes.com\n" >> ./elabnotes/client.env
    printf "REACT_APP_NODE_SERVER_PORT=443\n" >> ./elabnotes/client.env
    printf "REACT_APP_ONLYOFFICE_HOSTNAME=https://docs.${SITE}.labdrive.net\n" >> ./elabnotes/client.env
    
    doDockerStuff "$ACTION" "$SITE" "./elabnotes" "elabnotes-$INSTANCE"
}

# Plugin deployment with git repository management
deploySciforgePlugin() {
    local API_P_ROOT="/opt/scicloud/${INSTANCE}-data/sciforge/plugin"
    local API_PLUGIN_REPO_W_CRED=$(echo "$API_PLUGIN_REPO" | sed -e "s/^http[s]*:\/\//https:\/\/$GIT_HTTPS_USER:$GIT_PW@/i")
    
    if [ "$ACTION" != "down" ]; then
        doGitStuff $API_PLUGIN_REPO_W_CRED "../api-plugin" $API_PLUGIN_BRANCH
        
        if [ -d "$API_P_ROOT" ]; then
            find "$API_P_ROOT" -mindepth 1 -delete
            cp -r "../api-plugin/." "$API_P_ROOT"
        fi
    fi
}

# WordPress-based service deployment with plugin management
deployMyLabCare() {
    local MLC_ROOT="/var/www/html/${SITE}.mylabcare.com"
    local MYLABCARE_PLUGIN_W_CRED=$(echo "$MYLABCARE_PLUGIN" | sed -e "s/^http[s]*:\/\//https:\/\/$GIT_HTTPS_USER:$GIT_PW@/i")
    
    if [ "$ACTION" != "down" ]; then
        # Pull required plugins
        doGitStuff "https://github.com/wp-sync-db/wp-sync-db.git" "../wp-sync-db"
        doGitStuff "https://github.com/wp-sync-db/wp-sync-db-media-files.git" "../wp-sync-db-media-files"
        doGitStuff $MYLABCARE_PLUGIN_W_CRED "../mylabcare-wp" $MYLABCARE_BRANCH
        
        # Copy plugins to persistent volume locations
        if [ -d "$MLC_ROOT/wp-content/plugins/wp-sync-db" ]; then
            cp -r "../wp-sync-db" "$MLC_ROOT/wp-content/plugins/wp-sync-db"
        fi
    fi
    
    doDockerStuff "$ACTION" "$SITE" "./mylabcare" "mylabcare-$INSTANCE"
    
    # Post-deployment permissions fix
    if [ "$ACTION" == "up" ]; then
        sleep 10
        mylabcare_container=`docker ps -a | grep mylabcare-prod_app | grep Up | awk '{print $1}'`
        
        if [ $mylabcare_container ]; then
            docker exec -i $mylabcare_container /bin/bash <<EOF
                if [ ! -d "/var/www/html/wp-content/uploads" ]; then
                    mkdir -p "/var/www/html/wp-content/uploads"
                fi
                chown -R www-data:www-data /var/www/html/
                exit
EOF
        fi
    fi
}
```

**Environment Variable Management:**
```bash
# Real environment variable loading patterns
export CLIENT_CODE="$(read_var CLIENT_CODE .env)"
export INSTANCE="$(read_var INSTANCE .env)"
export SITE="$CLIENT_CODE"
if [ "$INSTANCE" != "prod" ]; then
    export SITE="$CLIENT_CODE-$INSTANCE"
fi

# Memory allocation from configuration
export ELN_CLIENT_MEM="$(read_var ELN_CLIENT .env.mem)M"
export ELN_SERVER_MEM="$(read_var ELN_SERVER .env.mem)M"
export SCIFORGE_API_MEM="$(read_var SCIFORGE_API .env.mem)M"

# Conditional service deployment based on configuration
if [ "$API_ENABLED" == "true" ]; then
    doDockerStuff "$ACTION" "$SITE" "./sciforge" "sciforge-$INSTANCE" 
fi

if [ "$ELN_ENABLED" == "true" ]; then
    deployELN
fi

if [ "$MYLABCARE_ENABLED" == "true" ] && [ -n "$MYLABCARE_PLUGIN" ]; then
    deployMyLabCare
fi
```

**Multi-Environment Strategy:**
- Standardized configuration management across development, staging, and production environments
- Implemented client-specific environment isolation using separate Docker stacks and servers
- Created automated provisioning system for rapid new client onboarding
- Established consistent deployment patterns with environment-specific overrides

**Example Environment Configuration:**
```bash
# Client environment provisioning script
provision_client_environment() {
    local client_code=$1
    local environment=$2
    
    echo "Provisioning ${client_code} ${environment} environment..."
    
    # Create client-specific network
    docker network create \
        --driver overlay \
        --attachable \
        "${client_code}-${environment}-network" 2>/dev/null || true
    
    # Create client-specific volumes
    docker volume create "${client_code}-${environment}-data" 2>/dev/null || true
    docker volume create "${client_code}-${environment}-uploads" 2>/dev/null || true
    
    # Generate environment configuration
    cat > ".env.${client_code}.${environment}" << EOF
CLIENT_CODE=${client_code}
ENVIRONMENT=${environment}
DOMAIN=${DOMAIN}
STACK_NAME=${client_code}-${environment}

# Database configuration
DB_NAME=${client_code}_${environment}
DB_HOST=database.${client_code}-${environment}-network

# Service URLs
API_URL=https://api.${client_code}.${DOMAIN}
WEB_URL=https://${client_code}.${DOMAIN}

# Resource limits
WEB_MEMORY=512M
API_MEMORY=1G
DB_MEMORY=2G
EOF

    # Deploy stack with client-specific configuration
    export $(grep -v '^#' ".env.${client_code}.${environment}" | xargs)
    
    docker stack deploy \
        --compose-file docker-compose.yml \
        --compose-file "docker-compose.${environment}.yml" \
        "${STACK_NAME}"
    
    # Validate deployment
    validate_client_deployment "$client_code" "$environment"
}
```

#### Monitoring & Operational Excellence

**Monitoring Infrastructure:**
- Implemented comprehensive health monitoring with automated alerting
- Set up centralized logging aggregation for troubleshooting distributed services
- Created performance dashboards for capacity planning and resource optimization
- Established backup and disaster recovery procedures for critical data

**Monitoring Implementation:**
- **Prometheus Node-Exporter:** Deployed node-exporter instances across all Docker Swarm nodes to collect system metrics (CPU, memory, disk, network)
- **Site Availability Monitoring:** Implemented external site checks to monitor service endpoints and application availability
- **Docker Swarm Native Health Checks:** Leveraged Docker's built-in health check mechanisms configured in service definitions
- **Infrastructure Metrics:** Monitored container resource usage, service replica status, and network connectivity through Prometheus metrics

**Backup Strategy:**
- **Database Backups:** Automated database backups handled by `databack/mysql-backup` Docker service (as shown in service configurations above) with configurable frequency and retention
- **Application Data:** Persistent Docker volumes automatically backed up through host-level backup processes
- **Server-Level Recovery:** AWS-based backup solutions implemented for complete server recovery and disaster recovery scenarios
- **Configuration Management:** All Docker Compose files, environment configurations, and deployment scripts maintained in version control for reproducible deployments

### Risk Mitigation Strategies
- **Health Checks:** Comprehensive health monitoring for all services
- **Rolling Updates:** Zero-downtime deployments with automatic rollback
- **Resource Limits:** Prevent resource exhaustion and service conflicts
- **Backup Strategy:** Automated backup of volumes and configuration
- **Version Control:** Open source applications (WordPress, NextCloud, Node-RED) were version-controlled for testing upgrades before production deployment
- **Monitoring:** Real-time alerting for service failures and performance issues

---

## Results

### Platform Delivery Metrics
- **Client Environment Provisioning:** 15m vs 2+ weeks with traditional custom development approaches
- **Deployment Automation:** Fully automated deployments with zero-downtime updates and 5-minute rollback capability
- **Service Reliability:** 100% deployment success rate across 30+ microservices
- **Environment Consistency:** 100% configuration consistency across development, staging, and production environments
- **Scalability:** Platform designed to support unlimited client instances with isolated, secure environments

### Technical Achievements
**Platform Performance Characteristics:**
- **Service startup time:** 2 minutes from deployment to full service availability
- **Resource efficiency:** Optimized containerized architecture with dynamic resource allocation
- **Network performance:** High-performance overlay networking with encrypted inter-service communication
- **Service discovery:** Sub-second endpoint resolution through Docker Swarm's native DNS
- **SSL automation:** Automatic certificate provisioning and renewal for all client domains

**Operational Excellence:**
- **Automated infrastructure:** Zero-touch deployment and management across all platform services
- **Monitoring coverage:** Comprehensive health monitoring and alerting for proactive issue resolution
- **Backup automation:** Automated database and application data backup with configurable retention
- **Security integration:** Built-in SSL, encrypted networking, and service isolation by design

### Business Impact
- **Client Flexibility:** Platform enabled rapid deployment of client-specific APIs, portals, and integrations without core LIMS modifications
- **Development Efficiency:** Standardized platform components eliminated custom development time for common client requirements
- **Technology Consolidation:** Single containerized platform replaced need for maintaining diverse technology stacks across different client implementations
- **Market Responsiveness:** New client environments provisioned in 15 minutes vs 2+ weeks with traditional approaches
- **Operational Consistency:** Standardized deployment and management processes across all client augmentation services
- **Cost Predictability:** Platform approach provided predictable infrastructure and maintenance costs through centralized, reusable components

---

## Lessons Learned

### What Worked Well
- **Docker Swarm:** Simpler than Kubernetes for this use case, excellent for small teams
- **Traefik Integration:** Automatic service discovery reduced configuration complexity
- **Health Checks:** Comprehensive health monitoring prevented cascading failures
- **Script Automation:** Bash scripts provided reliable, version-controlled deployments

### What Would Be Done Differently
- **Custom Domain Support:** Would implement features to allow clients to use custom domain names instead of being restricted to platform-provided domains
- **Flexible SSL Requirements:** Would add support for non-HTTPS requirements for self-hosted deployments where SSL termination occurs at infrastructure level
- **Multi-Stack Traefik Architecture:** Would redesign Traefik configuration to better support multiple client stacks when hosted on a single server

### Key Infrastructure Insights
- **Container Orchestration:** Essential for enterprise applications with multiple services
- **Automated Deployments:** Manual deployments not sustainable at enterprise scale
- **Service Discovery:** Automatic service registration crucial for microservices
- **Resource Management:** Proper resource limits prevent one service affecting others

---

## Technologies Used

### Core Orchestration
- **Docker Swarm:** Container orchestration and cluster management
- **Docker Engine:** Container runtime and image management
- **Docker Compose:** Service definition and configuration
- **Docker Hub:** Container image registry and distribution
- **Overlay Networks:** Secure inter-service communication

### Load Balancing & Routing
- **Traefik:** Reverse proxy with automatic service discovery
- **Let's Encrypt:** Automated SSL certificate management
- **DNS Integration:** Automatic domain resolution and routing

### Application Stack
- **Node.js/GraphQL:** API services for LIMS integration
- **Node-RED:** Visual workflow automation for integrations
- **WordPress:** Configurable client portal framework
- **NextCloud:** Cloud file storage and collaboration platform
- **MariaDB:** Database infrastructure
- **Redis:** Caching and session storage
- **phpMyAdmin:** Database administration interface

### Platform Management
- **LimStudio:** Internal provisioning and platform management application
- **Configuration Management:** YAML-based service definitions with Git version control
- **Client API Integration:** External API endpoints enabling client system integration with platform services

### Infrastructure & Deployment
- **AWS:** Base server images and cloud infrastructure
- **BitBucket:** Source code repository and version control
- **Development Workflows:** Isolated development and testing environments

### Monitoring & Backup
- **Prometheus Node-Exporter:** System metrics collection across Docker Swarm nodes
- **External Site Monitoring:** Service availability checks
- **databack/mysql-backup:** Automated database backup service
- **AWS Backup Solutions:** Server-level recovery and disaster recovery

### Automation & Scripting
- **Bash Scripts:** Deployment automation and environment management
- **Git:** Version control for open source applications and configuration
- **Docker Health Checks:** Built-in service health monitoring

---

## Architecture Diagrams

### Platform Data Flow Architecture

![Scicloud Platform Architecture](../diagrams/Architecture_images/Scicloud/Scicloud_Automation.png)

The above diagram illustrates the complete data flow and component relationships within the Scicloud LIMS augmentation platform, including:

**External Integrations:**
- **Users:** Client access through DNS-resolved domains with Let's Encrypt SSL
- **External APIs:** Integration points for LIMS data exchange and third-party services
- **LimStudio:** Internal provisioning and management application for platform configuration

**Development & Deployment Pipeline:**
- **BitBucket:** Source code repository and version control
- **Docker Hub:** Container image registry for application deployment
- **Development Environment:** Isolated development and testing workflows

**Infrastructure Components:**
- **AWS Base Server Image:** Foundation infrastructure for scalable deployment
- **Scicloud Server:** Central Docker Swarm orchestration with 30+ microservices
- **Let's Encrypt:** Automated SSL certificate management and renewal
- **DNS Integration:** Automatic domain resolution and routing

### High-Level Service Architecture

```
                    ┌─────────────────────────────────────┐
                    │            Load Balancer            │
                    │         (Traefik + SSL)            │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────┴───────────────────────┐
                    │          Docker Swarm Manager       │
                    │        (Orchestration Layer)        │
                    └─────────────┬───────────────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      │                           │                           │
┌─────┴─────┐            ┌───────┴────────┐         ┌───────┴────────┐
│  Worker   │            │    Worker      │         │    Worker      │
│  Node 1   │            │    Node 2      │         │    Node 3      │
└───────────┘            └────────────────┘         └────────────────┘

Sample Service Distribution (30+ total services):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  GraphQL    │  │  LabDrive   │  │ MyLabCare   │  │ GetTested   │
│    API      │  │ (NextCloud) │  │(WordPress)  │  │(WordPress)  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Redis     │  │   MariaDB   │  │  phpMyAdmin │  │   Traefik   │
│   Cache     │  │ Databases   │  │ (multiple)  │  │Load Balancer│
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   LabVia    │  │ ELN Client  │  │ ELN Server  │  │   Backup    │
│  (Node-RED) │  │  (React)    │  │   (API)     │  │  Services   │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘

Note: Architecture supported 30+ microservices across multiple 
laboratory platform applications with client-specific isolation
```

---

## Deployment Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Code      │    │   Build     │    │   Test      │    │   Deploy    │
│   Commit    │───▶│   Images    │───▶│   & Scan   │─ ─▶│   to Swarm  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Git Hook    │    │ Multi-stage │    │ Security    │    │ Rolling     │
│ Triggers    │    │ Docker      │    │ Scanning    │    │ Update      │
│ Build       │    │ Build       │    │ + Tests     │    │ + Health    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

*This case study demonstrates enterprise-scale container orchestration with significant business impact, showcasing DevOps expertise suitable for infrastructure architecture and modernization consulting roles.*
