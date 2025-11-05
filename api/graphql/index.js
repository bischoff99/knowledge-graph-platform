import { ApolloServer } from 'apollo-server';
import { Neo4jGraphQL } from '@neo4j/graphql';
import neo4j from 'neo4j-driver';
import dotenv from 'dotenv';

dotenv.config();

const typeDefs = `#graphql
  type Project {
    id: ID!
    name: String!
    status: String
    criticality: String
    tags: [String]
    last_verified: DateTime
    location: String
    test_pass_rate: Float
    
    dependencies: [Tool!]! @relationship(type: "DEPENDS_ON_CRITICAL", direction: OUT)
    optimizations: [Configuration!]! @relationship(type: "OPTIMIZED_WITH", direction: OUT)
    tools: [Tool!]! @relationship(type: "EXPOSES", direction: OUT)
    patterns: [Pattern!]! @relationship(type: "IMPLEMENTS_PATTERN", direction: OUT)
  }
  
  type Tool {
    id: ID!
    name: String!
    status: String
    criticality: String
    tags: [String]
    description: String
    
    dependentProjects: [Project!]! @relationship(type: "DEPENDS_ON_CRITICAL", direction: IN)
  }
  
  type Configuration {
    id: ID!
    name: String!
    status: String
    tags: [String]
    cpu_cores: Int
    ram_gb: Int
    gpu_cores: Int
  }
  
  type Pattern {
    id: ID!
    name: String!
    status: String
    tags: [String]
    formula: String
    proven_speedup: String
    applies_to: String
    
    implementations: [Project!]! @relationship(type: "IMPLEMENTS_PATTERN", direction: IN)
  }
  
  type Documentation {
    id: ID!
    name: String!
    tags: [String]
    content: String
    keywords: String
  }
  
  type Query {
    projectsByStatus(status: String!): [Project!]!
      @cypher(statement: """
        MATCH (p:Project {status: $status})
        RETURN p
      """)
    
    criticalInfrastructure: [Tool!]!
      @cypher(statement: """
        MATCH (t:Tool)
        WHERE t.criticality = 'critical'
        RETURN t
      """)
    
    patternsByTag(tag: String!): [Pattern!]!
      @cypher(statement: """
        MATCH (p:Pattern)
        WHERE $tag IN p.tags
        RETURN p
      """)
    
    projectDependencyGraph(projectId: ID!): [Project!]!
      @cypher(statement: """
        MATCH path = (p:Project {id: $projectId})-[:DEPENDS_ON_CRITICAL*1..3]->()
        UNWIND nodes(path) AS node
        RETURN DISTINCT node
      """)
  }
`;

const driver = neo4j.driver(
  process.env.NEO4J_URI || 'bolt://localhost:7687',
  neo4j.auth.basic(
    process.env.NEO4J_USER || 'neo4j',
    process.env.NEO4J_PASSWORD || 'test1234'
  )
);

const neoSchema = new Neo4jGraphQL({ typeDefs, driver });

const server = new ApolloServer({
  schema: await neoSchema.getSchema(),
  context: ({ req }) => ({ req }),
});

const { url } = await server.listen(process.env.GRAPHQL_PORT || 4000);
console.log(`🚀 GraphQL server ready at ${url}`);
console.log(`🔗 Connected to Neo4j at ${process.env.NEO4J_URI || 'bolt://localhost:7687'}`);
