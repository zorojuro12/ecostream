package com.ecostream.order.controller;

import com.ecostream.order.dto.LocationDTO;
import com.ecostream.order.dto.OrderRequestDTO;
import com.ecostream.order.dto.OrderResponseDTO;
import com.ecostream.order.entity.OrderStatus;
import com.ecostream.order.service.OrderService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import java.util.Arrays;
import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * Unit tests for OrderController.
 * Tests follow TDD Red-Green-Refactor workflow.
 */
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createOrder_ShouldReturn201Created() throws Exception {
        // Arrange: Create request DTO
        LocationDTO locationDTO = LocationDTO.builder()
                .latitude(37.7749)
                .longitude(-122.4194)
                .build();

        OrderRequestDTO requestDTO = OrderRequestDTO.builder()
                .status(OrderStatus.CONFIRMED)
                .destination(locationDTO)
                .priority(5)
                .build();

        // Arrange: Create response DTO
        UUID orderId = UUID.randomUUID();
        OrderResponseDTO responseDTO = OrderResponseDTO.builder()
                .id(orderId)
                .status(OrderStatus.PENDING)
                .destination(locationDTO)
                .priority(5)
                .build();

        // Arrange: Mock service to return response DTO
        when(orderService.createOrder(any(OrderRequestDTO.class))).thenReturn(responseDTO);

        // Act & Assert: POST request and verify 201 Created response
        mockMvc.perform(post("/api/orders")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(requestDTO)))
                .andExpect(status().isCreated())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(orderId.toString()))
                .andExpect(jsonPath("$.status").value("PENDING"))
                .andExpect(jsonPath("$.destination.latitude").value(37.7749))
                .andExpect(jsonPath("$.destination.longitude").value(-122.4194))
                .andExpect(jsonPath("$.priority").value(5));
    }

    @Test
    void getOrderById_ShouldReturn200Ok_WhenOrderExists() throws Exception {
        // Arrange: Create order ID and response DTO
        UUID orderId = UUID.randomUUID();
        LocationDTO locationDTO = LocationDTO.builder()
                .latitude(37.7749)
                .longitude(-122.4194)
                .build();

        OrderResponseDTO responseDTO = OrderResponseDTO.builder()
                .id(orderId)
                .status(OrderStatus.PENDING)
                .destination(locationDTO)
                .priority(5)
                .build();

        // Arrange: Mock service to return Optional with response DTO
        when(orderService.getOrderById(orderId)).thenReturn(Optional.of(responseDTO));

        // Act & Assert: GET request and verify 200 OK response
        mockMvc.perform(get("/api/orders/{id}", orderId))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value(orderId.toString()))
                .andExpect(jsonPath("$.status").value("PENDING"))
                .andExpect(jsonPath("$.destination.latitude").value(37.7749))
                .andExpect(jsonPath("$.destination.longitude").value(-122.4194))
                .andExpect(jsonPath("$.priority").value(5));
    }

    @Test
    void getOrderById_ShouldReturn404NotFound_WhenOrderDoesNotExist() throws Exception {
        // Arrange: Create order ID
        UUID orderId = UUID.randomUUID();

        // Arrange: Mock service to return empty Optional
        when(orderService.getOrderById(orderId)).thenReturn(Optional.empty());

        // Act & Assert: GET request and verify 404 Not Found response
        mockMvc.perform(get("/api/orders/{id}", orderId))
                .andExpect(status().isNotFound());
    }

    @Test
    void getAllOrders_ShouldReturn200Ok_WithMultipleOrders() throws Exception {
        // Arrange: Create multiple order response DTOs
        UUID orderId1 = UUID.randomUUID();
        UUID orderId2 = UUID.randomUUID();
        
        LocationDTO location1 = LocationDTO.builder()
                .latitude(37.7749)
                .longitude(-122.4194)
                .build();
        
        LocationDTO location2 = LocationDTO.builder()
                .latitude(40.7128)
                .longitude(-74.0060)
                .build();

        OrderResponseDTO responseDTO1 = OrderResponseDTO.builder()
                .id(orderId1)
                .status(OrderStatus.PENDING)
                .destination(location1)
                .priority(5)
                .build();

        OrderResponseDTO responseDTO2 = OrderResponseDTO.builder()
                .id(orderId2)
                .status(OrderStatus.CONFIRMED)
                .destination(location2)
                .priority(3)
                .build();

        List<OrderResponseDTO> allOrders = Arrays.asList(responseDTO1, responseDTO2);

        // Arrange: Mock service to return list of orders
        when(orderService.getAllOrders()).thenReturn(allOrders);

        // Act & Assert: GET request and verify 200 OK response with multiple orders
        mockMvc.perform(get("/api/orders"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].id").value(orderId1.toString()))
                .andExpect(jsonPath("$[0].status").value("PENDING"))
                .andExpect(jsonPath("$[0].priority").value(5))
                .andExpect(jsonPath("$[1].id").value(orderId2.toString()))
                .andExpect(jsonPath("$[1].status").value("CONFIRMED"))
                .andExpect(jsonPath("$[1].priority").value(3));
    }
}
