package com.ecostream.order.dto;

import com.ecostream.order.entity.OrderStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * Data Transfer Object for order responses.
 * Prevents entity exposure and maintains strict API contract boundaries.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderResponseDTO {

    /**
     * Unique identifier for the order.
     */
    private UUID id;

    /**
     * Current status of the order in the delivery lifecycle.
     */
    private OrderStatus status;

    /**
     * Destination location coordinates.
     * Nested LocationDTO matching the request structure.
     */
    private LocationDTO destination;

    /**
     * Priority level of the order (higher number = higher priority).
     */
    private Integer priority;
}
