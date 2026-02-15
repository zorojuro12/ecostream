package com.ecostream.order.entity;

/**
 * Order status enumeration.
 * Represents the current state of an order in the delivery lifecycle.
 */
public enum OrderStatus {
    PENDING,
    CONFIRMED,
    IN_TRANSIT,
    DELIVERED,
    CANCELLED
}
