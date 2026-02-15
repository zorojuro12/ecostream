package com.ecostream.order.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Health check controller for the Order Service.
 * Provides endpoint to verify service availability and status.
 */
@RestController
public class HealthController {

    /**
     * Health check endpoint to verify service is running.
     * Returns service status and name for monitoring and integration testing.
     *
     * @return Map containing status and service name
     */
    @GetMapping("/health")
    public Map<String, String> healthCheck() {
        return Map.of("status", "UP", "service", "order-service");
    }
}
