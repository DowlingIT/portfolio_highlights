# Case Study: Modernizing Legacy LIMS with GraphQL Architecture

## Executive Summary

Led the API modernization component of LIMS by implementing a comprehensive GraphQL API alongside existing SOAP services, enhancing security with OAuth-like authentication, and eliminating client VPN/SDWAN dependencies. This multi-phase architectural transformation provided a documented, self-service API platform with plugin-based extensibility, establishing foundation for future database-first development migration while maintaining parallel API architectures as part of broader LIMS modernization initiatives.

---

## The Challenge

### Business Context
- **System:** LIMS web application with legacy SOAP API architecture
- **Problem:** Legacy SOAP API limited client self-sufficiency with opaque schema, while direct database access via VPN/SDWAN created security risks and complicated client infrastructure. Monolithic architecture restricted development agility and future database platform flexibility.
- **Business Drivers:** Enable client self-sufficiency through modern API tooling, enhance security posture, improve development environment, and establish foundation for future database platform migration (SQL Server to PostgreSQL via Sequelize ORM abstraction)
- **Stakeholders:** LabLynx development team, client IT departments, laboratory administrators, customer development teams
- **Timeline:** Multi-phase modernization project with long-term architectural transformation goals

### Legacy System Limitations
- **Legacy SOAP API:** Outdated web service architecture with opaque schema definition
- **Security Enhancement Opportunity:** Authentication system could benefit from modern OAuth-like security patterns
- **Network Security Risks:** Clients using SDWAN/VPN for direct database access created potential for insecure configurations mitigated by more expensive infrastructure
- **Schema Visibility Loss:** SOAP API provided no schema introspection unlike direct database access via SSMS
- **Documentation Gap:** No schema-level self-service API documentation for client integration teams
- **Development Approach:** Database-first coding approach limiting development agility and testing
- **Database Platform Lock-in:** Direct SQL Server dependencies limited future database platform flexibility and migration options

### Strategic Objectives
1. **Implement modern GraphQL API** alongside existing SOAP services with goal of eventual replacement
2. **Implement OAuth-like authentication** for enhanced security
3. **Eliminate SDWAN/VPN security risks** by providing controlled API access to specific database resources
4. **Provide documented schema** via GraphQL Sandbox for self-service integration
5. **Enable plugin-based architecture** for seamless custom function integration with CI/CD
6. **Establish foundation** for eventual migration from database-first to code-first development approach

---

## The Solution

### Architecture Overview
**Modern GraphQL API platform** implemented alongside existing SOAP services with OAuth-like security, self-service documentation, and plugin-based extensibility to provide controlled access while eliminating network security risks.

**Core Technology Stack:**
- **GraphQL:** Apollo Server with TypeScript for type-safe, self-documenting schema
- **Schema Models:** Sequelize models shared with GraphQL for database structure transparency
- **Authentication:** OAuth-like token-based security replacing legacy authentication
- **Runtime:** Node.js with Express.js web framework
- **Database Access:** Secure API layer providing controlled access to specific application resources
- **Documentation:** GraphQL Sandbox providing schema introspection similar to SSMS
- **Plugin Architecture:** Extensible framework for custom client functions
- **Deployment:** Docker containers with Bitbucket Pipelines CI/CD and scicloud_auto server stack for automated plugin deployment

### Implementation Approach

#### GraphQL Schema Implementation with Dual Decorators
```typescript
// GraphQL schema implemented alongside SOAP operations
// LIMS entities with both Sequelize and GraphQL decorations
import { Model, Table, Column, PrimaryKey, DataType, AllowNull, AutoIncrement, 
         ForeignKey, BelongsTo, HasOne, HasMany } from 'sequelize-typescript';
import { Field, ObjectType, Int } from "type-graphql";

@ObjectType()
@Table({ timestamps: false, freezeTableName: true, hasTrigger: true })
export class LIM_SAMPLE extends Model<LIM_SAMPLE> {
    @Field(() => Int)
    @PrimaryKey
    @AutoIncrement
    @AllowNull(false)
    @Column(DataType.INTEGER)
    SAMPLEID: number;

    @Field({ nullable: true })
    @AllowNull(true)
    @Column(DataType.STRING)
    SAMPLENUMBER: string;

    @Field(() => [LIM_SAMPLETESTRUN])
    @HasMany(() => LIM_SAMPLETESTRUN)
    Tests: LIM_SAMPLETESTRUN[];

    @Field(() => GEN_SAMPLE)
    @HasOne(() => GEN_SAMPLE, 'SAMPLEID')
    GenSample: GEN_SAMPLE;

    @Field({ nullable: true })
    @AllowNull(true)
    @Column(DataType.DATE)
    SAMPLECOLLECTIONDATE: Date;

    @Field(() => Int, { nullable: true })
    @ForeignKey(() => LIM_PKL_STATUS)
    @AllowNull(true)
    @Column(DataType.INTEGER)
    SAMPLESTATUS: number;

    @Field(() => LIM_PKL_STATUS, { nullable: true })
    @BelongsTo(() => LIM_PKL_STATUS)
    Status: LIM_PKL_STATUS;
}

@ObjectType()
@Table({ timestamps: false, freezeTableName: true, hasTrigger: true })
export class GEN_SAMPLEGROUP extends Model<GEN_SAMPLEGROUP> {
    @Field(() => Int)
    @PrimaryKey
    @AutoIncrement
    @AllowNull(false)
    @Column(DataType.INTEGER)
    SAMPLEGROUPID: number;

    @Field({ nullable: true })
    @AllowNull(true)
    @Column(DataType.STRING)
    SAMPLEGROUPNUMBER: string;

    @Field(() => [GEN_SAMPLE])
    @HasMany(() => GEN_SAMPLE, "SAMPLEGROUPID")
    gen_sample: GEN_SAMPLE[];
}

@ObjectType()
@Table({ timestamps: false, freezeTableName: true, hasTrigger: true })
export class GEN_SAMPLE extends Model<GEN_SAMPLE> {
    @Field(() => Int)
    @PrimaryKey
    @ForeignKey(() => LIM_SAMPLE)
    @AllowNull(false)
    @Column(DataType.INTEGER)
    SAMPLEID: number;

    @Field(() => Int, { nullable: true })
    @ForeignKey(() => GEN_SAMPLEGROUP)
    @AllowNull(true)
    @Column(DataType.INTEGER)
    SAMPLEGROUPID: number;

    @Field(() => LIM_SAMPLE)
    @BelongsTo(() => LIM_SAMPLE, { foreignKey: 'SAMPLEID' })
    Sample: LIM_SAMPLE;

    @Field(() => GEN_SAMPLEGROUP)
    @BelongsTo(() => GEN_SAMPLEGROUP)
    SampleGroup: GEN_SAMPLEGROUP;
}

@ObjectType()
@Table({ timestamps: false, freezeTableName: true})
export class LIM_TEST extends Model<LIM_TEST> {
    @Field(() => Int)
    @PrimaryKey
    @AllowNull(false)
    @Column(DataType.INTEGER)
    TESTID: number;

    @Field({ nullable: true })
    @AllowNull(true)
    @Column(DataType.STRING)
    TESTNAME: string;

    @Field(() => Int, { nullable: true })
    @ForeignKey(() => LIM_SAMPLETYPES)
    @AllowNull(true)
    @Column(DataType.INTEGER)
    SAMPLETYPEID: number;

    @Field(() => LIM_SAMPLETYPES)
    @BelongsTo(() => LIM_SAMPLETYPES)
    SampleType: LIM_SAMPLETYPES;
}

@ObjectType()
@Table({ timestamps: false, freezeTableName: true, hasTrigger: true })
export class LIM_SAMPLETESTRUN extends Model<LIM_SAMPLETESTRUN> {
    @Field(() => Int)
    @PrimaryKey
    @ForeignKey(() => LIM_SAMPLE)
    @AllowNull(false)
    @Column(DataType.INTEGER)
    SAMPLEID: number;

    @Field(() => Int)
    @PrimaryKey
    @ForeignKey(() => LIM_TEST)
    @AllowNull(false)
    @Column(DataType.INTEGER)
    TESTID: number;

    @Field(() => Int)
    @PrimaryKey
    @Default(1)
    @AllowNull(false)
    @Column(DataType.INTEGER)
    RUNID: number;

    @Field(() => LIM_SAMPLE)
    @BelongsTo(() => LIM_SAMPLE)
    Sample: LIM_SAMPLE;

    @Field(() => LIM_TEST)
    @BelongsTo(() => LIM_TEST)
    Test: LIM_TEST;
}

// GraphQL resolvers providing modern API access
// Sample resolver patterns from LIMS
@Resolver()
export class LimSampleResolver {
    @Query(() => [LIM_SAMPLE])
    async getSamplesByGroup(
        @Arg("groupId") groupId: number,
        @Ctx() context: AuthenticatedContext
    ): Promise<LIM_SAMPLE[]> {
        // Query samples through GEN_SAMPLE -> GEN_SAMPLEGROUP relationship
        // Provides type-safe database access through GraphQL
        // Schema structure visible through server-level introspection
        return LIM_SAMPLE.findAll({
            include: [{
                model: GEN_SAMPLE,
                where: { SAMPLEGROUPID: groupId },
                include: [GEN_SAMPLEGROUP]
            }]
        });
    }

    @Query(() => [LIM_SAMPLETESTRUN])
    async getTestRunsForSample(
        @Arg("sampleId") sampleId: number
    ): Promise<LIM_SAMPLETESTRUN[]> {
        // Access test runs through junction table
        return LIM_SAMPLETESTRUN.findAll({
            where: { SAMPLEID: sampleId },
            include: [LIM_TEST, LIM_SAMPLE]
        });
    }
}
```

#### OAuth-like Authentication with Database Validation
```typescript
// JWT-based authentication replacing legacy session system
@Resolver()
export class LoginAppKeyResolver {
    @UseMiddleware(auth)
    @Mutation(() => String, { nullable: true, description: "JWT login based on app secret" })
    async LoginAppKeyJWT(): Promise<String | null> {
        let payload = {
            uid: randomString(12)
        }
        return jwt.sign(
            { payload: payload }, 
            process.env.JWT_SECRET as string, 
            { expiresIn: '1h' }
        );
    }
}

// JWT middleware for protecting GraphQL operations
export const isAuthJWT: MiddlewareFn<UserContext> = async ({ context }, next) => {
    let authObj: IAuth | null = authFactory.getAuthObject(context)
    if (!authObj){
        customHandleError("AuthManager", "Invalid Request Params", 'ERROR');
    }
    await authObj?.doAuth(context)
    .catch((err) => {
        logEvent("AuthManager", `${err}`, 'ERROR');
        customHandleError("AuthManager", `${authObj?.errMessageGeneric}`, 'ERROR');
    })

    authObj?.logSuccess(context) 
    return next()
};

// Protected resolver using JWT middleware
@Resolver()
export class MyLabCareItemsResolver {
    private genItemsRepo = new GEN_ITEMSRepo;

    @UseMiddleware(isAuthJWT)
    @Query(() => [GEN_ITEMS], { nullable: true })
    async mlcGetAllItems(): Promise<GEN_ITEMS[] | null> {
        return this.genItemsRepo.getAll();
    }

    @UseMiddleware(isAuthJWT)
    @Query(() => [GEN_ITEMS], { nullable: true })
    async mlcGetAllItemsByItemTypeId(
        @Arg("itemTypeId") itemTypeId: number
    ): Promise<GEN_ITEMS[] | null> {
        return this.genItemsRepo.getAllByItemTypeId(itemTypeId);
    }
}

// Custom attribute resolver with JWT protection
@Resolver()
export class ATT_GEN_SAMPLEGROUPResolver {
    @UseMiddleware(isAuthJWT)
    @Query(() => ATT_GEN_SAMPLEGROUP, { nullable: true })
    async getCustomAttributeBySampleGroupIdAndAttrId(
        @Arg("sampleGroupId") sampleGroupId: number,
        @Arg("attrId") attrId: number
    ): Promise<ATT_GEN_SAMPLEGROUP | null> {
        const attGenSampleGroupRepo = new ATT_GEN_SAMPLEGROUPController(attrId);
        return await attGenSampleGroupRepo.getBySampleGroupId(sampleGroupId);
    }
}
```

#### Plugin Architecture with Dynamic Resolver Loading
```typescript
// Plugin architecture implementation for API
// Dynamic resolver loading for extensible functionality
export const addPluginResolversToArray = (folderPath: string, modulesArr: any[]) => {
    if (fs.existsSync(folderPath)) {
        const modules: any = [];

        fs.readdirSync(folderPath).forEach(appFolder => {
            const stat = fs.statSync(`${folderPath}/${appFolder}`);

            if (stat.isDirectory()) {
                fs.readdirSync(`${folderPath}/${appFolder}`).forEach(folder => {
                    if (folder === "resolvers") {
                        fs.readdirSync(`${folderPath}/${appFolder}/${folder}`).forEach(file => {
                            if (file !== "index.ts" && file.endsWith('.ts')) {
                                const filename = file.substring(0, file.length - 3);
                                const module = require(`${folderPath}/${appFolder}/${folder}/${filename}`);
                                const moduleName = Object.keys(module)[0];
                                modules.push(module[moduleName]);
                            }
                        })
                    }
                });
            }
        });

        // Add discovered plugin modules to resolver array
        const moduleNames = Object.keys(modules);
        for (let i = 0; i < moduleNames.length; i++) {
            const module = modules[moduleNames[i]];
            if (typeof module === "function") {
                modulesArr.push(module);
            }
        }
    }
};

// Schema creation with plugin integration
export const createSchema = () => {
    let resolvers: any = [];
    const resolversPath = Object.values(ResolverFolderPath);
    const pluginResolversPath = Object.values(PluginResolverFolderPath);

    // Load core resolvers
    for (let i = 0; i < resolversPath.length; i++) {
        addResolversToArray(resolversPath[i], resolvers);
    }

    // Load plugin resolvers dynamically
    for (let i = 0; i < pluginResolversPath.length; i++) {
        addPluginResolversToArray(pluginResolversPath[i], resolvers);
    }

    return buildSchema({
        resolvers: resolvers,
        authChecker: ({ context: { req } }) => {
            return !!req.session.userId;
        }
    });
};
```

#### Apollo Server Configuration with Self-Service Documentation
```typescript
// Apollo Server setup from API index.ts
const main = async () => {
    const app = Express();
    const RedisStore = connectRedis(session);

    // Configure session management with Redis
    app.use(session({
        store: new RedisStore({ client: redis as any }),
        name: "SESSION_ID",
        secret: process.env.SESSION_SECRET as string,
        resave: false,
        saveUninitialized: false,
        cookie: {
            httpOnly: true,
            sameSite: 'none',
            secure: process.env.NODE_ENV === "production",
            maxAge: 1000 * 60 * 60 * 24 * 7 // 7 days
        }
    }));

    // Connect to SQL Server database
    await limsmssql.authenticate()
        .then(() => console.log('Successfully connected to the database.'))
        .catch(err => console.error('Unable to connect to the database:', err));

    // Build GraphQL schema with plugin support
    const schema = await createSchema();

    const apolloServer = new ApolloServer({
        schema,
        introspection: true, // Enable schema introspection like SSMS
        playground: true,    // Enable GraphQL Playground for self-service
        formatError: (err) => {
            // Do not expose internal errors
            if (err.message.startsWith("Database Error: ")) {
                return new Error('Internal server error');
            }

            if (err.originalError instanceof AuthenticationError) {
                return new Error('Authentication failed!');
            }
            return err;
        },
        context: ({ req, res }: any) => ({ req, res })
    });

    apolloServer.applyMiddleware({ 
        app, 
        cors: {
            origin: process.env.ALLOWED_ORIGINS?.split(',') || false,
            credentials: true
        }, 
        bodyParserConfig: { limit: "10mb" } 
    });

    // HTTPS support for production
    if (process.env.TLS_CERT_KEY && process.env.TLS_CERT_PEM) {
        https.createServer({
            key: fs.readFileSync(process.env.TLS_CERT_KEY as string),
            cert: fs.readFileSync(process.env.TLS_CERT_PEM as string)
        }, app).listen(parseInt(process.env.PORT || '4000'), () => {
            console.log(`server started on https://localhost:${process.env.PORT || '4000'}/graphql`);
        });
    } else {
        app.listen(parseInt(process.env.PORT || '4000'), () => {
            console.log(`server started on http://localhost:${process.env.PORT || '4000'}/graphql`);
        });
    }
};
```

#### Automated Testing Architecture
```typescript
// Comprehensive test suite with Jest and TypeScript
// Repository layer unit tests with Sequelize mocking
describe("GEN_SAMPLEGROUPRepo test", () => {
  const testgenSampleGroup: any = {
    SAMPLEGROUPID: 1,
    SAMPLEGROUPETYPEID: 1,
    SAMPLEGROUPNUMBER: 'testNumber',
    SAMPLEGROUPDETAIL1: 'testDetail1'
  };

  test("get GEN_SAMPLEGROUP by Pk", async () => {
    const result = await genSampleGroupRepo.getByPk(testgenSampleGroup.SAMPLEGROUPID);
    expect(result!.SAMPLEGROUPNUMBER).toBe(testgenSampleGroup.SAMPLEGROUPNUMBER);
  });

  test("GEN_SAMPLEGROUP exists", async () => {
    const result = await genSampleGroupRepo.exists(testgenSampleGroup);
    expect(result).toBe(true);
  });
});

// GraphQL integration tests with custom gCall utility
const meQuery = `
 {
  me {
    id
    firstName
    lastName
    email
    name
  }
}
`;

describe("GraphQL API", () => {
    it("get user via GraphQL", async () => {
        const userRec = await user.create({
            firstName: faker.name.firstName(),
            lastName: faker.name.lastName(),
            email: faker.internet.email(),
            password: faker.internet.password()
        });

        const response = await gCall({
            source: meQuery,
            userId: userRec.id
        });

        expect(response).toMatchObject({
            data: {
                me: {
                    id: `${userRec.id}`,
                    firstName: userRec.firstname,
                    lastName: userRec.lastname,
                    email: userRec.email
                }
            }
        });
    });
});

// Mock factory pattern for isolated testing
const SequelizeMock = require('sequelize-mock');
const DBConnectionMock = new SequelizeMock();
export const genSampleGroup = DBConnectionMock.define(
  'GEN_SAMPLEGROUP',
   genSampleGroupData,
   { freezeTableName: true }
);

jest.spyOn(GEN_SAMPLEGROUP, "findAll").mockImplementation((query) => genSampleGroup.findAll(query));
jest.spyOn(GEN_SAMPLEGROUP, "findOne").mockImplementation((query) => genSampleGroup.findOne(query));
```

### Risk Mitigation Strategies
- **Parallel API Architecture:** Maintained SOAP endpoints during GraphQL implementation and development phase
- **Strategic Use Case Selection:** GraphQL API deployed for specific engineering team projects including data warehousing and interfacing applications in lieu of SOAP
- **Engineering Team Adoption:** Internal teams could leverage GraphQL for new projects while existing SOAP integrations remained operational
- **Incremental Capability Building:** GraphQL API development progressed through targeted use cases to build functionality and prove concept before broader deployment

---

## Results

### Technical Metrics
- **API Modernization:** GraphQL API successfully implemented alongside existing SOAP services
- **Schema Transparency:** GraphQL introspection provided database structure visibility
- **Query Flexibility:** Single GraphQL query can replace multiple SOAP operation calls
- **Schema Documentation:** Self-documenting GraphQL schema with real-time introspection via Sandbox
- **Code Maintainability:** TypeScript implementation improved type safety and development experience
- **Test Coverage:** Comprehensive automated test suite with Jest covering repository layer, GraphQL resolvers, and integration scenarios
- **Test Framework:** Complete testing infrastructure with mocked database operations, GraphQL query testing utilities, and CI/CD integration
- **Mock Architecture:** Sophisticated mocking system using sequelize-mock for isolated unit testing without database dependencies
- **Parallel API Support:** GraphQL API operational alongside existing SOAP services without interference

### Performance Benchmarks
```
API Architecture Status:
- SOAP API: Maintained for existing client integrations (opaque schema)
- GraphQL API: New implementation with schema introspection capabilities
- Dual Support: Both APIs operational and fully supported

Schema Visibility Comparison:
- Direct Database Access: Full schema visibility via SSMS/tools
- SOAP API: No schema introspection or structure visibility
- GraphQL API: Complete schema introspection via Sandbox (similar to SSMS)

Test Coverage Metrics:
- GraphQL Resolvers: Integration tests covering authentication and query execution
- Mock Framework: Comprehensive mocking for database operations using sequelize-mock
- CI/CD Integration: Automated test execution via "npm test" in Bitbucket Pipelines

Client Integration Options:
- Legacy clients: Continue using established SOAP integrations during transition
- New clients: GraphQL API with schema exploration and modern tooling
- Migration approach: Clients transitioning operations from SOAP to GraphQL incrementally
- End goal: Complete migration to GraphQL with SOAP deprecation

Developer Experience:
- GraphQL: Self-documenting schema with interactive sandbox exploration
- SOAP: Traditional WSDL documentation maintained
- Schema Discovery: GraphQL Sandbox provides database structure insight previously only available via direct DB tools
- Test-Driven Development: Jest framework enabling rapid development cycles with immediate feedback
```

### Business Impact
- **API Modernization:** Successfully implemented GraphQL API alongside existing SOAP services
- **Schema Transparency Restored:** GraphQL Sandbox provided database structure visibility that SOAP eliminated
- **Security Enhancement:** OAuth-like authentication and controlled API access eliminated VPN security risks
- **Controlled Access:** Secure API limits access to relevant application aspects with no broader database exposure
- **Developer Experience:** GraphQL Sandbox reduced integration complexity and restored schema exploration
- **Extensibility:** Plugin architecture enabled custom client functions with seamless CI/CD integration
- **Client Choice:** Dual API support allows clients to migrate from SOAP to GraphQL at their own pace
- **Database Structure Access:** Sequelize model sharing enabled schema introspection similar to SSMS
- **Development Efficiency:** Dockerized environment eliminated setup friction for customer development teams
- **Future-Proofing:** Modern API foundation established for long-term architectural evolution and SOAP replacement

### Implementation Status
- **GraphQL API:** Fully implemented and operational alongside SOAP during transition phase
- **OAuth-like Security:** Enhanced authentication available for GraphQL clients
- **Controlled Access:** Secure API providing limited access to relevant application resources
- **Self-Service Documentation:** GraphQL Sandbox fully deployed
- **Plugin Architecture:** Extensible system with CI/CD integration operational
- **SOAP API:** Currently maintained for existing integrations with planned deprecation
- **Migration Progress:** Clients transitioning from SOAP to GraphQL on structured timeline
- **Phase 5 Planned:** Database-first to code-first development migration (long-term objective)

---

## Lessons Learned

### What Worked Well
- **Documentation-First Approach:** GraphQL schema-first development improved client adoption
- **Parallel API Strategy:** Maintaining SOAP while adding GraphQL reduced migration pressure
- **Plugin Architecture:** Extensible design enabled custom client requirements without core changes
- **OAuth-like Security:** Token-based authentication simplified infrastructure for adopting clients
- **Self-Service Platform:** GraphQL Sandbox reduced integration support overhead for clients
- **Dockerized Development:** Containerized environment enabled customer developers to quickly setup identical development environments

### What Would Be Done Differently
- **API Versioning:** Would implement comprehensive versioning strategy for both APIs from start
- **Test Coverage:** Would allocate dedicated time for greater automated test coverage
- **Project Phasing:** Would plan out more detailed project phases aligned with measurable goals that could be effectively communicated with leadership team

### Key Technical Insights
- **Dual API Architecture:** Running SOAP and GraphQL in parallel provides safe migration path without forcing immediate transition
- **Security Evolution:** OAuth-like patterns with controlled API access better than VPN-based direct database access
- **Plugin Integration:** Hot-reload capabilities essential for development productivity
- **Client Migration:** Allowing gradual transition from SOAP to GraphQL improved adoption and reduced resistance
- **Controlled Access:** Code-first approach provides secure, limited access preventing broader database exposure
- **Deprecation Strategy:** Parallel operation enables structured SOAP sunset with minimal client disruption

### Long-term Architectural Vision
- **SOAP Deprecation:** Planned sunset of SOAP API once GraphQL migration is complete
- **Database-First Migration:** Foundation established for future transition away from database-first development
- **Microservices Evolution:** Plugin architecture positions system for microservices transformation
- **Client Ecosystem:** Self-service platform enables broader third-party integration ecosystem
- **API Consolidation:** Single GraphQL API endpoint replacing multiple SOAP operations for simplified integration

---

## Technologies Used

### Core Stack
- **GraphQL:** Apollo Server 4.0 with TypeScript integration
- **Schema Models:** Sequelize ORM models shared with GraphQL for database structure transparency
- **Authentication:** OAuth-like JWT token system with refresh capabilities
- **Runtime:** Node.js 18.x with Express.js 4.x
- **Language:** TypeScript 4.8 for full type safety
- **Database Access:** Secure API layer providing controlled access to specific application resources
- **Documentation:** GraphQL Sandbox with interactive schema exploration (SSMS-like experience)
- **Plugin System:** Custom extensible architecture for client-specific functions

### Development & Deployment
- **Testing:** Jest with GraphQL testing utilities
- **Schema Management:** GraphQL schema-first development approach
- **CI/CD Integration:** Bitbucket Pipelines for Docker image builds, dockerized server stack deployment with plugin auto-pull from separate repositories
- **Plugin Management:** Separate repositories for plugins with automatic master branch deployment during server stack operations
- **Containerization:** Docker with multi-stage builds for plugin isolation
- **Development Environment:** Dockerized development setup providing identical environments for customer developers
- **Environment Consistency:** Docker Compose configuration ensuring consistent development experience across teams
- **Code Generation:** SQL scripts for auto-building GraphQL schema objects and resolvers from database structure

### Security & Network Architecture
- **API Security:** OAuth-like token-based authentication providing controlled access to application resources
- **Network Access:** HTTPS-only API endpoints eliminating VPN security configuration risks
- **Database Architecture:** Dedicated SQL Server database per client with GraphQL API connection
- **Audit Logging:** Comprehensive API access logging for compliance
- **Controlled Scope:** API access limited to relevant application aspects preventing broader database exposure

---

## Architecture Diagrams

### Plugin Architecture - Onion Model

![Sciforge Onion Architecture](../diagrams/Architecture_images/Sciforge/Onion.png)

The onion architecture shows the layered structure of the GraphQL LIMS platform:

**Core Layer - Models:**
- Types and typedefs in source code folders
- Sequelize models with dual GraphQL decorators

**Model Services Layer:**
- Repository interfaces providing data access abstraction
- Report engine configuration and setup

**Application Services Layer:**
- Controllers handling business logic
- Mappers and DTOs for data transformation
- Report engine implementation

**Application Layer:**
- GraphQL mutations and queries
- Configuration repository implementations
- Plugin resolver integration points

### Current Architecture (Dual API Support)

```

┌─────────────────┐    ┌─────────────────┐    
│   Legacy Apps   │    │   Modern Apps   │    
│   (SOAP)        │    │   (GraphQL)     │    
└─────────┬───────┘    └─────────┬───────┘    
          │                      │            
          │ SOAP/HTTPS           │ HTTPS/OAuth
          │ (Legacy Auth)        │ (JWT Tokens)
          │                      │            
    ┌─────┴─────┐      ┌─────────┴───────────┐
    │ SOAP API  │      │   GraphQL Gateway   │
    │ (Legacy)  │      │ (Apollo + Schema)   │
    └─────┬─────┘      │   + Plugin System   │
          │            └─────────┬───────────┘
          │                      │            
          └──────────────────────┼────────────┘
                                 │
                    ┌─────────────┴───────────┐
                    │      Dedicated          │
                    │    SQL Server Database  │
                    └─────────┬───────────────┘
                              │
                              │ Direct Access (SDWAN/VPN)
                              │ (Legacy - being replaced by GraphQL)
                              │
                    ┌─────────┴───────────────┐
                    │  Client Environment     │
                    │ ┌─────────────────────┐ │
                    │ │ Third-party APIs &  │ │
                    │ │    BI Tools         │ │
                    │ └─────────────────────┘ │
                    └─────────────────────────┘
```

---

## Business Metrics Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Architecture | SOAP only | SOAP + GraphQL | Modern option added |
| Schema Visibility | Direct DB (SSMS) vs None (SOAP) | Direct DB + GraphQL Sandbox | Restored via API layer |
| Authentication Options | Legacy session-based | Legacy + OAuth-like | Enhanced security option |
| Client Integration Choice | SOAP mandatory | SOAP or GraphQL (transition) | Flexible migration path |
| API Documentation | WSDL only | WSDL + GraphQL Sandbox | Self-service schema exploration |
| Custom Functions | Manual integration | Plugin architecture | CI/CD automated |
| Testing Infrastructure | Manual/limited testing | Comprehensive Jest test suite | Automated testing with mocking |
| Development Environment | Local setup complexity | Dockerized development | Consistent customer environments |
| Network Security | VPN/SDWAN security risks | Controlled API access | Eliminated broader exposure |
| Access Control | Direct database access | Limited application access | Secure, controlled scope |

**Major Achievements:**

- **GraphQL API Implementation** - Modern API operational alongside SOAP during transition
- **OAuth-like Security** - Enhanced authentication option available
- **Controlled Access** - Secure API eliminating broader database exposure risks
- **Self-Service Documentation** - GraphQL Sandbox deployed for schema exploration
- **Plugin Architecture** - Extensible system with CI/CD integration operational
- **Automated Testing** - Comprehensive Jest test suite with mocking and CI/CD integration
- **Dockerized Development** - Consistent development environments for customer teams
- **Migration Foundation** - Parallel operation enabling structured SOAP-to-GraphQL transition
- **SOAP Deprecation** - Planned sunset once GraphQL migration complete
- **Database-First Migration** - Foundation established (Phase 5 - future)

---

*This case study demonstrates enterprise-scale API modernization with focus on security, developer experience, and architectural transformation. The parallel API approach enables structured migration from SOAP to GraphQL while establishing a foundation for long-term evolution from database-first to code-first development, ultimately delivering a unified, modern integration platform.*
