package com.ecostream.order.service;

import com.ecostream.order.client.ForecastResponseDTO;
import com.ecostream.order.client.ForecastingClient;
import com.ecostream.order.dto.LocationDTO;
import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.dto.TelemetryRequestDTO;
import com.ecostream.order.dto.UpdateOrderRequestDTO;
import com.ecostream.order.entity.Order;
import com.ecostream.order.entity.OrderStatus;
import com.ecostream.order.entity.Telemetry;
import com.ecostream.order.repository.OrderRepository;
import com.ecostream.order.repository.TelemetryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Implementation of OrderService interface.
 * Provides business logic for order management operations.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderServiceImpl implements OrderService {

    private final OrderRepository orderRepository;
    private final TelemetryRepository telemetryRepository;
    private final ForecastingClient forecastingClient;

    /**
     * Creates a new order from the provided request DTO.
     * Sets the order status to PENDING regardless of the status in the request.
     *
     * @param request the order creation request containing status, destination, and priority
     * @return the created order as an OrderResponseDTO
     */
    @Override
    public OrderResponseDTO createOrder(OrderRequestDTO request) {
        log.debug("Creating new order with priority: {}", request.getPriority());

        // Map DTO to Entity, setting status to PENDING
        Order order = Order.builder()
                .status(OrderStatus.PENDING) // Always set to PENDING for new orders
                .destinationLatitude(request.getDestination().getLatitude())
                .destinationLongitude(request.getDestination().getLongitude())
                .priority(request.getPriority())
                .build();

        // Save order to database
        Order savedOrder = orderRepository.save(order);
        log.info("Order created successfully with ID: {}", savedOrder.getId());

        // Map Entity to Response DTO
        return mapToResponseDTO(savedOrder);
    }

    @Override
    public Optional<OrderResponseDTO> getOrderById(UUID id) {
        log.debug("Retrieving order with ID: {}", id);

        Optional<Order> orderOptional = orderRepository.findById(id);

        if (orderOptional.isEmpty()) {
            log.debug("Order not found with ID: {}", id);
            return Optional.empty();
        }

        Order order = orderOptional.get();
        OrderResponseDTO dto = mapToResponseDTO(order);

        try {
            String priorityForAi = order.getPriority() != null && order.getPriority() >= 5 ? "Express" : "Standard";
            ForecastResponseDTO forecast = forecastingClient.getForecast(
                    id,
                    order.getDestinationLatitude(),
                    order.getDestinationLongitude(),
                    priorityForAi);
            if (forecast != null) {
                dto.setDistanceKm(forecast.distanceKm());
                dto.setEstimatedArrivalMinutes(forecast.estimatedArrivalMinutes());
            }
        } catch (Exception e) {
            log.warn("AI forecasting unavailable for order {}: {}", id, e.getMessage());
            // Leave ETA and distanceKm null so core order data is still returned
        }

        log.info("Order retrieved successfully with ID: {}", id);
        return Optional.of(dto);
    }

    @Override
    public List<OrderResponseDTO> getAllOrders() {
        log.debug("Retrieving all orders");
        
        List<Order> orders = orderRepository.findAll();
        log.info("Retrieved {} orders", orders.size());
        
        return orders.stream()
                .map(this::mapToResponseDTO)
                .toList();
    }

    @Override
    public Optional<OrderResponseDTO> updateOrder(UUID id, UpdateOrderRequestDTO request) {
        log.debug("Updating order with ID: {}", id);
        
        Optional<Order> orderOptional = orderRepository.findById(id);
        
        if (orderOptional.isEmpty()) {
            log.debug("Order not found with ID: {}", id);
            return Optional.empty();
        }
        
        Order order = orderOptional.get();
        
        // Update fields if provided in request
        if (request.getStatus() != null) {
            order.setStatus(request.getStatus());
            log.debug("Updated status to: {}", request.getStatus());
        }
        
        if (request.getDestination() != null) {
            order.setDestinationLatitude(request.getDestination().getLatitude());
            order.setDestinationLongitude(request.getDestination().getLongitude());
            log.debug("Updated destination coordinates");
        }
        
        if (request.getPriority() != null) {
            order.setPriority(request.getPriority());
            log.debug("Updated priority to: {}", request.getPriority());
        }
        
        // Save updated order
        Order updatedOrder = orderRepository.save(order);
        log.info("Order updated successfully with ID: {}", id);
        
        return Optional.of(mapToResponseDTO(updatedOrder));
    }

    @Override
    public boolean deleteOrder(UUID id) {
        log.debug("Deleting order with ID: {}", id);
        
        if (!orderRepository.existsById(id)) {
            log.debug("Order not found with ID: {}", id);
            return false;
        }
        
        orderRepository.deleteById(id);
        log.info("Order deleted successfully with ID: {}", id);
        return true;
    }

    @Override
    public void ingestTelemetry(UUID orderId, TelemetryRequestDTO request) {
        log.debug("Ingesting telemetry for orderId: {}", orderId);
        
        // Get current timestamp in epoch seconds
        long timestamp = java.time.Instant.now().getEpochSecond();
        
        // Create telemetry entity
        Telemetry telemetry = Telemetry.builder()
                .orderId(orderId.toString())
                .timestamp(timestamp)
                .currentLatitude(request.getCurrentLatitude())
                .currentLongitude(request.getCurrentLongitude())
                .build();
        
        // Save to DynamoDB
        telemetryRepository.save(telemetry);
        
        // Real-time monitoring: Log ingestion details to console
        log.info("Telemetry ingested successfully for orderId: {}, timestamp: {}", orderId, timestamp);
        System.out.println(String.format("[TELEMETRY] orderId=%s, timestamp=%d", orderId, timestamp));
    }

    /**
     * Maps an Order entity to an OrderResponseDTO.
     *
     * @param order the Order entity to map
     * @return the mapped OrderResponseDTO
     */
    private OrderResponseDTO mapToResponseDTO(Order order) {
        LocationDTO locationDTO = LocationDTO.builder()
                .latitude(order.getDestinationLatitude())
                .longitude(order.getDestinationLongitude())
                .build();

        return OrderResponseDTO.builder()
                .id(order.getId())
                .status(order.getStatus())
                .destination(locationDTO)
                .priority(order.getPriority())
                .distanceKm(null)
                .estimatedArrivalMinutes(null)
                .build();
    }
}
