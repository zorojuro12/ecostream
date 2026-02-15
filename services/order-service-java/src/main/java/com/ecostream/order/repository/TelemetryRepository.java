package com.ecostream.order.repository;

import com.ecostream.order.entity.Telemetry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Repository;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.model.PutItemEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryEnhancedRequest;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Repository for Telemetry entity operations in DynamoDB.
 * Uses AWS SDK v2 Enhanced Client for simplified DynamoDB operations.
 */
@Repository
@RequiredArgsConstructor
@Slf4j
public class TelemetryRepository {

    private static final String TABLE_NAME = "ecostream-telemetry-local";
    private final DynamoDbEnhancedClient dynamoDbEnhancedClient;

    /**
     * Gets the DynamoDB table for telemetry data.
     *
     * @return DynamoDbTable instance for Telemetry
     */
    private DynamoDbTable<Telemetry> getTable() {
        return dynamoDbEnhancedClient.table(TABLE_NAME, TableSchema.fromBean(Telemetry.class));
    }

    /**
     * Saves a telemetry record to DynamoDB.
     *
     * @param telemetry the telemetry data to save
     * @return the saved telemetry record
     */
    public Telemetry save(Telemetry telemetry) {
        log.debug("Saving telemetry for orderId: {}, timestamp: {}", telemetry.getOrderId(), telemetry.getTimestamp());
        
        DynamoDbTable<Telemetry> table = getTable();
        table.putItem(telemetry);
        
        log.debug("Telemetry saved successfully");
        return telemetry;
    }

    /**
     * Retrieves all telemetry records for a specific order.
     *
     * @param orderId the order ID to query
     * @return list of telemetry records for the order
     */
    public List<Telemetry> findByOrderId(String orderId) {
        log.debug("Querying telemetry for orderId: {}", orderId);
        
        DynamoDbTable<Telemetry> table = getTable();
        Key key = Key.builder()
                .partitionValue(orderId)
                .build();
        
        QueryConditional queryConditional = QueryConditional.keyEqualTo(key);
        QueryEnhancedRequest queryRequest = QueryEnhancedRequest.builder()
                .queryConditional(queryConditional)
                .build();
        
        List<Telemetry> results = table.query(queryRequest)
                .items()
                .stream()
                .collect(Collectors.toList());
        
        log.debug("Found {} telemetry records for orderId: {}", results.size(), orderId);
        return results;
    }

    /**
     * Retrieves a specific telemetry record by orderId and timestamp.
     *
     * @param orderId the order ID
     * @param timestamp the timestamp (epoch seconds)
     * @return the telemetry record if found, null otherwise
     */
    public Telemetry findByOrderIdAndTimestamp(String orderId, Long timestamp) {
        log.debug("Retrieving telemetry for orderId: {}, timestamp: {}", orderId, timestamp);
        
        DynamoDbTable<Telemetry> table = getTable();
        Key key = Key.builder()
                .partitionValue(orderId)
                .sortValue(timestamp)
                .build();
        
        Telemetry result = table.getItem(key);
        
        if (result != null) {
            log.debug("Telemetry record found");
        } else {
            log.debug("Telemetry record not found");
        }
        
        return result;
    }
}
