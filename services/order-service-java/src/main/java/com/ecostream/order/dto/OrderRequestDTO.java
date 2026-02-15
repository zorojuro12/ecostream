package com.ecostream.order.dto;

import com.ecostream.order.entity.OrderStatus;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for creating a new order.
 * Contains all required fields with validation annotations.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderRequestDTO {

    /**
     * Current status of the order in the delivery lifecycle.
     */
    @NotNull(message = "Order status is required")
    private OrderStatus status;

    /**
     * Destination location coordinates.
     * Nested LocationDTO with coordinate range validation.
     */
    @NotNull(message = "Destination location is required")
    @Valid
    private LocationDTO destination;

    /**
     * Priority level of the order (higher number = higher priority).
     */
    @NotNull(message = "Priority is required")
    private Integer priority;
}
