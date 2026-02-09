package com.ecostream.order.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;

import java.time.Instant;

/**
 * Telemetry entity representing real-time tracking data for orders.
 * Stored in DynamoDB with orderId as partition key and timestamp as sort key.
 */
@DynamoDbBean
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Telemetry {

    /**
     * Order ID (Partition Key).
     * Links telemetry data to a specific order.
     */
    private String orderId;

    /**
     * Timestamp in epoch seconds (Sort Key).
     * Allows querying telemetry data by time range for a specific order.
     */
    private Long timestamp;

    /**
     * Current latitude coordinate of the order.
     */
    private Double currentLatitude;

    /**
     * Current longitude coordinate of the order.
     */
    private Double currentLongitude;

    @DynamoDbPartitionKey
    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    @DynamoDbSortKey
    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }
}
