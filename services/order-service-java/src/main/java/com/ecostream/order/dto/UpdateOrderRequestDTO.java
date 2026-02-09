package com.ecostream.order.dto;

import com.ecostream.order.entity.OrderStatus;
import jakarta.validation.Valid;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for updating an existing order.
 * All fields are optional to allow partial updates.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateOrderRequestDTO {

    /**
     * New status for the order (optional).
     * Allows status changes during order lifecycle.
     */
    private OrderStatus status;

    /**
     * New destination location coordinates (optional).
     * Nested LocationDTO with coordinate range validation.
     */
    @Valid
    private LocationDTO destination;

    /**
     * New priority level for the order (optional).
     */
    private Integer priority;
}
