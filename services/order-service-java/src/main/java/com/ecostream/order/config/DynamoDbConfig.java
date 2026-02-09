package com.ecostream.order.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

import java.net.URI;

/**
 * Configuration for DynamoDB Enhanced Client.
 * Overrides endpoint to http://localhost:9000 for local development.
 */
@Configuration
public class DynamoDbConfig {

    @Value("${aws.dynamodb.endpoint:http://localhost:9000}")
    private String dynamoDbEndpoint;

    /**
     * Creates a DynamoDB client configured for local development.
     * Overrides endpoint to http://localhost:9000 as required.
     *
     * @return configured DynamoDbClient
     */
    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
                .endpointOverride(URI.create(dynamoDbEndpoint))
                .region(Region.US_EAST_1)
                .credentialsProvider(DefaultCredentialsProvider.create())
                .build();
    }

    /**
     * Creates a DynamoDB Enhanced Client for simplified operations.
     *
     * @param dynamoDbClient the base DynamoDB client
     * @return configured DynamoDbEnhancedClient
     */
    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
        return DynamoDbEnhancedClient.builder()
                .dynamoDbClient(dynamoDbClient)
                .build();
    }
}
