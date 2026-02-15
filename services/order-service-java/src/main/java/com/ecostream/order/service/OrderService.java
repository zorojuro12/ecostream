package com.ecostream.order.service;

import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.dto.UpdateOrderRequestDTO;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Service interface for order management operations.
 * Defines CRUD operations using DTOs to maintain strict separation of concerns.
 */
public interface OrderService {

    /**
     * Creates a new order from the provided request DTO.
     *
     * @param request the order creation request containing status, destination, and priority
     * @return the created order as an OrderResponseDTO
     */
    OrderResponseDTO createOrder(OrderRequestDTO request);

    /**
     * Retrieves an order by its unique identifier.
     *
     * @param id the UUID of the order to retrieve
     * @return an Optional containing the OrderResponseDTO if found, empty otherwise
     */
    Optional<OrderResponseDTO> getOrderById(UUID id);

    /**
     * Retrieves all orders in the system.
     *
     * @return a list of all orders as OrderResponseDTOs
     */
    List<OrderResponseDTO> getAllOrders();

    /**
     * Updates an existing order with the provided request data.
     *
     * @param id the UUID of the order to update
     * @param request the order update request containing new values
     * @return an Optional containing the updated OrderResponseDTO if found, empty otherwise
     */
    Optional<OrderResponseDTO> updateOrder(UUID id, UpdateOrderRequestDTO request);

    /**
     * Deletes an order by its unique identifier.
     *
     * @param id the UUID of the order to delete
     * @return true if the order was deleted, false if it was not found
     */
    boolean deleteOrder(UUID id);

    /**
     * Ingests telemetry data for an order.
     * Saves the current coordinates to DynamoDB with a timestamp.
     *
     * @param orderId the UUID of the order
     * @param location the current location coordinates
     */
    void ingestTelemetry(UUID orderId, com.ecostream.order.dto.LocationDTO location);
}
