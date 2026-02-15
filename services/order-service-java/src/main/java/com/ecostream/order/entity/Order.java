package com.ecostream.order.entity;

import jakarta.persistence.*;
import lombok.*;
import java.util.UUID;

/**
 * Order entity representing a delivery order in the EcoStream system.
 * Stores order details including destination coordinates and priority level.
 */
@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Order {

    /**
     * Unique identifier for the order.
     * Generated automatically if not provided.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    /**
     * Current status of the order in the delivery lifecycle.
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private OrderStatus status;

    /**
     * Latitude coordinate of the delivery destination.
     */
    @Column(name = "destination_latitude", nullable = false)
    private Double destinationLatitude;

    /**
     * Longitude coordinate of the delivery destination.
     */
    @Column(name = "destination_longitude", nullable = false)
    private Double destinationLongitude;

    /**
     * Priority level of the order (higher number = higher priority).
     */
    @Column(name = "priority", nullable = false)
    private Integer priority;
}
