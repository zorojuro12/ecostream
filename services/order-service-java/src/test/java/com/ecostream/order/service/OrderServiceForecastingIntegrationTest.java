package com.ecostream.order.service;

import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.entity.Order;
import com.ecostream.order.entity.OrderStatus;
import com.ecostream.order.repository.OrderRepository;
import com.ecostream.order.repository.TelemetryRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Integration test: getOrderById enriches response with ETA from AI Forecasting Service.
 * Uses mocked ForecastingClient so the test does not depend on Python service being up.
 */
@ExtendWith(MockitoExtension.class)
class OrderServiceForecastingIntegrationTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private TelemetryRepository telemetryRepository;

    @Mock
    private com.ecostream.order.client.ForecastingClient forecastingClient;

    @InjectMocks
    private OrderServiceImpl orderService;

    @Test
    void getOrderById_ShouldIncludeEstimatedArrivalMinutesFromAIService() {
        UUID orderId = UUID.randomUUID();
        Order order = Order.builder()
                .id(orderId)
                .status(OrderStatus.PENDING)
                .destinationLatitude(37.7749)
                .destinationLongitude(-122.4194)
                .priority(5)
                .build();

        when(orderRepository.findById(orderId)).thenReturn(Optional.of(order));

        com.ecostream.order.client.ForecastResponseDTO mockForecast =
                new com.ecostream.order.client.ForecastResponseDTO(13.72, 25.5);
        when(forecastingClient.getForecast(
                eq(orderId),
                eq(37.7749),
                eq(-122.4194),
                any(String.class)))
                .thenReturn(mockForecast);

        Optional<OrderResponseDTO> result = orderService.getOrderById(orderId);

        assertTrue(result.isPresent(), "Order should be present");
        assertEquals(25.5, result.get().getEstimatedArrivalMinutes(),
                "Response should include ETA from AI service");
        assertEquals(13.72, result.get().getDistanceKm(),
                "Response should include distance_km from AI service");
    }

    @Test
    void getOrderById_WhenAIServiceFails_ShouldReturnOrderWithNullEta() {
        UUID orderId = UUID.randomUUID();
        Order order = Order.builder()
                .id(orderId)
                .status(OrderStatus.PENDING)
                .destinationLatitude(37.7749)
                .destinationLongitude(-122.4194)
                .priority(5)
                .build();

        when(orderRepository.findById(orderId)).thenReturn(Optional.of(order));
        when(forecastingClient.getForecast(eq(orderId), eq(37.7749), eq(-122.4194), any(String.class)))
                .thenThrow(new RuntimeException("Connection refused"));

        Optional<OrderResponseDTO> result = orderService.getOrderById(orderId);

        assertTrue(result.isPresent(), "Order should still be present");
        assertNull(result.get().getEstimatedArrivalMinutes(), "ETA should be null when AI fails");
        assertNull(result.get().getDistanceKm(), "Distance should be null when AI fails");
        assertEquals(orderId, result.get().getId(), "Core order data should be unchanged");
        verify(forecastingClient).getForecast(eq(orderId), eq(37.7749), eq(-122.4194), any(String.class));
    }
}
